"""@bruin
name: ingest.protondb
type: python
image: python:3.12
connection: duckdb-default
description: |
    Ingests ProtonDB data from github repo json file using Python requests library.

depends:
  - ingest.download
  - ingest.games

materialization:
    type: table
    strategy: delete+insert # replace

@bruin"""

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import json


from .settings import DATA_DIR, VISUALS_DIR, START_YEAR, START_DATE, DEBUG
from .settings import MODE, SAMPLE, PARQUET, DUCKDB, BIGQUERY, CHUNKSIZE, SAMPLE_SIZE
from .settings import SELECTED_COLS, CATEGORICAL_COLS
# from settings import games_sets, SELECTED_GAMES
from .settings import TARGET_FILE_NAME
# from .utils import flatten_record # , get_dataset_file
# DATA_DIR = f'/app/test/proj-data/'  # ! with '/' at the end!
# Github dataset info: Data exports from ProtonDB.com released under ODbL https://github.com/bdefore/protondb-data

if DEBUG:
    import tracemalloc
    # Start tracing memory allocations
    tracemalloc.start()


def memory_check(i=''):
    # Take a snapshot of the current and peak memory usage
    current_mem, peak_mem = tracemalloc.get_traced_memory()

    print(f"--{i}-- Current memory usage: {current_mem / (1024 * 1024):.2f} MiB", f"Peak memory usage: {peak_mem / (1024 * 1024):.2f} MiB")

if DEBUG:
    memory_check("Ingestion start")

def flatten_record(obj, parent_key="", sep="_"):
    """
    Flatten a nested JSON-like object (dicts and lists).
    - dict keys are appended with sep (default '.')
    - lists are expanded with index in square brackets e.g. 'list[0]'
    Returns a flat dict mapping flattened keys to values.
    """
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_record(v, new_key, sep=sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}[{i}]"
            items.update(flatten_record(v, new_key, sep=sep))
    else:
        items[parent_key] = obj
    return items


def df_transform1(df, cols):
    # yes/no cols to 1/0
    for col in cols:
        df.loc[df[col] == 'no', col] = 0
        df.loc[df[col] == 'yes', col] = 1
        df.loc[df[col].isnull(), col] = 2 # coding empty values
        df[col] = df[col].astype(int)
    return df

def df_transform2(df):
    # AppID to int
    col_id = 'app_steam_appId'
    df[col_id] = df[col_id].astype(int)

    # type check
    # find the rows where the value is NOT a valid number
    non_numeric_mask = pd.to_numeric(df[col_id], errors='coerce').isna()
    strings_only = df[non_numeric_mask]
    if len(strings_only):
        print(f'\n\n!!! AppID Errors: {len(strings_only)}\n{strings_only}\n\n')
        return df[~non_numeric_mask]
    else:
        return df

def normalize_df_columns(df):
    # normalizing column names - lowercase, no spaces
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df


def extract_json_reports(file_name):
    import ijson

    data_file = DATA_DIR + file_name
    skip_records = 0 # 348683 - SAMPLE_SIZE
    print(f'Processing {file_name}')
    chunksize = SAMPLE_SIZE
    # f = urlopen('http://.../')
    with open(data_file, "r") as f:
        objects = ijson.items(f, 'item')
        export_list = []
        data = []
        i = 0
        min_record = {}
        max_record = {}
        fullest_record = {}
        min_keys = 0
        max_keys = 0
        for record in objects:
            # print('\n', i, record)
            flat_record = flatten_record(record)
            fullest_record.update(flat_record)
            keys = flat_record.keys()
            len_keys = len(keys)
            if i == 0:
                min_keys = len_keys
                max_keys = len_keys
                print(f'\nFirst record: {datetime.fromtimestamp(flat_record["timestamp"])}\n{flat_record}')
            else:
                if min_keys > len_keys:
                    min_keys = len_keys
                    min_record = keys
                if max_keys < len_keys:
                    max_keys = len_keys
                    max_record = keys
            # print(f' --> {i}, {len_keys}, [ {min_keys}, {max_keys} ]') #, keys) #, flat_record)

            # if i>=1_000_000:
            # if i>=SAMPLE_SIZE:
            if i < skip_records:
                # break
                pass
            else:
                data.append(flat_record)

            if i % CHUNKSIZE == 0: 
                # ping
                if DEBUG:
                    memory_check(i)
                print(f' --> {i}, {datetime.fromtimestamp(flat_record["timestamp"])}, {len_keys}, [ {min_keys}, {max_keys} / {len(fullest_record.keys())} ]') #, keys) #, flat_record)
            i += 1

        print(f"\n---\ntotal: {i}")
        print(f' --> [ {min_keys}, {max_keys} ]\n{min_record=}\n{max_record=}')
        print(f'\nLatest record: {datetime.fromtimestamp(flat_record["timestamp"])}\n{flat_record}')

        try:
            df0 = pd.DataFrame(data)
        except Exception as e:
            print('!!! Failed to combine df0:', e)
            memory_check("df not combined")
            exit(1)

        if DEBUG:
            memory_check("df combined")

        df_columns = list(df0.columns)
        selected_cols = [col for col in SELECTED_COLS if col in df_columns]
        categorical_cols = [col for col in CATEGORICAL_COLS if col in df_columns]

        # transformation 1: 'yes'/'no' to 1/0
        df1 = df_transform1(df0, categorical_cols)

        # transformation 2: AppID type
        df2 = df_transform2(df1)

        # df[selected_cols].to_csv(f'{data_file}-sample-{SAMPLE_SIZE}.csv', encoding='utf-8', index=False)
        df2 = df2[selected_cols] 
        print(f"{selected_cols=}")
        print()

        df2 = normalize_df_columns(df2)
        print(f"normalized columns:{list(df2.columns)}")
        print()

        # df2.to_csv(f'{data_file}-sample-{SAMPLE_SIZE}.csv', encoding='utf-8', index=False)
        df2.to_csv(f'{data_file}.csv', encoding='utf-8', index=False)
        # print(df[selected_cols].info())
        # print(df1.info())
        # print()
        # print(df.count().to_string())
        print(df2.count().to_string())
        print()
        df2.info(verbose=True, max_cols=40, show_counts=True)
        return df2


def materialize():
    """
    Materialize function that returns a Pandas DataFrame.
    Bruin will automatically insert this DataFrame into DuckDB based on materialization strategy.
    """

    # dataset file is already downloaded and unpacked
    data_file1 = DATA_DIR + TARGET_FILE_NAME
    if os.path.exists(data_file1):
        print(f"Target file for extraction {TARGET_FILE_NAME} found: {data_file1}")
    else:
        print(f"Target file for extraction {TARGET_FILE_NAME} not found. Aborting.")
        exit(1)

    df1 = extract_json_reports(TARGET_FILE_NAME)
    df1 = pd.read_csv(f'{data_file1}.csv', encoding="utf-8")
    print(f"\n\n{data_file1}: {len(df1)}")
    df1.info()
        
    # Get Bruin parameters
    bruin_vars = json.loads(os.environ["BRUIN_VARS"])
    games_starting_year = bruin_vars.get('games_starting_year')
    protondb_starting_year = bruin_vars.get('protondb_starting_year')
    print(f"\n\n{games_starting_year=}, {protondb_starting_year=}")

    return df1

    # Get start and end dates from environment variables
    start_date = os.environ.get('BRUIN_START_DATE')
    end_date = os.environ.get('BRUIN_END_DATE')

