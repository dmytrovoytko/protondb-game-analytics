"""@bruin
name: ingest.download
type: python
image: python:3.12
description: |
    Downloads ProtonDB data from github repo json file using Python requests library.

@bruin"""

import requests
import os

import tarfile

try:
    from .settings import DATA_DIR, DEBUG, SKIP_DOWNLOADING
    from .settings import GH_OWNER, GH_REPO, GH_TOKEN
    from .settings import TARGET_FILE_NAME
except:
    from settings import DATA_DIR, DEBUG, SKIP_DOWNLOADING
    from settings import GH_OWNER, GH_REPO, GH_TOKEN
    from settings import TARGET_FILE_NAME

if DEBUG:
    import tracemalloc
    # Start tracing memory allocations
    tracemalloc.start()

def memory_check(i=''):
    # Take a snapshot of the current and peak memory usage
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    print(f"--{i}-- Current memory usage: {current_mem / (1024 * 1024):.2f} MiB. Peak memory usage: {peak_mem / (1024 * 1024):.2f} MiB")

if DEBUG:
    memory_check("Download start")

def gh_list_latest_added_files(owner=GH_OWNER, repo=GH_REPO, token=GH_TOKEN):
    """
    Lists files added in the latest commit of a GitHub repository using the API.
    """

    # Endpoint to get repo info, including default_branch
    repo_info_url = f'https://api.github.com/repos/{owner}/{repo}'
    # Endpoint to list commits (we only need the latest one)
    commits_url = f'https://api.github.com/repos/{owner}/{repo}/commits?per_page=1'
    headers = {"Authorization": f"token {token}"} if token else {}

    try:
        response = requests.get(repo_info_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        # default_branch = response.json()
        # print(f"{default_branch=}")
        default_branch = response.json()["default_branch"]

        response = requests.get(commits_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        latest_commit = response.json()[0]
        commit_sha = latest_commit['sha']
        
        # Endpoint to get details of a specific commit
        commit_details_url = f'https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}'
        details_response = requests.get(commit_details_url, headers=headers)
        details_response.raise_for_status()
        commit_data = details_response.json()
        # print(f"{commit_data=}")
        added_files = []
        for file in commit_data['files']:
            # 'A' change type means the file was added
            if file['status'] == 'added':
                added_files.append(f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/"+file['filename'])
        return added_files

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub API: {e}")
        return []

def unpack_tar_gz_from_url(url, extract_path='.'):
    """
    Downloads a .tar.gz file from a URL and extracts its contents.

    Args:
            url (str): The URL of the .tar.gz file.
            extract_path (str): The directory to extract files into.
    """
    try:
        # Create the extraction directory if it doesn't exist
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)

        # Use requests to get the file content as a stream
        # Setting stream=True ensures the entire file isn't loaded into memory at once
        with requests.get(url, stream=True) as r:
            # Use BytesIO to treat the raw response stream as a file-like object
            with tarfile.open(fileobj=r.raw, mode="r:*") as tar_obj:
                print(f" ... extracting contents to: {os.path.abspath(extract_path)}")
                # Extract archived files
                tar_obj.extractall(path=extract_path, filter="data")
        print("Extraction complete.")
        if os.path.isfile(extract_path+TARGET_FILE_NAME):
            return True
        else:
            print(f"Error in archive content: {TARGET_FILE_NAME} is not found in downloaded archive {url}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error during download: {e}")
        return False
    except tarfile.TarError as e:
        print(f"Error during tarfile operation: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    return False


def get_dataset_file():
    # first get list of latest added files in target GH repo
    added_file_urls = gh_list_latest_added_files()
    print(f"Files added in the latest commit of {GH_OWNER}/{GH_REPO}:")
    for url in added_file_urls:
        print(f"--> processing {url}")
        # download latest archive from github repo
        # we actually expect only 1 file
        return unpack_tar_gz_from_url(url, extract_path=DATA_DIR)

###################

def download_gh_files():
    if SKIP_DOWNLOADING or get_dataset_file():
        data_file = DATA_DIR + TARGET_FILE_NAME
        print(f"Target file for extraction {TARGET_FILE_NAME} found: {data_file}")
    else:
        print(f"Target file for extraction {TARGET_FILE_NAME} not found. Aborting.")
        exit(1)
    if DEBUG:
        memory_check("Downloading complete")

######################################

def main():
    download_gh_files()

if __name__ == "__main__":
    main()