"""
compiler.py — Pipeline Compiler lengkap untuk JogLang.

Mengintegrasikan seluruh tahap kompilasi:
  Lexer -> Parser -> SemanticAnalyzer -> Optimizer -> CodeGenerator

Menyediakan:
  - class Compiler       : pipeline lengkap dengan opsi verbose & optimasi
  - class CompileResult  : hasil kompilasi terstruktur
  - function compile()   : shortcut satu baris
  - function compile_file(): kompilasi dari file .jog
"""

from __future__ import annotations
import time
import os
from dataclasses import dataclass, field
from typing import Optional

from .lexer    import Lexer
from .parser   import Parser
from .semantic import SemanticAnalyzer
from .optimizer import Optimizer, OptimizationStats
from .codegen  import CodeGenerator
from .utils    import read_source_file, write_output_file, get_output_path
from .errors   import (
    JogLangError, LexicalError, SyntaxError_,
    SemanticError, OptimizationError, CodeGenerationError,
)
from .token    import Token
from .ast_nodes import ProgramNode


# ===========================================================================
# COMPILE RESULT
# ===========================================================================

@dataclass
class CompileResult:
    """
    Hasil proses kompilasi lengkap.

    Attributes:
        success       : True jika kompilasi berhasil tanpa error
        source_path   : Path file sumber .jog (jika dari file)
        output_path   : Path file output .py (jika disimpan)
        python_code   : Kode Python hasil generasi
        tokens        : List token dari Lexer (jika verbose)
        ast           : AST asli dari Parser (jika verbose)
        optimized_ast : AST setelah optimasi (jika verbose)
        opt_stats     : Statistik optimasi
        error         : Error pertama yang terjadi (jika gagal)
        elapsed_ms    : Waktu kompilasi dalam milidetik
        stage         : Tahap di mana kompilasi berhenti (jika gagal)
    """
    success:       bool                       = False
    source_path:   Optional[str]              = None
    output_path:   Optional[str]              = None
    python_code:   str                        = ""
    tokens:        list                       = field(default_factory=list)
    ast:           Optional[ProgramNode]      = None
    optimized_ast: Optional[ProgramNode]      = None
    opt_stats:     Optional[OptimizationStats] = None
    error:         Optional[JogLangError]     = None
    elapsed_ms:    float                      = 0.0
    stage:         str                        = ""

    def __str__(self) -> str:
        if self.success:
            lines = [f"[OK] Kompilasi berhasil ({self.elapsed_ms:.1f}ms)"]
            if self.output_path:
                lines.append(f"     Output: {self.output_path}")
            if self.opt_stats:
                lines.append(f"     {self.opt_stats.summary()}")
            return "\n".join(lines)
        return (
            f"[GAGAL] Kompilasi gagal pada tahap '{self.stage}' "
            f"({self.elapsed_ms:.1f}ms)\n"
            f"     {self.error}"
        )


# ===========================================================================
# COMPILER CLASS
# ===========================================================================

