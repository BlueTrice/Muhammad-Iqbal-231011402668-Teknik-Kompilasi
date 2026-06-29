"""
cli.py — CLI (Command Line Interface) JogLang Compiler.

Dipindahkan dari main.py (root project) ke dalam package
joglang_compiler agar ikut ter-package saat instalasi via pip,
dan agar entry_points 'joglang' serta 'python -m joglang_compiler'
dapat menemukannya. Perilaku/isi TIDAK diubah dari versi main.py asli.

Penggunaan:
    joglang <file.jog> [opsi]
    python -m joglang_compiler <file.jog> [opsi]
    python main.py <file.jog> [opsi]   (kompatibilitas lama)

Opsi:
    -o, --output <dir>   Direktori output (default: output/)
    -v, --verbose        Tampilkan informasi lengkap (token, AST, stats)
    --no-optimize        Nonaktifkan optimizer
    --run                Kompilasi lalu jalankan hasilnya
    --tokens             Hanya tampilkan token (debug lexer)
    --ast                Hanya tampilkan AST (debug parser)
    --version            Tampilkan versi
    -h, --help           Tampilkan bantuan ini
"""

from __future__ import annotations
import sys
import os
import argparse

from . import __version__, __language__, __extension__
from .compiler import Compiler
from .lexer import Lexer
from .parser import Parser
from .utils import read_source_file, print_banner
from .repl  import start_repl
from .errors import JogLangError


# ===========================================================================
# CLI ARGUMENT PARSER
# ===========================================================================

