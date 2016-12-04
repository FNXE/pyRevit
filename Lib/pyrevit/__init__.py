import os
import os.path as op

# noinspection PyUnresolvedReferences
from System.Diagnostics import Process


# ----------------------------------------------------------------------------------------------------------------------
# testing for availability of __revit__ just in case and collect host information
# ----------------------------------------------------------------------------------------------------------------------
class _HostApplication:
    """Contains current host version and provides comparison functions."""
    def __init__(self):
        # define HOST_SOFTWARE
        try:
            # noinspection PyUnresolvedReferences
            self.uiapp = __revit__
        except Exception:
            raise Exception('Critical Error: Host software is not supported. (__revit__ handle is not available)')

    @property
    def version(self):
        return self.uiapp.Application.VersionNumber

    @property
    def username(self):
        """Return the username from Revit API (Application.Username)"""
        uname = self.uiapp.Application.Username
        uname = uname.split('@')[0]  # if username is email
        uname = uname.replace('.', '')  # removing dots since username will be used in file naming
        return uname

    @property
    def proc_id(self):
        return Process.GetCurrentProcess().Id

    @property
    def proc_name(self):
        return Process.GetCurrentProcess().ProcessName

    def is_newer_than(self, version):
        return int(self.version) > int(version)

    def is_older_than(self, version):
        return int(self.version) < int(version)


HOST_APP = _HostApplication()


# ----------------------------------------------------------------------------------------------------------------------
# Testing the value of __forceddebugmode__ (set in builtins scope by C# Script Executor)
# ----------------------------------------------------------------------------------------------------------------------
class _ExecutorParams(object):
    @property   # read-only
    def forced_debug_mode(self):
        try:
            # noinspection PyUnresolvedReferences
            return __forceddebugmode__
        except:
            return False

    @property   # read-only
    def window_handle(self):
        # noinspection PyUnresolvedReferences
        return __window__

    @property   # writeabe
    def command_name(self):
        # noinspection PyUnresolvedReferences
        return __commandname__

    @command_name.setter
    def command_name(self, value):
        # noinspection PyUnusedLocal
        __commandname__ = value


EXEC_PARAMS = _ExecutorParams()


# ----------------------------------------------------------------------------------------------------------------------
# environment info
# ----------------------------------------------------------------------------------------------------------------------
def _find_home_directory():
    """Return the pyRevitLoader.py full directory address"""
    try:
        return op.dirname(op.dirname(op.dirname(__file__)))   # 3 steps back for <home>/Lib/pyrevit
    except NameError:
        raise Exception('Critical Error. Can not find home directory.')


# main pyrevit repo folder
HOME_DIR = _find_home_directory()

# main pyrevit lib folder
MAIN_LIB_DIR = op.join(HOME_DIR, 'lib')

# default extension extensions folder
EXTENSIONS_DEFAULT_DIR = op.join(HOME_DIR, 'extensions')


PYREVIT_ADDON_NAME = 'pyrevit'
_VERSION_MAJOR = 4
_VERSION_MINOR = 0


# user env paths
USER_ROAMING_DIR = os.getenv('appdata')
USER_SYS_TEMP = os.getenv('temp')
