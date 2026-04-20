import os
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

def load_duckdb_settings(connection_string):
    # using environment variables, including DUCKDB connection settings
    connection = os.environ.get('DUCKDB_CONNECTION', connection_string)
    if connection:
        if DEBUG:
            print('DUCKDB_CONNECTION:', connection)
    else:
        print ('The DUCKDB_CONNECTION environment variable is not defined.\n')
        return None

    return connection

def load_gcp_settings():
    # using environment variables, including Google Cloud credentials
    credentials = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None)
    if credentials:
        if DEBUG:
            print('GOOGLE_APPLICATION_CREDENTIALS:', credentials)
        if (not os.path.exists(credentials)):
            print (f'The GOOGLE_APPLICATION_CREDENTIALS file {credentials} does not exist.\n')
            return None, None, None
    else:
        print ('The GOOGLE_APPLICATION_CREDENTIALS environment variable is not defined.\n')
        return None, None, None

    project_name = os.environ.get('GCP_PROJECT_NAME', None)
    dataset = os.environ.get('BQ_DATASET', None)
    if DEBUG:
        print(f'GCP Credentials file: {credentials}, GCP_PROJECT_NAME: {project_name}, BQ_DATASET: {dataset}')
    return credentials, project_name, dataset


# show extra information for checking execution
DEBUG = True # False

# DATA_DIR = f'./data/'  # ! with '/' at the end!
DATA_DIR = f'/app/data/'  # ! with '/' at the end!
# DATA_DIR = f'/tmp/dl/app/test/proj-data/'  # ! with '/' at the end!
VISUALS_DIR = './visuals/'

SKIP_DOWNLOADING = False # True # False 
START_YEAR = 2025 # 2010
START_DATE = f'{START_YEAR}-01-01'

# Github dataset info: Data exports from ProtonDB.com released under ODbL https://github.com/bdefore/protondb-data
GH_OWNER = 'bdefore'
GH_REPO = 'protondb-data'
GH_TOKEN = '' # Use a real token if needed
TARGET_FILE_NAME = 'reports_piiremoved.json'

SELECTED_COLS = [
    'app_steam_appId', 'app_title', 
    'timestamp', 
    'systemInfo_cpu', 'systemInfo_gpu', 'systemInfo_gpuDriver', 'systemInfo_kernel', 'systemInfo_os', 'systemInfo_ram',
    # 'systemInfo_steamRuntimeVersion', 'systemInfo_xWindowManager', # recent records 98%

    # 'responses_customProtonVersion', # 'responses_protonVersion', 
    'responses_verdict', 
    # 'responses_answerToWhatGame', # duplicate of app_steam_appId
    'responses_installs', 
    'responses_opens', 
    'responses_startsPlay', 
    
    # 'responses_launcher', 
    # 'responses_audioFaults', 
    # 'responses_graphicalFaults', 
    # 'responses_inputFaults', 
    # 'responses_performanceFaults', 
    # 'responses_saveGameFaults', 
    # 'responses_stabilityFaults', 
    # 'responses_windowingFaults', 

    'responses_significantBugs', 
    # 'responses_variant', # recent records 100% 
    # 'responses_notes_verdict', 
    # 'responses_tinkerOverride', 
    # 'responses_triedOob', 
    # 'responses_concludingNotes', # ~50%

    # 'responses_batteryPerformance', 'responses_concludingNotes', 'responses_controlLayout', 'responses_controlLayoutCustomization', 'responses_customProtonVersion', 'responses_customizationsUsed_configChange', 'responses_customizationsUsed_protonfixes', 'responses_didChangeControlLayout', 'responses_followUp_audioFaults_crackling', 'responses_followUp_audioFaults_lowQuality', 'responses_followUp_audioFaults_outOfSync', 'responses_followUp_controlLayoutCustomization_enableGripButtons', 'responses_followUp_graphicalFaults_heavyArtifacts', 'responses_followUp_graphicalFaults_minorArtifacts', 'responses_followUp_graphicalFaults_missingTextures', 'responses_followUp_inputFaults_controllerMapping', 'responses_followUp_inputFaults_controllerNotDetected', 
    # 'responses_followUp_performanceFaults', 
    # 'responses_followUp_saveGameFaults_errorSaving', 'responses_followUp_stabilityFaults', 'responses_followUp_windowingFaults_activatingFullscreen', 'responses_followUp_windowingFaults_fullNotFull', 'responses_followUp_windowingFaults_switching', 
    # 'responses_notes_audioFaults', 
    # 'responses_notes_graphicalFaults', 
    # 'responses_notes_inputFaults', 'responses_notes_performanceFaults', 
    # 'responses_notes_readability', 'responses_notes_significantBugs', 'responses_notes_stabilityFaults', 
    # 'responses_notes_windowingFaults', 
    # 'responses_readability', 
    # 'responses_secondaryLauncher', 
    # 'responses_variant', 
]

CATEGORICAL_COLS = [
    'responses_verdict', 
    'responses_installs', 
    'responses_opens', 
    'responses_startsPlay', 
    'responses_significantBugs', 
]


games_sets = {
    "popular": ["Desperados: Wanted Dead or Alive", "Injustice: Gods Among Us Ultimate Edition", "Resident Evil Revelations", ],
    "set1": ["Battlefield™ 2042", "PAYDAY 3", ],
} 
SELECTED_GAMES = games_sets["popular"]                    


SAMPLE = 'sample' # export samples to .csv 
PARQUET = 'parquet' # export to .parquet files
DUCKDB = 'duckdb' # export to DuckDB
BIGQUERY = 'bigquery' # export to BigQuery

MODE = os.environ.get('DATAWAREHOUSE', BIGQUERY) # DUCKDB BIGQUERY SAMPLE
CHUNKSIZE = 100_000 # 100_000
SAMPLE_SIZE = 1000

DUCKDB_CONNECTION_STRING = '/app/test/my-pipeline/duckdb.db'
if MODE==DUCKDB:
    DUCKDB_CONNECTION = load_duckdb_settings(DUCKDB_CONNECTION_STRING)
else:
    DUCKDB_CONNECTION = None

if MODE==BIGQUERY:
    GCP_CREDENTIALS, GCP_PROJECT_NAME, BQ_DATASET = load_gcp_settings()
else:    
    GCP_CREDENTIALS, GCP_PROJECT_NAME, BQ_DATASET = None, None, None
