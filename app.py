import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from pathlib import Path
import datetime
import duckdb

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ProtonDB Reports Game Analytics",
    page_icon="🎮",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Data Loading & Processing
# -----------------------------------------------------------------------------
# from pipeline.settings import DEBUG, MODE, DUCKDB, BIGQUERY, START_DATE
# from pipeline.settings import DUCKDB_CONNECTION
DEBUG = True # False
SAMPLE = 'sample' # export samples to .csv 
PARQUET = 'parquet' # export to .parquet files
DUCKDB = 'duckdb' # export to DuckDB
BIGQUERY = 'bigquery' # export to BigQuery

MODE = os.environ.get('DATAWAREHOUSE', DUCKDB) # DUCKDB BIGQUERY SAMPLE
DUCKDB_CONNECTION = './data/duckdb.db'
DATA_DIR = f'./data/'  # ! with '/' at the end!
TARGET_FILE_NAME = 'reports_piiremoved.json'

def duckdb_connect(connection=""):
    if connection == "":
        if DUCKDB_CONNECTION:
            connection = DUCKDB_CONNECTION
        else:
            print("DUCKDB_CONNECTION environment variable is not defined.\n")
            return None, []

    if not connection.startswith("md:") and not os.path.exists(connection):
        print(f'The file "{connection}" does not exist. Creating.\n')
    elif connection.startswith("md:") and not os.environ.get("motherduck_token", ""):
        print(f'!! Error connecting to MotherDuck "{connection}": motherduck_token not defined. Check .env file.')
        return None, []

    if DEBUG:
        print(f'\nDuckDb connection: "{connection}"')

    try:
        con = duckdb.connect(connection, read_only=False)
        df = con.sql(f"SELECT * FROM duckdb_tables()").df()
        tables = df["table_name"].to_list()
        return con, tables
    except Exception as e:
        print(f'!! Error connecting to duckdb "{connection}":\n {e}')
        return None, []


def db_get_reports_records(con, table_name, start_date=None, end_date=None):
    condition = ""
    if start_date and end_date:
        condition = f"WHERE strftime(timestamp, '%Y-%m-%d') <= '{end_date}'  \
                    AND strftime(timestamp, '%Y-%m-%d') >= '{start_date}'"
    query = f"SELECT app_steam_appid,app_title,timestamp, \
                systeminfo_cpu,systeminfo_gpu,systeminfo_gpudriver,systeminfo_kernel,systeminfo_os,systeminfo_ram, \
                responses_verdict,responses_installs \
                FROM  {table_name} \
                {condition} \
                ORDER BY timestamp ASC;" # date_part('year', date)
                # ,responses_opens,responses_startsplay,responses_significantbugs 
    res = con.sql(query)
    df = res.df()
    if DEBUG:
        print(" Total records:", df.shape[0])
    return df

class DbConnector:
    def __init__(self, mode=MODE):
        self.mode = mode
        if self.mode == DUCKDB:
            con, tables = duckdb_connect()
            self.con = con
        # elif self.mode == BIGQUERY:
        #     bq_client, dataset = bigquery_connect()
        #     self.bq_client = bq_client

    def get_reports_records(self, table_name, start_date=None, end_date=None):
        if self.mode == DUCKDB:
            return db_get_reports_records(self.con, table_name, start_date, end_date)
        # elif self.mode == BIGQUERY:
        #     return biqquery_get_reports_records(self.bq_client, table_name, start_date, end_date)


connection = DbConnector(MODE)


# --- OS name/version cleaning ---
# Function to clean OS names
# Turn "Ubuntu 18.04.3 LTS", "Ubuntu 19.10", or "Linux Mint 21.1", "Linux Mint 22.3" etc into "Ubuntu", "Linux Mint" etc
def clean_os_name(os_string):
    if pd.isna(os_string):
        return "Unknown OS"
    
    # Take the first two words
    parts = os_string.split()
    base_name = " ".join(parts[:2])
    
    # # Remove numbers and punctuation
    # cleaned_name = re.sub(r'[\d\W_]+', '', base_name)
    
    # Remove first non letter/space and everything after
    cleaned_name = re.sub(r'[^a-zA-Z\s\!_].*', '', base_name).strip()

    # Remove any character NOT in the range 00-7F (ASCII)
    cleaned_name = re.sub(r'[^\x00-\x7F]+', '', cleaned_name)

    # Remove 'release'
    cleaned_name = re.sub(r'release$', '', cleaned_name).strip()
    
    # Return a default if the result is empty after cleaning
    return cleaned_name if cleaned_name else "Unknown OS"

