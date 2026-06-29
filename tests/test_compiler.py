"""
test_compiler.py — Unit test untuk JogLang Compiler (pipeline lengkap).

Menguji:
  1.  Compile dasar berhasil (CompileResult.success)
  2.  Compile menghasilkan Python code yang benar
  3.  Error lexer terdeteksi di stage Lexer
  4.  Error parser terdeteksi di stage Parser
  5.  Error semantik terdeteksi di stage Semantic Analysis
  6.  Optimizer aktif (opt_stats tersedia)
  7.  Optimizer bisa dinonaktifkan (--no-optimize)
  8.  Output Python bisa dieksekusi (compile_and_run)
  9.  Program variabel: semua tipe data
  10. Program aritmatika: operator dasar + constant folding
  11. Program kondisional: if/elif/else
  12. Program while loop
  13. Program for loop
  14. Program fungsi dan return
  15. Program faktorial rekursif
  16. Program break dan continue
  17. CompileResult.__str__ informatif
  18. File compile: file .jog tidak ada -> error
  19. compile() shortcut function
  20. Optimasi aktif menghasilkan code lebih sederhana
"""

import sys
import os
import io
import contextlib
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from joglang_compiler.compiler import Compiler, compile, compile_file, compile_and_run
from joglang_compiler.errors import LexicalError, SyntaxError_, SemanticError


# ===========================================================================
# HELPERS
# ===========================================================================

def run(source: str, optimize: bool = True) -> str:
    """Kompilasi dan jalankan, kembalikan stdout sebagai string."""
    result = compile(source, optimize=optimize)
    if not result.success:
        raise result.error
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(result.python_code, {})
    return buf.getvalue().strip()


def compile_ok(source: str) -> str:
    """Kompilasi dan kembalikan kode Python. Gagal jika kompilasi error."""
    result = compile(source)
    assert result.success, f"Kompilasi gagal: {result.error}"
    return result.python_code


# ===========================================================================

class TestCompileBasic(unittest.TestCase):
    """Test kompilasi dasar."""

    def test_empty_program_succeeds(self):
        result = compile("wiwiti rampung")
        self.assertTrue(result.success)
        self.assertEqual(result.error, None)

    def test_result_has_python_code(self):
        result = compile('wiwiti tampilna("halo") rampung')
        self.assertTrue(result.success)
        self.assertIn("print", result.python_code)

    def test_result_elapsed_time(self):
        result = compile("wiwiti rampung")
        self.assertGreater(result.elapsed_ms, 0)

    def test_result_str_success(self):
        result = compile("wiwiti rampung")
        s = str(result)
        self.assertIn("OK", s)
        self.assertIn("Kompilasi berhasil", s)

    def test_result_str_failure(self):
        result = compile("wiwiti if x rampung")  # 'if' terlarang
        self.assertFalse(result.success)
        s = str(result)
        self.assertIn("GAGAL", s)


class TestCompileErrors(unittest.TestCase):
    """Test deteksi error di setiap tahap."""

    def test_lexer_error_stage(self):
        result = compile("wiwiti angka x = @ rampung")
        self.assertFalse(result.success)
        self.assertEqual(result.stage, "Lexer")

    def test_forbidden_keyword_stage(self):
        result = compile("wiwiti print(1) rampung")
        self.assertFalse(result.success)
        self.assertEqual(result.stage, "Lexer")

    def test_parser_error_stage(self):
        result = compile('wiwiti tampilna "halo" rampung')  # kurang kurung
        self.assertFalse(result.success)
        self.assertEqual(result.stage, "Parser")

    def test_semantic_error_stage(self):
        result = compile("wiwiti tampilna(x) rampung")  # x belum deklarasi
        self.assertFalse(result.success)
        self.assertEqual(result.stage, "Semantic Analysis")

    def test_error_has_location(self):
        result = compile("wiwiti angka x = @ rampung")
        self.assertFalse(result.success)
        self.assertGreater(result.error.line, 0)


