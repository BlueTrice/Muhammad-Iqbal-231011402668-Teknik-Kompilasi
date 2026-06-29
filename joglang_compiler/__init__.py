"""
JogLang Compiler Package
========================
Mini compiler untuk bahasa JogLang (bahasa Jawa dialek Yogyakarta).

Tahapan compiler:
  1. Lexer           - Tokenisasi source code
  2. Parser          - Membangun AST dari token
  3. AST             - Representasi pohon sintaks abstrak
  4. Semantic Analysis - Pemeriksaan semantik
  5. Code Optimization - Optimasi kode
  6. Code Generation  - Menghasilkan kode Python

Author : JogLang Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__  = "JogLang Team"
__language__ = "JogLang"
__extension__ = ".jog"