@st.cache_data
def load_data(data_file):
    try:
        if connection.con:
            df = connection.get_reports_records(table_name="ingest.protondb")
        else:
            df = pd.read_csv(data_file)
        
        # Ensure timestamp is datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
        # print(df.head(2))
        
        # Drop rows with invalid timestamps to prevent chart errors
        df = df.dropna(subset=['timestamp'])
        
        # Clean OS name
        df['os_group'] = df['systeminfo_os'].apply(clean_os_name)

        # Create a Monthly Period column for aggregation
        # used to_timestamp() at the end so Plotly treats it as a date axis
        df['month'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()
        df['year'] = df['timestamp'].dt.year
        
        # Ensure responses_verdict is treated as categorical for better plotting
        df['responses_verdict'] = df['responses_verdict'].astype(str)
        
        return df
    except FileNotFoundError:
        st.error(f"File not found: {data_file}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# -----------------------------------------------------------------------------
# 3. Main Application
# -----------------------------------------------------------------------------
def main():
    st.title("🎮 ProtonDB Reports Game Analytics")
    
    data_file = DATA_DIR + f"{TARGET_FILE_NAME}.csv"

    df = load_data(data_file)

    if not df.empty:
        # --- Sidebar Filters ---
        st.sidebar.header("Global Filters")
        
        # Date Range Filter
        min_date = df['timestamp'].min().date() + datetime.timedelta(days=1)
        max_date = df['timestamp'].max().date() + datetime.timedelta(days=-1)
        date_range = st.sidebar.date_input(
            "Select Date Range", 
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

        # Filter DataFrame by selected date range
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
        else:
            filtered_df = df

        # OS Filter (applied after date filtering)
        # available_os = sorted(filtered_df['os_group'].unique())
        available_os = filtered_df['os_group'].unique()
        selected_os = st.sidebar.multiselect("Filter by OS", available_os, default=available_os)
        
        # Apply OS filter
        filtered_df = filtered_df[filtered_df['os_group'].isin(selected_os)]

        # -------------------------------------------------------------------------
        # DASHBOARD 1: Monthly OS Trends (Top 10)
        # -------------------------------------------------------------------------
        st.header("1. Top 10 OS Monthly Trends")
        # st.info("Showing trends for the Top 10 most frequent OS families over the selected period.")
        
        if not filtered_df.empty:
            # Group by month and OS
            os_monthly_counts = filtered_df.groupby(['month', 'os_group']).size().reset_index(name='report_count')

            # Get Top 10 OS groups by total count in filtered period
            top_os_groups = os_monthly_counts.groupby('os_group')['report_count'].sum().nlargest(10).index.tolist()

            # Filter for Top 10 only
            top_os_monthly = os_monthly_counts[os_monthly_counts['os_group'].isin(top_os_groups)]

            fig_os = px.line(
                top_os_monthly, 
                x='month', 
                y='report_count', 
                color='os_group',
                markers=True,
                line_shape='linear',
                title="Top 10 OS Families: Volume of Reports per Month",
                labels={'month': 'Month', 'report_count': 'Total Reports', 'os_group': 'OS Family'}
            )
            
            fig_os.update_xaxes(dtick="M1", tickformat="%b %Y")
            fig_os.update_layout(hovermode="x unified", legend_title_text='OS Family')
            
            st.plotly_chart(fig_os, width='stretch') # , use_container_width=True) deprecated
        else:
            st.warning("No data available for selected filters.")

        # -------------------------------------------------------------------------
        # DASHBOARD 2: Top 10 Hardware Combinations
        # -------------------------------------------------------------------------
        st.divider()
        st.header("2. Top 10 Hardware Configurations")
        
        if not filtered_df.empty:
            hw_counts = filtered_df.groupby(
                ['systeminfo_cpu', 'systeminfo_gpu', 'systeminfo_ram']
            ).size().reset_index(name='count')

            top_10_hw = hw_counts.nlargest(10, 'count')

            top_10_hw['label'] = (
                top_10_hw['systeminfo_cpu'].str.split().str[:6].str.join(" ") + " | " + 
                top_10_hw['systeminfo_gpu'].str.split().str[:7].str.join(" ") + " | " + 
                top_10_hw['systeminfo_ram']
            )

            fig_hw = px.bar(
                top_10_hw, 
                x='count', 
                y='label', 
                orientation='h',
                text='count',
                color='count',
                color_continuous_scale='Viridis',
                title="Most Frequent Hardware Setup (CPU | GPU | RAM)",
                labels={'count': 'Reports', 'label': 'Configuration'}
            )
            
            fig_hw.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig_hw, width='stretch') # , use_container_width=True) deprecated
        else:
            st.warning("No data available for selected filters.")

        # -------------------------------------------------------------------------
        # DASHBOARD 3: Reports by Year and Working Status
        # -------------------------------------------------------------------------
        st.divider()
        st.header("3. Reports Status (Working/Non-Working) by Year")
        
        if not filtered_df.empty:
            # Group by Year and responses_verdict
            year_status_counts = filtered_df.groupby(['year', 'responses_verdict']).size().reset_index(name='count')
            
            # Map 0/1 to clearer labels
            year_status_counts['status'] = year_status_counts['responses_verdict'].map({'0': 'Not Working', '1': 'Working'})
            
            fig_year_status = px.bar(
                year_status_counts,
                x='year',
                y='count',
                color='status',
                barmode='group', # or 'stack' if you prefer stacked bars
                title="Total Reports per Year: Working vs Not Working",
                color_discrete_map={'Working': '#2ecc71', 'Not Working': '#e74c3c'},
                labels={'count': 'Number of Reports', 'year': 'Year', 'status': 'Game Status'}
            )
            
            fig_year_status.update_layout(legend_title_text='Response Status')
            st.plotly_chart(fig_year_status, width='stretch') # , use_container_width=True) deprecated
            
            # # Optional: Show data table
            # with st.expander("View Data Table"):
            #     st.dataframe(year_status_counts)
        else:
            st.warning("No data available for selected filters.")

        # -------------------------------------------------------------------------
        # DASHBOARD 4: Top 10 Games by Working Reports
        # -------------------------------------------------------------------------
        st.divider()
        st.header("4. Top 10 Games with Most Working Reports")
        
        if not filtered_df.empty:
            # Filter only for working reports (responses_verdict == 1)
            working_reports = filtered_df[filtered_df['responses_verdict'] == '1']
            
            game_working_counts = working_reports.groupby('app_title').size().reset_index(name='working_count')
            
            # Get Top 10
            top_10_games = game_working_counts.nlargest(10, 'working_count')
            
            fig_games = px.bar(
                top_10_games,
                x='working_count',
                y='app_title',
                orientation='h',
                text='working_count',
                color='working_count',
                color_continuous_scale='greens',
                title="Games with Highest Number of 'Working' Reports",
                labels={'working_count': 'Working Reports', 'app_title': 'Game Title'}
            )
            
            fig_games.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig_games, width='stretch') # , use_container_width=True) deprecated
        else:
            st.warning("No data available for selected filters.")

        # -------------------------------------------------------------------------
        # DASHBOARD 5: Top 10 Games by Not Working Reports
        # -------------------------------------------------------------------------
        st.divider()
        st.header("5. Top 10 Games with Most Not Working Reports")
        
        if not filtered_df.empty:
            # Filter only for working reports (responses_verdict == 1)
            working_reports = filtered_df[filtered_df['responses_verdict'] == '0']
            
            game_working_counts = working_reports.groupby('app_title').size().reset_index(name='working_count')
            
            # Get Top 10
            top_10_games = game_working_counts.nlargest(10, 'working_count')
            
            fig_games = px.bar(
                top_10_games,
                x='working_count',
                y='app_title',
                orientation='h',
                text='working_count',
                color='working_count',
                color_continuous_scale='reds',
                title="Games with Highest Number of 'Not Working' Reports",
                labels={'working_count': 'Not Working Reports', 'app_title': 'Game Title'}
            )
            
            fig_games.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig_games, width='stretch') # , use_container_width=True) deprecated
        else:
            st.warning("No data available for selected filters.")

    else:
        st.warning(f"Please ensure '{data_file}' exists and contains valid data.")

if __name__ == "__main__":
    main()
