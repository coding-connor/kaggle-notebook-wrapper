import json
import re
import nbformat
import shutil
import builtins
from nbformat.notebooknode import NotebookNode
import difflib

def read_log_file(log_file_path):
    print(f"Reading log file: {log_file_path}")
    with open(log_file_path, 'r') as log_file:
        log_content = log_file.read()
    print("Read log file content")
    return log_content

def extract_log_entries(log_content):
    log_data = []
    try:
        log_entries = json.loads(log_content)
        for entry in log_entries:
            log_message = entry.get('data', '')
            match = re.search(r'\[cell_id: (\d+)\]', log_message)
            if match:
                cell_id = int(match.group(1))
                log_data.append((cell_id, log_message))
                print(f"Extracted log for cell_id {cell_id}: {log_message}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    print(f"Extracted {len(log_data)} log entries with cell_id")
    return log_data

def append_logs_to_cells(notebook_path, log_data):
    try:
        with builtins.open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        # Append logs to the first cell
        if nb.cells:
            nb.cells[0].source += '\n' + '\n'.join(log_data)
        else:
            nb.cells.append(nbformat.v4.new_code_cell('\n'.join(log_data)))

        with builtins.open(notebook_path, 'w') as f:
            nbformat.write(nb, f)

        # Debugging: Verify the notebook content after writing
        with builtins.open(notebook_path, 'r') as f:
            nb_after = nbformat.read(f, as_version=4)

        # Check if nb and nb_after are the same
        if nb == nb_after:
            print("Notebook content is the same before and after writing.")
        else:
            print("Notebook content differs before and after writing.")
            # Print differences
            nb_str = json.dumps(nb, indent=2)
            nb_after_str = json.dumps(nb_after, indent=2)
            diff = difflib.unified_diff(nb_str.splitlines(), nb_after_str.splitlines(), lineterm='')
            for line in diff:
                print(line)

        print("Finished appending logs to notebook")
   
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Restoring from backup...")
        shutil.copy(notebook_path + '.bak', notebook_path)
        print("Restored from backup")
        raise e

def backup_notebook(notebook_path):
    backup_path = notebook_path + '.bak'
    shutil.copy(notebook_path, backup_path)
    print(f"Backup created: {backup_path}")

def process_logs(notebook_path, log_file_path):
    """Process logs and append them to the notebook."""
    backup_notebook(notebook_path)
    log_content = read_log_file(log_file_path)
    log_data = extract_log_entries(log_content)
    append_logs_to_cells(notebook_path, log_data)

