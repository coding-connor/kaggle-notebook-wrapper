import argparse
import subprocess
import time
import json
import os
import re
from kaggle_notebook_wrapper.log_parsing import process_logs

def push_notebook(path=None):
    """Push the notebook to Kaggle."""
    command = ['kaggle', 'kernels', 'push']
    if path:
        command.extend(['--path', path])
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while pushing the notebook: {e}")
        print(f"Error output: {e.stderr}")

def pull_results(kernel_id):
    """Pull the results of the notebook execution from Kaggle."""
    log_file_path = None
    while True:
        try:
            result = subprocess.run(['kaggle', 'kernels', 'status', kernel_id], check=True, capture_output=True, text=True)
            output = result.stdout
            print(output)
            if "complete" in output.lower():
                break
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while checking the status: {e}")
            print(f"Error output: {e.stderr}")
            raise
        time.sleep(2)  

    # Download the log file
    try:
        result = subprocess.run(['kaggle', 'kernels', 'output', kernel_id], check=True, capture_output=True, text=True)
        print(result.stdout)
        # Extract log file path from the output
        match = re.search(r'Kernel log downloaded to (.+\.log)', result.stdout)
        if match:
            log_file_path = match.group(1)
        else:
            raise FileNotFoundError("Error locating .log file to parse")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while downloading the log file: {e}")
        print(f"Error output: {e.stderr}")
        raise

    return log_file_path

def sync_notebook(path=None):
    """Sync the notebook by pushing it and pulling the results."""
    metadata_path = os.path.join(path, 'kernel-metadata.json') if path else 'kernel-metadata.json'
    with open(metadata_path) as f:
        metadata = json.load(f)
        kernel_id = metadata['id']
        notebook_file = metadata['code_file']

    push_notebook(path)
    log_file_path = pull_results(kernel_id)

    # Process logs after pulling results
    if log_file_path:
        notebook_path = os.path.join(path, notebook_file) if path else notebook_file
        process_logs(notebook_path, log_file_path)

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Kaggle Notebook Wrapper CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help="Push the notebook and pull the results")
    sync_parser.add_argument('-p', '--path', help="Folder for upload, containing data files and a special kernel-metadata.json file (https://github.com/Kaggle/kaggle-api/wiki/Kernel-Metadata). Defaults to current working directory")
    sync_parser.set_defaults(func=lambda args: sync_notebook(args.path))

    args = parser.parse_args()

    if args.command == 'sync':
        args.func(args)
    else:
        if not hasattr(args, 'kaggle_args') or not args.kaggle_args:
            print("No arguments provided for kaggle CLI")
            return

if __name__ == "__main__":
    main()