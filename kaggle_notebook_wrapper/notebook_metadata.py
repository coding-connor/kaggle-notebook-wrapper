import nbformat
import builtins

def add_cell_ids(notebook_path):
    with builtins.open(notebook_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)

        # Set metadata cell_id
        for i, cell in enumerate(nb.cells):
            cell.metadata['cell_id'] = i

    with builtins.open(notebook_path, 'w') as f:
        nbformat.write(nb, f)