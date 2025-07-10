"""Compatibility wrapper for moved compressor module."""

from __future__ import annotations

import pathlib
import sys

# allow running as a standalone script
if __name__ == "__main__" and __package__ is None:
    ROOT = pathlib.Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

from scripts.glyph.compressor import *  # noqa: F401,F403

if __name__ == "__main__":  # pragma: no cover - passthrough to real entrypoint
    main()