class TestOptimizer(unittest.TestCase):
    """Test integrasi optimizer."""

    def test_optimizer_active_by_default(self):
        result = compile("wiwiti angka x = 5 + 3 rampung")
        self.assertTrue(result.success)
        self.assertIsNotNone(result.opt_stats)

    def test_optimizer_does_constant_fold(self):
        result = compile("wiwiti angka x = 5 + 3 rampung")
        # Setelah fold: x = 8 (bukan x = 5 + 3)
        self.assertIn("8", result.python_code)
        self.assertNotIn("5 + 3", result.python_code)

    def test_optimizer_disable(self):
        result = compile("wiwiti angka x = 5 + 3 rampung", optimize=False)
        self.assertTrue(result.success)
        # Tanpa optimasi, ekspresi tetap asli
        self.assertIn("5", result.python_code)

    def test_opt_stats_recorded(self):
        result = compile("wiwiti angka x = 5 + 3 rampung")
        self.assertGreater(result.opt_stats.total, 0)
        self.assertGreater(result.opt_stats.constant_folds, 0)


class TestCodeOutput(unittest.TestCase):
    """Test kebenaran kode Python yang dihasilkan."""

    def test_print_generates_python_print(self):
        code = compile_ok('wiwiti tampilna("halo") rampung')
        self.assertIn('print("halo")', code)

    def test_var_decl_generates_assignment(self):
        code = compile_ok("wiwiti angka umur = 20 rampung")
        self.assertIn("umur = 20", code)

    def test_if_generates_python_if(self):
        code = compile_ok("wiwiti angka x = 5 yen x > 0 { tampilna(x) } rampung")
        self.assertIn("if", code)
        self.assertIn("print", code)

    def test_if_elif_else_structure(self):
        code = compile_ok("""
        wiwiti
            angka x = 5
            yen x > 10 { tampilna(1) }
            liyane_yen x > 0 { tampilna(2) }
            liyane { tampilna(3) }
        rampung
        """)
        self.assertIn("if", code)
        self.assertIn("elif", code)
        self.assertIn("else", code)

    def test_while_generates_python_while(self):
        code = compile_ok("wiwiti angka i = 0 nalika i < 5 { i = i + 1 } rampung")
        self.assertIn("while i < 5:", code)

    def test_function_generates_def(self):
        code = compile_ok("wiwiti gawe halo() { tampilna(\"halo\") } rampung")
        self.assertIn("def halo():", code)

    def test_return_generates_return(self):
        code = compile_ok("""
        wiwiti
            gawe dua() { balekna 2 }
        rampung
        """)
        self.assertIn("return", code)

    def test_break_generates_break(self):
        code = compile_ok("""
        wiwiti
            angka i = 0
            nalika i < 10 { mandheg }
        rampung
        """)
        self.assertIn("break", code)

    def test_continue_generates_continue(self):
        code = compile_ok("""
        wiwiti
            angka i = 0
            nalika i < 10 { terusna }
        rampung
        """)
        self.assertIn("continue", code)

    def test_joglang_operators_mapped(self):
        code = compile_ok("""
        wiwiti
            bener_salah a = bener
            bener_salah b = salah
            bener_salah c = a lan b
            bener_salah d = a utawa b
            bener_salah e = ora a
        rampung
        """)
        self.assertIn("and", code)
        self.assertIn("or",  code)
        self.assertIn("not", code)
        self.assertNotIn("lan",   code.split("# ")[0] if "# " in code else code)

    def test_true_false_null_mapped(self):
        code = compile_ok("""
        wiwiti
            bener_salah a = bener
            bener_salah b = salah
            angka x = kosong
        rampung
        """)
        self.assertIn("True",  code)
        self.assertIn("False", code)
        self.assertIn("None",  code)

    def test_for_loop_generates_while(self):
        """baleni diterjemahkan ke while Python."""
        code = compile_ok("""
        wiwiti
            baleni angka i = 0 ; i < 5 ; i += 1 {
                tampilna(i)
            }
        rampung
        """)
        self.assertIn("while", code)
        self.assertNotIn("for ", code)  # Tidak ada for Python


