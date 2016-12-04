import ast
import inspect
import os
import os.path as op
import time

from pyrevit import HOST_APP
from pyrevit.core.exceptions import PyRevitException
from pyrevit.coreutils.logger import get_logger

# noinspection PyUnresolvedReferences
from System.Diagnostics import Process
# noinspection PyUnresolvedReferences
from System import AppDomain
# noinspection PyUnresolvedReferences
from System.Reflection import Assembly


logger = get_logger(__name__)


def enum(**enums):
    return type('Enum', (), enums)


class Timer:
    """Timer class using python native time module."""
    def __init__(self):
        self.start = time.time()

    def restart(self):
        self.start = time.time()

    def get_time(self):
        return time.time() - self.start


class ScriptFileParser:
    def __init__(self, file_address):
        self.file_addr = file_address
        try:
            with open(file_address, 'r') as f:
                self.ast_tree = ast.parse(f.read())
        except Exception as err:
            raise PyRevitException('Error parsing script file: {} | {}'.format(self.file_addr, err))

    def extract_param(self, param_name):
        try:
            for child in ast.iter_child_nodes(self.ast_tree):
                if hasattr(child, 'targets'):
                    for target in child.targets:
                        if hasattr(target, 'id') and target.id == param_name:
                            return ast.literal_eval(child.value)
        except Exception as err:
            raise PyRevitException('Error parsing parameter: {} in script file for : {} | {}'.format(param_name,
                                                                                                     self.file_addr,
                                                                                                     err))

        return None


def get_all_subclasses(parent_classes):
    sub_classes = []
    # if super-class, get a list of sub-classes. Otherwise use component_class to create objects.
    for parent_class in parent_classes:
        try:
            derived_classes = parent_class.__subclasses__()
            if len(derived_classes) == 0:
                sub_classes.append(parent_class)
            else:
                sub_classes.extend(derived_classes)
        except AttributeError:
            sub_classes.append(parent_class)
    return sub_classes


def get_sub_folders(search_folder):
    sub_folders = []
    for f in os.listdir(search_folder):
        if op.isdir(op.join(search_folder, f)):
            sub_folders.append(f)
    return sub_folders


def verify_directory(folder):
    """Checks if the folder exists and if not creates the folder.
    Returns OSError on folder making errors."""
    if not op.exists(folder):
        try:
            os.makedirs(folder)
        except OSError as err:
            raise err
    return True


def get_parent_directory(path):
    return op.dirname(path)


def join_strings(path_list):
    if path_list:
        return ';'.join(path_list)
    return ''


# character replacement list for cleaning up file names
SPECIAL_CHARS = {' ': '',
                 '~': '',
                 '!': 'EXCLAM',
                 '@': 'AT',
                 '#': 'NUM',
                 '$': 'DOLLAR',
                 '%': 'PERCENT',
                 '^': '',
                 '&': 'AND',
                 '*': 'STAR',
                 '+': 'PLUS',
                 ';': '', ':': '', ',': '', '\"': '', '{': '', '}': '', '[': '', ']': '', '\(': '', '\)': '',
                 '-': 'MINUS',
                 '=': 'EQUALS',
                 '<': '', '>': '',
                 '?': 'QMARK',
                 '.': 'DOT',
                 '_': 'UNDERS',
                 '|': 'VERT',
                 '\/': '', '\\': ''}


def cleanup_string(input_str):
    # remove spaces and special characters from strings
    for char, repl in SPECIAL_CHARS.items():
        input_str = input_str.replace(char, repl)

    return input_str


def get_revit_instances():
    return len(list(Process.GetProcessesByName(HOST_APP.proc_name)))


def run_process(proc, cwd=''):
    import subprocess
    return subprocess.Popen(proc, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, shell=True)


def inspect_calling_scope_local_var(variable_name):
    """Traces back the stack to find the variable in the caller local stack.
    Example:
    PyRevitLoader defines __revit__ in builtins and __window__ in locals. Thus, modules have access to
    __revit__ but not to __window__. This function is used to find __window__ in the caller stack.
    """
    frame = inspect.stack()[1][0]
    while variable_name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[variable_name]


def inspect_calling_scope_global_var(variable_name):
    """Traces back the stack to find the variable in the caller local stack.
    Example:
    PyRevitLoader defines __revit__ in builtins and __window__ in locals. Thus, modules have access to
    __revit__ but not to __window__. This function is used to find __window__ in the caller stack.
    """
    frame = inspect.stack()[1][0]
    while variable_name not in frame.f_globals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[variable_name]


def find_loaded_asm(asm_name):
    logger.debug('Finding assembly: {}'.format(asm_name))
    loaded_asm_list = []
    for loaded_assembly in AppDomain.CurrentDomain.GetAssemblies():
        if asm_name.lower() == str(loaded_assembly.GetName().Name).lower():
            loaded_asm_list.append(loaded_assembly)

    count = len(loaded_asm_list)
    if count == 0:
        logger.debug('Assembly not found.')
        return None
    elif count == 1:
        found_asm = loaded_asm_list[0]
        logger.debug('Assembly found: {}'.format(found_asm))
        return found_asm
    elif count > 1:
        found_asm_list = loaded_asm_list
        logger.debug('More than one assembly found: {}'.format(found_asm_list))
        return loaded_asm_list


def load_asm_file(asm_file):
    return Assembly.LoadFile(asm_file)


def make_full_classname(namespace, class_name):
    return '{}.{}'.format(namespace, class_name)
