"""
utils.py — Fungsi utilitas umum untuk JogLang Compiler.
"""

from __future__ import annotations
import os


def read_source_file(filepath: str) -> str:
    """
    Membaca file source JogLang (.jog).

    Args:
        filepath: Path ke file .jog

    Returns:
        Isi file sebagai string

    Raises:
        FileNotFoundError: Jika file tidak ditemukan
        ValueError: Jika ekstensi file bukan .jog
    """
    if not filepath.endswith(".jog"):
        raise ValueError(f"File harus berekstensi .jog, bukan: '{filepath}'")
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File tidak ditemukan: '{filepath}'")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_output_file(filepath: str, content: str) -> None:
    """
    Menulis hasil code generation ke file output.

    Args:
        filepath: Path tujuan output
        content : Isi file yang akan ditulis
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def get_output_path(source_path: str, output_dir: str = "output") -> str:
    """
    Menghasilkan path output berdasarkan path source.

    Contoh: examples/hello.jog -> output/hello.py

    Args:
        source_path: Path file .jog
        output_dir : Direktori output (default: 'output')

    Returns:
        Path file output .py
    """
    basename = os.path.basename(source_path)          # hello.jog
    stem     = os.path.splitext(basename)[0]           # hello
    return os.path.join(output_dir, f"{stem}.py")


def print_banner() -> None:
    """Menampilkan banner JogLang Compiler."""
    banner = r"""
     _            _                       
    | | ___   __ | |    __ _ _ __   __ _ 
 _  | |/ _ \ / _` |   / _` | '_ \ / _` |
| |_| | (_) | (_| |  | (_| | | | | (_| |
 \___/ \___/ \__, |   \__,_|_| |_|\__, |
             |___/  COMPILER v1.0  |___/ 

  Basa Jawa Dialek Yogyakarta
    """
    print(banner)
