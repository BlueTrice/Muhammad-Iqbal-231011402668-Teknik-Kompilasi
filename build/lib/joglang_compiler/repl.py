"""
repl.py — Interactive REPL (Read-Eval-Print Loop) untuk JogLang Compiler.

REPL memungkinkan pengguna mengetik source code JogLang secara interaktif
baris demi baris, lalu menjalankannya dengan perintah :run.

Perintah yang tersedia:
    :run    Kompilasi dan jalankan source code yang ada di buffer
    :save   Simpan source code ke file .jog di folder examples/
    :clear  Hapus seluruh isi buffer, nomor baris kembali ke 01
    :new    Buat sesi baru (tanya konfirmasi jika buffer belum disimpan)
    :show   Tampilkan seluruh isi buffer dengan nomor baris
    :help   Tampilkan daftar perintah
    :exit   Keluar dari REPL (tanya konfirmasi jika buffer belum disimpan)

Arsitektur:
    JogLangREPL                     ← kelas utama REPL
      ├── _buffer: list[str]        ← baris-baris source code
      ├── _saved: bool              ← sudah disimpan sejak perubahan terakhir?
      ├── _examples_dir: str        ← direktori untuk :save
      └── _compiler: Compiler       ← pipeline compiler yang sudah ada (TIDAK DIUBAH)

Compiler pipeline yang digunakan saat :run:
    Lexer → Parser → SemanticAnalyzer → Optimizer → CodeGenerator
    (identik dengan mode file — memanggil compiler.compile_source())
"""

from __future__ import annotations

import os
import sys
import tempfile
import traceback
from typing import Optional

from .compiler import Compiler, CompileResult
from . import __version__


# ===========================================================================
# KONSTANTA TAMPILAN
# ===========================================================================

_DIVIDER   = "─" * 52
_SEPARATOR = "═" * 52
_PROMPT    = "JogLang > "

# Warna ANSI (dinonaktifkan otomatis di Windows tanpa dukungan VT)
_USE_COLOR = sys.stdout.isatty() and os.name != "nt"

def _c(code: str, text: str) -> str:
    """Bungkus teks dengan kode warna ANSI jika terminal mendukung."""
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

def _green(t: str)  -> str: return _c("32", t)
def _red(t: str)    -> str: return _c("31", t)
def _cyan(t: str)   -> str: return _c("36", t)
def _yellow(t: str) -> str: return _c("33", t)
def _bold(t: str)   -> str: return _c("1",  t)
def _dim(t: str)    -> str: return _c("2",  t)


# ===========================================================================
# REPL CLASS
# ===========================================================================

