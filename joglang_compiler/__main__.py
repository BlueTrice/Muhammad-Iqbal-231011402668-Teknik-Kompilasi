"""
__main__.py — Entry point untuk `python -m joglang_compiler`.

Memanggil CLI yang sama dengan command `joglang` dan `python main.py`.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