class TestRuntime(unittest.TestCase):
    """Test program JogLang yang dikompilasi dan dijalankan."""

    def test_hello_world(self):
        out = run('wiwiti tampilna("Sugeng rawuh!") rampung')
        self.assertEqual(out, "Sugeng rawuh!")

    def test_arithmetic_output(self):
        out = run("wiwiti angka x = 5 + 3 tampilna(x) rampung")
        self.assertEqual(out, "8")

    def test_string_concat_output(self):
        out = run('wiwiti teks s = "halo" + " dunia" tampilna(s) rampung')
        self.assertEqual(out, "halo dunia")

    def test_if_true_branch(self):
        out = run("""
        wiwiti
            angka x = 10
            yen x > 5 {
                tampilna("besar")
            } liyane {
                tampilna("kecil")
            }
        rampung
        """)
        self.assertEqual(out, "besar")

    def test_if_false_branch(self):
        out = run("""
        wiwiti
            angka x = 3
            yen x > 5 {
                tampilna("besar")
            } liyane {
                tampilna("kecil")
            }
        rampung
        """)
        self.assertEqual(out, "kecil")

    def test_while_sum(self):
        out = run("""
        wiwiti
            angka i = 1
            angka jumlah = 0
            nalika i <= 10 {
                jumlah = jumlah + i
                i = i + 1
            }
            tampilna(jumlah)
        rampung
        """)
        self.assertEqual(out, "55")

    def test_for_loop(self):
        out = run("""
        wiwiti
            angka jumlah = 0
            baleni angka i = 1 ; i <= 5 ; i += 1 {
                jumlah = jumlah + i
            }
            tampilna(jumlah)
        rampung
        """)
        self.assertEqual(out, "15")

    def test_function_call(self):
        out = run("""
        wiwiti
            gawe tambah(angka a, angka b) {
                balekna a + b
            }
            tampilna(tambah(3, 4))
        rampung
        """)
        self.assertEqual(out, "7")

    def test_factorial(self):
        out = run("""
        wiwiti
            gawe faktorial(angka n) {
                yen n <= 1 { balekna 1 }
                balekna n * faktorial(n - 1)
            }
            tampilna(faktorial(5))
        rampung
        """)
        self.assertEqual(out, "120")

    def test_break_in_loop(self):
        out = run("""
        wiwiti
            angka i = 0
            nalika bener {
                i = i + 1
                yen i >= 3 { mandheg }
            }
            tampilna(i)
        rampung
        """)
        self.assertEqual(out, "3")

    def test_continue_in_for_loop(self):
        """For loop dengan continue: cetak hanya bilangan ganjil."""
        out = run("""
        wiwiti
            baleni angka i = 1 ; i <= 5 ; i += 1 {
                yen i % 2 == 0 { terusna }
                tampilna(i)
            }
        rampung
        """)
        self.assertEqual(out, "1\n3\n5")

    def test_multiple_functions(self):
        out = run("""
        wiwiti
            gawe kuadrat(angka n) {
                balekna n * n
            }
            gawe kubus(angka n) {
                balekna n * n * n
            }
            tampilna(kuadrat(4))
            tampilna(kubus(3))
        rampung
        """)
        self.assertEqual(out, "16\n27")

    def test_grade_checker(self):
        out = run("""
        wiwiti
            angka nilai = 85
            teks huruf  = "F"
            yen nilai >= 90 { huruf = "A" }
            liyane_yen nilai >= 80 { huruf = "B" }
            liyane_yen nilai >= 70 { huruf = "C" }
            liyane { huruf = "D" }
            tampilna(huruf)
        rampung
        """)
        self.assertEqual(out, "B")

    def test_nested_function_calls(self):
        out = run("""
        wiwiti
            gawe tambah(angka a, angka b) { balekna a + b }
            gawe kali(angka a, angka b) { balekna a * b }
            tampilna(tambah(kali(2, 3), kali(4, 5)))
        rampung
        """)
        self.assertEqual(out, "26")

    def test_boolean_logic(self):
        out = run("""
        wiwiti
            bener_salah a = bener
            bener_salah b = salah
            bener_salah c = a lan b
            bener_salah d = a utawa b
            tampilna(c)
            tampilna(d)
        rampung
        """)
        self.assertEqual(out, "False\nTrue")


class TestCompileFile(unittest.TestCase):
    """Test kompilasi dari file."""

    def test_nonexistent_file(self):
        result = compile_file("tidak_ada.jog")
        self.assertFalse(result.success)

    def test_wrong_extension(self):
        result = compile_file("program.py")
        self.assertFalse(result.success)


class TestVerboseMode(unittest.TestCase):
    """Test mode verbose."""

    def test_verbose_saves_tokens(self):
        c = Compiler(verbose=True)
        r = c.compile_source("wiwiti angka x = 5 rampung")
        self.assertTrue(r.success)
        self.assertGreater(len(r.tokens), 0)

    def test_verbose_saves_ast(self):
        c = Compiler(verbose=True)
        r = c.compile_source("wiwiti angka x = 5 rampung")
        self.assertIsNotNone(r.ast)

    def test_non_verbose_no_tokens(self):
        c = Compiler(verbose=False)
        r = c.compile_source("wiwiti angka x = 5 rampung")
        self.assertEqual(r.tokens, [])


# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
