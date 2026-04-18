from __future__ import annotations

import os
from typing import Optional

_DLL_HANDLE: Optional[object] = None


def configure_oqs_dll_search_path() -> None:
    """Make a manual liboqs install visible to Python on Windows."""
    global _DLL_HANDLE

    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    oqs_root = os.environ.get("OQS_INSTALL_PATH", r"C:\liboqs")
    oqs_bin = os.path.join(oqs_root, "bin")
    if os.path.isdir(oqs_bin):
        _DLL_HANDLE = os.add_dll_directory(oqs_bin)
