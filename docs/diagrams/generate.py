# Standard library imports
import importlib.util
import os
import shlex
import subprocess
import sys

# Third party imports

# Local Imports


# ==========================
# CONFIG
# ==========================
PATH_TO_ROOT = os.path.join("..", "..")
EXCLUDED_DIRS = ['venv', 'diagrams']


def get_project_py_files(root_dir):
    """ Returns list of paths for all local python project files NOT in EXCLUDED_DIRS"""
    paths = []

    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith(".py") and 'venv' not in file:
                paths.append(os.path.join(root, file))

    return paths


def import_module(path):
    """
    Import module from absolute path given with name of module's filename. Same as saying 'import X as [X filename]'

    ex:
    path = C:\\Users\\john\\Projects\\pomodoro_audio_player\\source\\ui\\screens.py
    Would import screens.py as screens

    """

    # Create module name
    module_name = os.path.basename(path)[:-3]
    # Create spec
    spec = importlib.util.spec_from_file_location(module_name, path)
    # Create module from spec
    module = importlib.util.module_from_spec(spec)
    # Load the module
    try:
        spec.loader.exec_module(module)
    except ImportError:
        print("Failed on {}".format(module_name))
    # Lets us refer to the module
    sys.modules[module_name] = module


def run_pyreverse(file_name=__file__):
    """run pyreverse"""
    command = 'pyreverse -o png -p componentplain {0}'.format(file_name)
    subprocess.call(shlex.split(command))


if __name__ == '__main__':
    root_dir = os.path.abspath(PATH_TO_ROOT)
    paths = get_project_py_files(root_dir=root_dir)
    print(paths)
    for p in paths:
        import_module(path=p)
    run_pyreverse()
    print("hello")