class JogLangREPL:
    """
    Interactive REPL untuk JogLang Compiler.

    Penggunaan:
        repl = JogLangREPL(examples_dir="examples")
        repl.run()
    """

    # -----------------------------------------------------------------------
    # Perintah khusus yang dimulai dengan ':'
    # -----------------------------------------------------------------------
    _COMMANDS = {
        ":run",
        ":save",
        ":clear",
        ":new",
        ":show",
        ":help",
        ":exit",
    }

    def __init__(
        self,
        examples_dir: str = "examples",
        optimize:     bool = True,
    ) -> None:
        """
        Args:
            examples_dir: Direktori tempat :save menyimpan file .jog
            optimize    : Aktifkan optimizer saat :run (default True)
        """
        self._buffer:       list[str]         = []   # baris source code
        self._saved:        bool              = True  # True = tidak ada perubahan belum disimpan
        self._examples_dir: str              = examples_dir
        self._compiler:     Compiler          = Compiler(
            verbose=False,
            optimize=optimize,
        )

    # -----------------------------------------------------------------------
    # PUBLIC: entry point
    # -----------------------------------------------------------------------

    def run(self) -> None:
        """Jalankan loop REPL hingga pengguna keluar."""
        self._print_welcome()

        while True:
            try:
                line = self._read_line()
            except (EOFError, KeyboardInterrupt):
                # Ctrl+D atau Ctrl+C → keluar dengan konfirmasi
                print()
                if self._confirm_exit():
                    break
                continue

            # Perintah khusus dimulai dengan ':'
            stripped = line.strip()
            if stripped.startswith(":"):
                should_exit = self._dispatch_command(stripped.lower())
                if should_exit:
                    break
            else:
                # Baris source code biasa → masuk ke buffer
                self._buffer.append(line)
                self._saved = False

    # -----------------------------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------------------------

    def _print_welcome(self) -> None:
        """Tampilkan header selamat datang."""
        print()
        print(_bold(_SEPARATOR))
        print(_bold(f"  JogLang Compiler v{__version__}"))
        print(_bold(  "  Basa Jawa Dialek Yogyakarta"))
        print(_bold(  "  Interactive REPL"))
        print(_bold(_SEPARATOR))
        print()
        print("  Perintah tersedia:")
        self._print_command_list(indent="    ")
        print()
        print(_dim("  Ketik source code JogLang lalu :run untuk menjalankan."))
        print(_dim(f"  Baris input dimulai dengan nomor otomatis."))
        print()
        print(_DIVIDER)
        print()

    def _print_command_list(self, indent: str = "  ") -> None:
        """Cetak tabel perintah singkat."""
        commands = [
            (":run",   "Compile dan jalankan source code"),
            (":save",  "Simpan source code ke file .jog"),
            (":clear", "Hapus seluruh source code"),
            (":new",   "Buat source code baru"),
            (":show",  "Tampilkan source code saat ini"),
            (":help",  "Tampilkan bantuan ini"),
            (":exit",  "Keluar dari REPL"),
        ]
        for cmd, desc in commands:
            print(f"{indent}{_cyan(cmd):<22}  {desc}")

    def _print_source(self) -> None:
        """Tampilkan isi buffer dengan nomor baris."""
        if not self._buffer:
            print(_dim("  (buffer kosong)"))
            return
        for i, line in enumerate(self._buffer, 1):
            num = _dim(f"{i:02d} │ ")
            print(f"  {num}{line}")

    def _next_line_number(self) -> str:
        """Nomor baris berikutnya, diformat dua digit."""
        return f"{len(self._buffer) + 1:02d}"

    # -----------------------------------------------------------------------
    # INPUT
    # -----------------------------------------------------------------------

    def _read_line(self) -> str:
        """
        Baca satu baris dari pengguna.
        Prompt menampilkan nomor baris berikutnya agar terasa seperti editor.
        Perintah ':' ditampilkan dengan prompt khusus.
        """
        num    = _dim(f"{self._next_line_number()} │ ")
        prompt = f"  {num}"
        return input(prompt)

    def _read_input(self, prompt: str) -> str:
        """Baca input konfirmasi/nama dengan prompt sederhana."""
        return input(f"  {prompt}").strip()

    # -----------------------------------------------------------------------
    # COMMAND DISPATCHER
    # -----------------------------------------------------------------------

    def _dispatch_command(self, cmd: str) -> bool:
        """
        Proses perintah ':xxx'.

        Returns:
            True  → REPL harus berhenti (exit)
            False → lanjutkan loop
        """
        if cmd == ":run":
            self._cmd_run()
        elif cmd == ":save":
            self._cmd_save()
        elif cmd == ":clear":
            self._cmd_clear()
        elif cmd == ":new":
            self._cmd_new()
        elif cmd == ":show":
            self._cmd_show()
        elif cmd == ":help":
            self._cmd_help()
        elif cmd == ":exit":
            return self._confirm_exit()
        else:
            print(_yellow(f"  Perintah tidak dikenal: '{cmd}'. Ketik :help untuk bantuan."))
        return False

    # -----------------------------------------------------------------------
    # :run
    # -----------------------------------------------------------------------

    def _cmd_run(self) -> None:
        """
        Kompilasi source code di buffer lalu jalankan.
        Menggunakan pipeline compiler yang sudah ada — tidak ada perubahan
        pada Lexer, Parser, SemanticAnalyzer, Optimizer, CodeGenerator.
        """
        if not self._buffer:
            print(_yellow("  Buffer kosong. Ketik source code terlebih dahulu."))
            return

        source = "\n".join(self._buffer)

        print()
        print(_DIVIDER)

        # ── Kompilasi ────────────────────────────────────────────────────
        result: CompileResult = self._compiler.compile_source(
            source,
            source_path="<repl>",
            save_output=False,
        )

        # Tampilkan status tiap tahap
        self._print_compile_status(result)

        print(_DIVIDER)

        if not result.success:
            # Error sudah ditampilkan di _print_compile_status
            print()
            return

        # ── Jalankan hasil kompilasi ─────────────────────────────────────
        print()
        print(_bold("  Program Output"))
        print(_DIVIDER)
        print()

        try:
            # exec() dengan namespace bersih agar variabel tidak bocor
            # antar sesi :run
            namespace: dict = {}
            exec(compile(result.python_code, "<repl>", "exec"), namespace)  # noqa: S102
        except SystemExit:
            pass
        except Exception as exc:
            print()
            print(_red(f"  [Runtime Error] {exc}"))
            if os.environ.get("JOGLANG_DEBUG"):
                traceback.print_exc()

        print()
        print(_DIVIDER)
        print()

    def _print_compile_status(self, result: CompileResult) -> None:
        """
        Tampilkan status sukses/gagal tiap tahap kompilasi.

        Karena CompileResult.stage menyimpan nama tahap yang gagal,
        kita bisa menentukan mana yang lulus dan mana yang gagal.
        """
        stages = [
            ("Lexical Analysis",  "lexer"),
            ("Parser",            "parser"),
            ("Semantic Analysis", "semantic"),
            ("Optimizer",         "optimizer"),
            ("Code Generation",   "codegen"),
        ]

        # Tentukan tahap mana yang gagal
        failed_stage = result.stage if not result.success else None

        # Tampilkan semua tahap sampai yang gagal
        passed = True
        for label, key in stages:
            if not passed:
                break
            if failed_stage and failed_stage.lower() in (key, label.lower()):
                # Tahap ini yang gagal
                print(f"  {_red('✗')} {label}")
                passed = False
            else:
                print(f"  {_green('✓')} {label}")
                if failed_stage and key == failed_stage:
                    passed = False

        # Jika gagal, tampilkan pesan error
        if not result.success and result.error:
            print()
            print(_red(f"  Error: {result.error}"))

    # -----------------------------------------------------------------------
    # :save
    # -----------------------------------------------------------------------

    def _cmd_save(self) -> None:
        """Simpan source code buffer ke file .jog."""
        if not self._buffer:
            print(_yellow("  Buffer kosong, tidak ada yang disimpan."))
            return

        print()
        nama = self._read_input("Nama file (tanpa .jog): ")
        if not nama:
            print(_yellow("  Nama file tidak boleh kosong."))
            return

        # Sanitasi nama file: hanya alfanumerik, underscore, dash
        nama_bersih = "".join(
            c if (c.isalnum() or c in "_-") else "_"
            for c in nama
        )
        if nama_bersih != nama:
            print(_dim(f"  Nama file disanitasi menjadi: '{nama_bersih}'"))

        os.makedirs(self._examples_dir, exist_ok=True)
        filepath = os.path.join(self._examples_dir, f"{nama_bersih}.jog")

        # Tanya overwrite jika sudah ada
        if os.path.exists(filepath):
            jawab = self._read_input(
                f"  File '{filepath}' sudah ada. Overwrite? [Y/N]: "
            ).upper()
            if jawab != "Y":
                print(_dim("  Penyimpanan dibatalkan."))
                return

        try:
            source = "\n".join(self._buffer)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(source)
            self._saved = True
            print(_green(f"  ✓ Disimpan ke: {filepath}"))
        except OSError as e:
            print(_red(f"  ✗ Gagal menyimpan: {e}"))

        print()

    # -----------------------------------------------------------------------
    # :clear
    # -----------------------------------------------------------------------

    def _cmd_clear(self) -> None:
        """Hapus seluruh buffer, nomor baris kembali ke 01."""
        if not self._buffer:
            print(_dim("  Buffer sudah kosong."))
            return

        if not self._saved:
            jawab = self._read_input(
                "Source code belum disimpan. Tetap hapus? [Y/N]: "
            ).upper()
            if jawab != "Y":
                print(_dim("  Clear dibatalkan."))
                return

        self._buffer.clear()
        self._saved = True
        print(_green("  ✓ Buffer dihapus. Nomor baris kembali ke 01."))
        print()

    # -----------------------------------------------------------------------
    # :new
    # -----------------------------------------------------------------------

    def _cmd_new(self) -> None:
        """
        Buat sesi baru.
        Jika buffer belum disimpan, tanya konfirmasi terlebih dahulu.
        """
        if self._buffer and not self._saved:
            jawab = self._read_input(
                "Source code belum disimpan. Tetap buat source baru? [Y/N]: "
            ).upper()
            if jawab != "Y":
                print(_dim("  Dibatalkan."))
                return

        self._buffer.clear()
        self._saved = True
        print(_green("  ✓ Source baru siap. Nomor baris mulai dari 01."))
        print()

    # -----------------------------------------------------------------------
    # :show
    # -----------------------------------------------------------------------

    def _cmd_show(self) -> None:
        """Tampilkan seluruh source code di buffer."""
        print()
        print(_DIVIDER)
        print(_bold("  Source Code Saat Ini:"))
        print(_DIVIDER)
        self._print_source()
        print(_DIVIDER)
        print()

    # -----------------------------------------------------------------------
    # :help
    # -----------------------------------------------------------------------

    def _cmd_help(self) -> None:
        """Tampilkan daftar perintah."""
        print()
        print(_DIVIDER)
        print(_bold("  Perintah JogLang REPL:"))
        print(_DIVIDER)
        self._print_command_list(indent="    ")
        print(_DIVIDER)
        print()
        print(_dim("  Tips:"))
        print(_dim("    • Ketik source code JogLang baris demi baris"))
        print(_dim("    • Setiap Enter → pindah ke baris berikutnya"))
        print(_dim("    • Perintah dimulai dengan ':' (colon)"))
        print(_dim("    • Ctrl+C / Ctrl+D untuk keluar"))
        print()

    # -----------------------------------------------------------------------
    # Konfirmasi exit
    # -----------------------------------------------------------------------

    def _confirm_exit(self) -> bool:
        """
        Tanya konfirmasi jika buffer belum disimpan.

        Returns:
            True jika pengguna benar-benar ingin keluar.
        """
        if self._buffer and not self._saved:
            print()
            jawab = self._read_input(
                "Source code belum disimpan. Keluar? [Y/N]: "
            ).upper()
            if jawab != "Y":
                print(_dim("  Tetap di REPL."))
                print()
                return False

        print()
        print(_bold("  Matur nuwun sampun nggunakaken JogLang!"))
        print()
        return True


# ===========================================================================
# CONVENIENCE FUNCTION
# ===========================================================================

def start_repl(
    examples_dir: str = "examples",
    optimize:     bool = True,
) -> None:
    """
    Shortcut untuk memulai REPL.

    Args:
        examples_dir: Direktori untuk :save (default 'examples')
        optimize    : Aktifkan optimizer (default True)
    """
    JogLangREPL(examples_dir=examples_dir, optimize=optimize).run()
