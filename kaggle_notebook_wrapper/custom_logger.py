import logging
from IPython import get_ipython
import nbformat
import builtins
import json
import os

class CustomAdapter(logging.LoggerAdapter):
    """
    This example log expects the passed in dict-like object to have a
    'cell_id' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        return '[cell_id: %s] %s' % (self.extra['cell_id'], msg), kwargs

class CustomContext:
    def __init__(self, metadata_path='kernel-metadata.json'):
        self.notebook_path = self._get_notebook_path(metadata_path)
        self.cells = self._load_cells()

    def _get_notebook_path(self, metadata_path):
        with open(metadata_path) as f:
            metadata = json.load(f)
            notebook_file = metadata['code_file']
        return notebook_file

    def _load_cells(self):
        with builtins.open(self.notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)
        return nb.cells

    def get_current_cell_id(self):
        # Get the current execution count
        ip = get_ipython()
        if ip is None:
            return None
        
        cell_source = ip.user_ns['In'][ip.execution_count]

        for cell in self.cells:
            if cell_source in cell['source']:
                return cell.metadata.get('cell_id')
        
        return None

    def __getitem__(self, key):
        return self.get_current_cell_id()
    
    def __iter__(self):
        return iter([])

def custom_logger(name, metadata_path='kernel-metadata.json'):
    logger = logging.getLogger(name)
    syslog = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(message)s')
    syslog.setFormatter(formatter)
    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        logger.addHandler(syslog)
    context = CustomContext(metadata_path)
    log = CustomAdapter(logger, context)
    log.setLevel(logging.INFO)
    return log