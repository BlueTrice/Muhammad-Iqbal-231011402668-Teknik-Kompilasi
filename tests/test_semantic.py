"""
test_semantic.py — Unit test untuk JogLang Semantic Analyzer.

Menguji:
  1.  Deklarasi variabel valid
  2.  Redeklarasi variabel -> SemanticError
  3.  Variabel belum dideklarasikan -> SemanticError
  4.  Assignment tipe kompatibel
  5.  Type mismatch pada deklarasi -> SemanticError
  6.  Type mismatch pada assignment -> SemanticError
  7.  balekna di luar fungsi -> SemanticError
  8.  balekna di dalam fungsi -> OK
  9.  mandheg di luar loop -> SemanticError
  10. mandheg di dalam loop -> OK
  11. terusna di luar loop -> SemanticError
  12. terusna di dalam loop -> OK
  13. Fungsi belum dideklarasikan -> SemanticError
  14. Jumlah argumen tidak sesuai -> SemanticError
  15. Jumlah argumen sesuai -> OK
  16. Panggil variabel sebagai fungsi -> SemanticError
  17. Fungsi sebagai variabel (assign) -> SemanticError
  18. Scope: variabel dari scope luar terlihat di dalam blok
  19. Scope: variabel lokal blok tidak terlihat di luar
  20. Program lengkap valid
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from joglang_compiler.lexer import tokenize
from joglang_compiler.parser import parse
from joglang_compiler.semantic import SemanticAnalyzer, analyze
from joglang_compiler.errors import SemanticError


def run_semantic(source: str) -> None:
    """Helper: lex -> parse -> analyze. Melempar SemanticError jika ada masalah."""
    tokens = tokenize(source)
    ast    = parse(tokens)
    analyze(ast)


def should_pass(source: str) -> None:
    """Pastikan source code lolos analisis semantik."""
    run_semantic(source)


def should_fail(source: str) -> SemanticError:
    """Pastikan source code gagal analisis semantik dan kembalikan error-nya."""
    try:
        run_semantic(source)
        raise AssertionError("Seharusnya melempar SemanticError, tapi tidak.")
    except SemanticError as e:
        return e


# ===========================================================================

class TestVariableDeclaration(unittest.TestCase):
    """Test deklarasi variabel."""

    def test_valid_int_declaration(self):
        should_pass("wiwiti angka x = 10 rampung")

    def test_valid_float_declaration(self):
        should_pass("wiwiti pecahan pi = 3.14 rampung")

    def test_valid_string_declaration(self):
        should_pass('wiwiti teks nama = "Budi" rampung')

    def test_valid_bool_declaration(self):
        should_pass("wiwiti bener_salah aktif = bener rampung")

    def test_valid_declaration_without_init(self):
        should_pass("wiwiti angka x rampung")

    def test_redeclaration_same_scope(self):
        err = should_fail("wiwiti angka x = 1 angka x = 2 rampung")
        self.assertIn("Redeklarasi", str(err))
        self.assertIn("x", str(err))

    def test_redeclaration_function_param_same_scope(self):
        """Parameter tidak boleh dideklarasikan ulang di scope fungsi."""
        err = should_fail("""
        wiwiti
            gawe tes(angka x) {
                angka x = 5
            }
        rampung
        """)
        self.assertIn("Redeklarasi", str(err))

    def test_different_scope_ok(self):
        """Variabel di scope berbeda tidak dianggap redeklarasi."""
        should_pass("""
        wiwiti
            angka x = 1
            yen bener {
                angka y = 2
            }
        rampung
        """)


class TestVariableLookup(unittest.TestCase):
    """Test penggunaan variabel."""

    def test_use_before_declare(self):
        err = should_fail("wiwiti tampilna(x) rampung")
        self.assertIn("belum dideklarasikan", str(err))
        self.assertIn("x", str(err))

    def test_use_after_declare(self):
        should_pass("wiwiti angka x = 5 tampilna(x) rampung")

    def test_outer_scope_visible_in_inner(self):
        """Variabel outer scope bisa digunakan di inner scope."""
        should_pass("""
        wiwiti
            angka total = 0
            yen bener {
                tampilna(total)
            }
        rampung
        """)

    def test_inner_scope_not_visible_outside(self):
        """Variabel yang dideklarasikan dalam if-block tidak bisa diakses di luar."""
        err = should_fail("""
        wiwiti
            yen bener {
                angka dalam = 99
            }
            tampilna(dalam)
        rampung
        """)
        self.assertIn("belum dideklarasikan", str(err))


class TestTypeMismatch(unittest.TestCase):
    """Test type mismatch."""

    def test_int_to_string_mismatch(self):
        err = should_fail('wiwiti teks nama = 42 rampung')
        self.assertIn("mismatch", str(err).lower())

    def test_string_to_int_mismatch(self):
        err = should_fail('wiwiti angka x = "halo" rampung')
        self.assertIn("mismatch", str(err).lower())

    def test_int_to_bool_mismatch(self):
        err = should_fail("wiwiti bener_salah flag = 1 rampung")
        self.assertIn("mismatch", str(err).lower())

    def test_int_float_widening_ok(self):
        """angka dan pecahan kompatibel satu sama lain (numeric widening)."""
        should_pass("wiwiti pecahan x = 5 rampung")
        should_pass("wiwiti angka y = 3.14 rampung")

    def test_assignment_type_mismatch(self):
        err = should_fail("""
        wiwiti
            angka x = 10
            x = "halo"
        rampung
        """)
        self.assertIn("mismatch", str(err).lower())

    def test_assignment_compatible_ok(self):
        should_pass("""
        wiwiti
            angka x = 10
            x = 20
        rampung
        """)


class TestReturnStatement(unittest.TestCase):
    """Test balekna (return)."""

    def test_return_outside_function(self):
        err = should_fail("wiwiti balekna 10 rampung")
        self.assertIn("balekna", str(err))
        self.assertIn("luar fungsi", str(err))

    def test_return_inside_function(self):
        should_pass("""
        wiwiti
            gawe tambah(angka a, angka b) {
                balekna a + b
            }
        rampung
        """)

    def test_return_no_value_in_function(self):
        should_pass("""
        wiwiti
            gawe kosongkan() {
                balekna
            }
        rampung
        """)


class TestBreakContinue(unittest.TestCase):
    """Test mandheg (break) dan terusna (continue)."""

    def test_break_outside_loop(self):
        err = should_fail("wiwiti mandheg rampung")
        self.assertIn("mandheg", str(err))
        self.assertIn("luar loop", str(err))

    def test_continue_outside_loop(self):
        err = should_fail("wiwiti terusna rampung")
        self.assertIn("terusna", str(err))
        self.assertIn("luar loop", str(err))

    def test_break_in_while_ok(self):
        should_pass("""
        wiwiti
            angka i = 0
            nalika i < 10 {
                mandheg
            }
        rampung
        """)

    def test_continue_in_while_ok(self):
        should_pass("""
        wiwiti
            angka i = 0
            nalika i < 10 {
                terusna
            }
        rampung
        """)

    def test_break_in_for_ok(self):
        should_pass("""
        wiwiti
            baleni angka i = 0 ; i < 5 ; i = i + 1 {
                mandheg
            }
        rampung
        """)

    def test_break_in_nested_loop_ok(self):
        should_pass("""
        wiwiti
            angka i = 0
            nalika i < 5 {
                angka j = 0
                nalika j < 5 {
                    mandheg
                }
                i = i + 1
            }
        rampung
        """)

    def test_break_outside_nested_loop(self):
        """Break di luar loop, meski di dalam blok if — tetap error."""
        err = should_fail("""
        wiwiti
            yen bener {
                mandheg
            }
        rampung
        """)
        self.assertIn("mandheg", str(err))


class TestFunctionCall(unittest.TestCase):
    """Test pemanggilan fungsi."""

    def test_call_undeclared_function(self):
        err = should_fail("wiwiti hasil() rampung")
        self.assertIn("belum dideklarasikan", str(err))

    def test_call_wrong_arg_count_too_few(self):
        err = should_fail("""
        wiwiti
            gawe tambah(angka a, angka b) {
                balekna a + b
            }
            angka x = tambah(1)
        rampung
        """)
        self.assertIn("argumen", str(err))

    def test_call_wrong_arg_count_too_many(self):
        err = should_fail("""
        wiwiti
            gawe satu(angka a) {
                balekna a
            }
            angka x = satu(1, 2, 3)
        rampung
        """)
        self.assertIn("argumen", str(err))

    def test_call_correct_arg_count(self):
        should_pass("""
        wiwiti
            gawe tambah(angka a, angka b) {
                balekna a + b
            }
            angka hasil = tambah(3, 4)
        rampung
        """)

    def test_call_no_args_ok(self):
        should_pass("""
        wiwiti
            gawe sapa() {
                tampilna("Halo!")
            }
            sapa()
        rampung
        """)

    def test_call_variable_as_function(self):
        err = should_fail("""
        wiwiti
            angka x = 5
            x()
        rampung
        """)
        self.assertIn("variabel", str(err))
        self.assertIn("fungsi", str(err))

    def test_assign_to_function(self):
        err = should_fail("""
        wiwiti
            gawe hitung() {
                balekna 1
            }
            hitung = 5
        rampung
        """)
        self.assertIn("fungsi", str(err))


class TestLoopSemantics(unittest.TestCase):
    """Test semantik loop."""

    def test_while_valid(self):
        should_pass("""
        wiwiti
            angka i = 0
            nalika i < 10 {
                i = i + 1
            }
        rampung
        """)

    def test_for_valid(self):
        should_pass("""
        wiwiti
            baleni angka i = 0 ; i < 5 ; i = i + 1 {
                tampilna(i)
            }
        rampung
        """)

    def test_for_counter_visible_in_body(self):
        """Variabel inisialisasi for harus tersedia di body."""
        should_pass("""
        wiwiti
            baleni angka n = 1 ; n <= 10 ; n = n + 1 {
                tampilna(n)
            }
        rampung
        """)


class TestIfSemantics(unittest.TestCase):
    """Test semantik percabangan."""

    def test_if_valid(self):
        should_pass("""
        wiwiti
            angka x = 5
            yen x > 0 {
                tampilna("positif")
            }
        rampung
        """)

    def test_if_elif_else_valid(self):
        should_pass("""
        wiwiti
            angka nilai = 75
            yen nilai >= 90 {
                tampilna("A")
            } liyane_yen nilai >= 80 {
                tampilna("B")
            } liyane_yen nilai >= 70 {
                tampilna("C")
            } liyane {
                tampilna("D")
            }
        rampung
        """)


class TestOperatorSemantics(unittest.TestCase):
    """Test semantik operator."""

    def test_not_on_bool_ok(self):
        should_pass("""
        wiwiti
            bener_salah flag = bener
            bener_salah hasil = ora flag
        rampung
        """)

    def test_not_on_non_bool(self):
        """ora pada non-boolean harus error."""
        err = should_fail("""
        wiwiti
            angka x = 5
            bener_salah hasil = ora x
        rampung
        """)
        self.assertIn("ora", str(err))


class TestCompleteProgram(unittest.TestCase):
    """Test program JogLang lengkap."""

    def test_factorial_program(self):
        should_pass("""
        wiwiti
            gawe faktorial(angka n) {
                yen n <= 1 {
                    balekna 1
                }
                balekna n * faktorial(n - 1)
            }
            angka hasil = faktorial(5)
            tampilna(hasil)
        rampung
        """)

    def test_fibonacci_program(self):
        should_pass("""
        wiwiti
            gawe fib(angka n) {
                yen n <= 1 {
                    balekna n
                }
                balekna fib(n - 1) + fib(n - 2)
            }
            tampilna(fib(10))
        rampung
        """)

    def test_counter_program(self):
        should_pass("""
        wiwiti
            angka jumlah = 0
            baleni angka i = 1 ; i <= 100 ; i = i + 1 {
                jumlah = jumlah + i
            }
            tampilna(jumlah)
        rampung
        """)

    def test_grade_checker(self):
        should_pass("""
        wiwiti
            angka nilai = 85
            teks huruf = "F"
            yen nilai >= 90 {
                huruf = "A"
            } liyane_yen nilai >= 80 {
                huruf = "B"
            } liyane_yen nilai >= 70 {
                huruf = "C"
            } liyane {
                huruf = "D"
            }
            tampilna(huruf)
        rampung
        """)


if __name__ == "__main__":
    unittest.main(verbosity=2)
