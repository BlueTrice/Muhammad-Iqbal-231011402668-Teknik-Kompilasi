"""
main.py — Wrapper kompatibilitas lama untuk menjalankan JogLang Compiler
langsung dari source tanpa instalasi (python main.py <file.jog>).

Logic CLI yang sesungguhnya sudah dipindahkan ke dalam package, di
joglang_compiler/cli.py, supaya ikut ter-package saat `pip install .`
dan supaya `joglang` (console script) serta `python -m joglang_compiler`
dapat menemukannya juga. File ini hanya pemanggil tipis (thin wrapper)
agar perilaku `python main.py ...` yang lama tetap berfungsi sama persis.

Penggunaan:
    python main.py <file.jog> [opsi]
"""

from __future__ import annotations
import sys
import os

# Pastikan direktori project ada di path saat dijalankan langsung dari
# source checkout (belum pip install), supaya `import joglang_compiler`
# tetap berhasil.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from joglang_compiler.cli import main

if __name__ == "__main__":
    sys.exit(main())