def _build_arg_parser() -> argparse.ArgumentParser:
    """Membangun argument parser untuk CLI."""
    ap = argparse.ArgumentParser(
        prog="joglang",
        description=(
            f"JogLang Compiler v{__version__} — "
            "Kompiler Basa Jawa Dialek Yogyakarta"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  joglang examples/halo.jog
  joglang examples/halo.jog --run
  joglang examples/halo.jog -o hasil/ --verbose
  joglang examples/halo.jog --tokens
  joglang examples/halo.jog --ast
        """,
    )

    ap.add_argument(
        "file",
        nargs="?",
        help=f"File source JogLang ({__extension__})",
    )
    ap.add_argument(
        "-o", "--output",
        default="output",
        metavar="DIR",
        help="Direktori output (default: output/)",
    )
    ap.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Tampilkan informasi lengkap",
    )
    ap.add_argument(
        "--no-optimize",
        action="store_true",
        help="Nonaktifkan optimizer",
    )
    ap.add_argument(
        "--run",
        action="store_true",
        help="Kompilasi lalu jalankan hasilnya langsung",
    )
    ap.add_argument(
        "--tokens",
        action="store_true",
        help="Debug: hanya tampilkan hasil tokenisasi",
    )
    ap.add_argument(
        "--ast",
        action="store_true",
        help="Debug: hanya tampilkan AST hasil parsing",
    )
    ap.add_argument(
        "--version",
        action="version",
        version=f"JogLang Compiler v{__version__}",
    )

    return ap


# ===========================================================================
# MODE HANDLERS
# ===========================================================================

def _mode_tokens(source: str) -> int:
    """Mode debug: tampilkan daftar token."""
    print("═" * 60)
    print("  TOKEN LIST")
    print("═" * 60)
    try:
        tokens = Lexer(source).tokenize()
        for tok in tokens:
            print(f"  [{tok.line:3d}:{tok.column:<3d}]  "
                  f"{tok.type.name:<20s}  {tok.lexeme!r}")
        print(f"\nTotal: {len(tokens)} token")
        return 0
    except JogLangError as e:
        print(f"\n{e}", file=sys.stderr)
        return 1


def _mode_ast(source: str) -> int:
    """Mode debug: tampilkan AST."""
    print("═" * 60)
    print("  ABSTRACT SYNTAX TREE")
    print("═" * 60)
    try:
        from .lexer import tokenize
        from .parser import parse
        tokens = tokenize(source)
        ast    = parse(tokens)
        _print_ast(ast, indent=0)
        return 0
    except JogLangError as e:
        print(f"\n{e}", file=sys.stderr)
        return 1


def _print_ast(node: object, indent: int = 0) -> None:
    """Cetak AST secara rekursif dengan indentasi."""
    prefix = "  " * indent
    name   = type(node).__name__

    if hasattr(node, "__dataclass_fields__"):
        print(f"{prefix}{name}")
        for fname, _ in node.__dataclass_fields__.items():
            if fname in ("line", "column"):
                continue
            val = getattr(node, fname)
            if val is None:
                continue
            elif isinstance(val, list):
                if val:
                    print(f"{prefix}  .{fname}:")
                    for item in val:
                        if hasattr(item, "__dataclass_fields__"):
                            _print_ast(item, indent + 2)
                        elif isinstance(item, tuple):
                            for sub in item:
                                if hasattr(sub, "__dataclass_fields__"):
                                    _print_ast(sub, indent + 2)
                        else:
                            print(f"{prefix}    {item!r}")
            elif hasattr(val, "__dataclass_fields__"):
                print(f"{prefix}  .{fname}:")
                _print_ast(val, indent + 2)
            else:
                print(f"{prefix}  .{fname} = {val!r}")
    else:
        print(f"{prefix}{node!r}")


def _mode_compile(
    source:      str,
    filepath:    str,
    output_dir:  str,
    verbose:     bool,
    no_optimize: bool,
    run:         bool,
) -> int:
    """Mode utama: kompilasi (dan opsional jalankan)."""
    compiler = Compiler(
        verbose=verbose,
        optimize=not no_optimize,
        output_dir=output_dir,
    )

    print(f"  Mengkompilasi: {filepath}")
    result = compiler.compile_source(
        source,
        source_path=filepath,
        save_output=True,
    )

    if not result.success:
        print(f"\n  ✗ GAGAL pada tahap: {result.stage}", file=sys.stderr)
        print(f"  {result.error}", file=sys.stderr)
        return 1

    # Tampilkan hasil sukses
    print(f"  ✓ Berhasil ({result.elapsed_ms:.1f}ms)")
    if result.output_path:
        print(f"  Output  : {result.output_path}")

    if verbose and result.opt_stats:
        print(f"  Optimasi: {result.opt_stats.summary()}")

    if verbose and result.tokens:
        print(f"\n  Token   : {len(result.tokens)}")

    # Tampilkan kode yang dihasilkan
    print()
    print("─" * 60)
    print("  KODE PYTHON YANG DIHASILKAN:")
    print("─" * 60)
    for i, line in enumerate(result.python_code.splitlines(), 1):
        print(f"  {i:3d}│ {line}")
    print("─" * 60)

    # Jalankan jika --run
    if run:
        print()
        print("═" * 60)
        print("  OUTPUT PROGRAM:")
        print("═" * 60)
        try:
            exec(result.python_code, {})
        except Exception as e:
            print(f"  Runtime Error: {e}", file=sys.stderr)
            return 1

    return 0


# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================

def main() -> int:
    """Entry point utama CLI JogLang Compiler."""
    ap     = _build_arg_parser()
    args   = ap.parse_args()

    # Jika tidak ada file → masuk ke Interactive REPL
    if not args.file:
        # Tentukan direktori examples relatif terhadap lokasi main.py / cli.py
        import pathlib
        cli_dir      = pathlib.Path(__file__).parent          # joglang_compiler/
        project_root = cli_dir.parent                         # joglang_project/
        examples_dir = str(project_root / "examples")
        start_repl(
            examples_dir=examples_dir,
            optimize=not args.no_optimize,
        )
        return 0

    # Validasi ekstensi file
    if not args.file.endswith(__extension__):
        print(
            f"  Error: File harus berekstensi '{__extension__}', "
            f"bukan '{os.path.splitext(args.file)[1] or '(tidak ada)'}'",
            file=sys.stderr,
        )
        return 1

    # Baca source file
    try:
        source = read_source_file(args.file)
    except FileNotFoundError:
        print(f"  Error: File tidak ditemukan: '{args.file}'", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"  Error: {e}", file=sys.stderr)
        return 1

    print_banner()
    print("═" * 60)

    # Pilih mode
    if args.tokens:
        return _mode_tokens(source)

    if args.ast:
        return _mode_ast(source)

    return _mode_compile(
        source      = source,
        filepath    = args.file,
        output_dir  = args.output,
        verbose     = args.verbose,
        no_optimize = args.no_optimize,
        run         = args.run,
    )


if __name__ == "__main__":
    sys.exit(main())
