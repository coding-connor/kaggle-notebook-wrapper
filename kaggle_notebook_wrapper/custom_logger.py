import logging
import sys
from IPython import get_ipython
import nbformat
import builtins
import json
import os

class CustomAdapter(logging.LoggerAdapter):
    """
     Prepend the value of cell_id to the log message.
    """
    def process(self, msg, kwargs):
        return f"[cell_id: {self.extra['cell_id']}] {msg}", kwargs

class CustomContext:
    """
    CustomContext provides a dictionary-like interface to supply context for the logger CustomAdapter. 
    It is specifically designed to retrieve the metadata 'cell_id' from the currently executing cell in a Jupyter notebook that's been linked to Kaggle.
    """
    def __init__(self, notebook_path):
        self.notebook_path = notebook_path
        self.cells = self._load_cells()

    def _get_notebook_path(self, metadata_path):
        """
        Retrieves the notebook file path from a Kaggle kernel-metadata.json file.
        """
        with open(metadata_path) as f:
            metadata = json.load(f)
            notebook_file = metadata['code_file']
        return notebook_file

    def _load_cells(self):
        """
        Loads the cells from the notebook file.
        """
        try:
            with builtins.open(self.notebook_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)
            return nb.cells
        except FileNotFoundError:
            logging.error(f"Notebook file {self.notebook_path} not found.")
            return []
        except Exception as e:
            logging.error(f"Error loading notebook file {self.notebook_path}: {e}")
            return []

    def get_current_cell_id(self):
        """
        Returns the ID of the currently executing cell.
        """
        try:
            ip = get_ipython()
            if ip is None:
                logging.warning("IPython environment not found.")
                return None
            
            # Get the current execution count
            cell_source = ip.user_ns['In'][ip.execution_count]

            for cell in self.cells:
                if cell_source in cell['source']:
                    return cell.metadata.get('cell_id')
            
            logging.warning("Current cell ID not found.")
            return None
        except Exception as e:
            logging.error(f"Error retrieving current cell ID: {e}")
            return None

    def __getitem__(self, key):
        return self.get_current_cell_id()
    
    def __iter__(self):
        return iter([])

class LoggerStream:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():  # Avoid logging empty messages
            self.logger.log(self.level, message)

    def flush(self):
        pass  # No need to implement flush for logging

def custom_logger(name, notebook_path="__notebook__.ipynb"):
    """
    Creates and returns a custom logger with a specified name and optional notebook path.
    If the default notebook path is used and the file does not exist, it prints a message indicating that custom logging is disabled and returns a default logger.
    """
    logger = logging.getLogger(name)
    if notebook_path == "__notebook__.ipynb" and not os.path.isfile(notebook_path):
        print("Default notebook path __notebook__.pynb not found. This likely means you are not running in a Kaggle notebook, or that you are using a Kaggle interactive session.")
        print("Custom logging disabled. Default logging will be used instead.")
        return logger
    try:
        syslog = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(message)s')
        syslog.setFormatter(formatter)
        if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            logger.addHandler(syslog)
        context = CustomContext(notebook_path)
        log = CustomAdapter(logger, context)
        log.setLevel(logging.INFO)

        # Redirect stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = LoggerStream(log, logging.INFO)
        sys.stderr = LoggerStream(log, logging.ERROR)

        return log
    except Exception as e:
        logging.error(f"Error setting up custom logger: {e}. Using default logger.")
        # Restore original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        return logger