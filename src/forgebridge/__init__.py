"""ForgeBridge inventory, one UVTT scene slice, and LevelDB compendium reading.

This package reads Foundry VTT package files and reports what is in them.
It can also write one scene as UVTT JSON plus a loss report.
It does not run imported code.
"""

from forgebridge.version import get_version

__version__ = get_version()
IR_VERSION = "0.1.0"