class Compiler:
    """
    Pipeline kompilasi lengkap JogLang -> Python.

    Usage:
        # Compile dari string source
        result = Compiler().compile_source(source_code)

        # Compile dari file
        result = Compiler().compile_file("examples/halo.jog")

        # Dengan opsi
        result = Compiler(verbose=True, optimize=True).compile_source(src)
    """

    def __init__(
        self,
        verbose:  bool = False,
        optimize: bool = True,
        output_dir: str = "output",
    ) -> None:
        """
        Args:
            verbose   : Jika True, simpan tokens dan AST di CompileResult
            optimize  : Jika True, jalankan optimizer (default: True)
            output_dir: Direktori untuk menyimpan file output
        """
        self.verbose    = verbose
        self.optimize   = optimize
        self.output_dir = output_dir

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def compile_source(
        self,
        source:      str,
        source_path: Optional[str] = None,
        save_output: bool          = False,
    ) -> CompileResult:
        """
        Kompilasi source code JogLang dari string.

        Args:
            source     : Source code JogLang
            source_path: Path file asal (opsional, untuk penamaan output)
            save_output: Jika True, simpan hasil ke file .py

        Returns:
            CompileResult berisi hasil dan metadata kompilasi
        """
        result = CompileResult(source_path=source_path)
        start  = time.perf_counter()

        try:
            # ─── TAHAP 1: LEXER ──────────────────────────────────────────
            result.stage = "Lexer"
            lexer  = Lexer(source)
            tokens = lexer.tokenize()
            if self.verbose:
                result.tokens = tokens

            # ─── TAHAP 2: PARSER ─────────────────────────────────────────
            result.stage = "Parser"
            parser = Parser(tokens)
            ast    = parser.parse()
            if self.verbose:
                result.ast = ast

            # ─── TAHAP 3: SEMANTIC ANALYSIS ──────────────────────────────
            result.stage = "Semantic Analysis"
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)

            # ─── TAHAP 4: CODE OPTIMIZATION ──────────────────────────────
            if self.optimize:
                result.stage = "Optimizer"
                optimizer = Optimizer()
                ast       = optimizer.optimize(ast)
                result.opt_stats     = optimizer.stats
                result.optimized_ast = ast if self.verbose else None
            else:
                result.optimized_ast = ast if self.verbose else None

            # ─── TAHAP 5: CODE GENERATION ────────────────────────────────
            result.stage = "Code Generator"
            gen          = CodeGenerator()
            python_code  = gen.generate(ast)
            result.python_code = python_code

            # ─── SIMPAN OUTPUT ───────────────────────────────────────────
            if save_output and source_path:
                out_path = get_output_path(source_path, self.output_dir)
                write_output_file(out_path, python_code)
                result.output_path = out_path

            result.success = True
            result.stage   = "Selesai"

        except JogLangError as e:
            result.error = e

        finally:
            result.elapsed_ms = (time.perf_counter() - start) * 1000

        return result

    def compile_file(self, filepath: str) -> CompileResult:
        """
        Kompilasi file .jog dan simpan hasilnya ke file .py.

        Args:
            filepath: Path ke file .jog

        Returns:
            CompileResult
        """
        result = CompileResult(source_path=filepath)
        try:
            source = read_source_file(filepath)
        except (FileNotFoundError, ValueError) as e:
            result.error = CodeGenerationError(str(e))
            result.stage = "File I/O"
            return result

        return self.compile_source(source, source_path=filepath, save_output=True)


# ===========================================================================
# CONVENIENCE FUNCTIONS
# ===========================================================================

def compile(source: str, optimize: bool = True) -> CompileResult:
    """
    Shortcut: kompilasi source code JogLang dan kembalikan hasil.

    Args:
        source  : Source code JogLang
        optimize: Aktifkan optimizer (default: True)

    Returns:
        CompileResult
    """
    return Compiler(optimize=optimize).compile_source(source)


def compile_file(filepath: str, optimize: bool = True) -> CompileResult:
    """
    Shortcut: kompilasi file .jog dan simpan ke output/.

    Args:
        filepath: Path file .jog
        optimize: Aktifkan optimizer (default: True)

    Returns:
        CompileResult
    """
    return Compiler(optimize=optimize).compile_file(filepath)


def compile_and_run(source: str, optimize: bool = True) -> Optional[str]:
    """
    Kompilasi dan jalankan langsung kode JogLang.
    HANYA untuk keperluan testing/demo.

    Args:
        source  : Source code JogLang
        optimize: Aktifkan optimizer (default: True)

    Returns:
        None jika sukses, string pesan error jika gagal

    Raises:
        JogLangError: jika kompilasi gagal
        Exception   : jika eksekusi Python gagal
    """
    result = compile(source, optimize=optimize)
    if not result.success:
        raise result.error

    # Eksekusi kode Python yang dihasilkan
    exec(result.python_code, {})
    return None
