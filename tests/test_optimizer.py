"""
test_optimizer.py — Unit test untuk JogLang Code Optimizer.

Menguji:
  1.  Constant Folding — aritmatika (+, -, *, /, %, **)
  2.  Constant Folding — perbandingan (==, !=, <, >, <=, >=)
  3.  Constant Folding — string concatenation
  4.  Constant Folding — logika (lan, utawa)
  5.  Constant Folding — unary (- dan ora)
  6.  Identity Optimization — x+0, x*1, x*0, x/1, x**1, x**0
  7.  Strength Reduction — x**2 -> x*x
  8.  Dead Code Elimination — yen bener / yen salah
  9.  Dead Code Elimination — nalika salah
  10. Boolean short-circuit — bener lan x, salah utawa x, dll.
  11. Nested constant folding
  12. Statistik optimasi
  13. Node tidak terpengaruh tetap utuh
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from joglang_compiler.lexer import tokenize
from joglang_compiler.parser import parse
from joglang_compiler.optimizer import Optimizer, optimize
from joglang_compiler.ast_nodes import (
    LiteralNode, BinaryOperationNode, UnaryOperationNode,
    VariableNode, IfNode, WhileNode, BlockNode, ProgramNode,
)


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def make_prog(source: str) -> ProgramNode:
    """Lex + parse source code JogLang."""
    return parse(tokenize(source))


def run_opt(source: str) -> ProgramNode:
    """Lex + parse + optimize, kembalikan AST teroptimasi."""
    ast, _ = optimize(make_prog(source))
    return ast


def first_stmt(source: str):
    """Optimasi dan ambil statement pertama."""
    return run_opt(source).body[0]


def first_expr(source: str):
    """Optimasi dan ambil ekspresi dari statement terakhir (VariableDeclaration)."""
    prog = run_opt(source)
    # Ambil statement VariableDeclarationNode terakhir
    from joglang_compiler.ast_nodes import VariableDeclarationNode
    for stmt in reversed(prog.body):
        if isinstance(stmt, VariableDeclarationNode):
            return stmt.initializer
    return prog.body[-1].initializer if prog.body else None


# ===========================================================================
# TEST CLASSES
# ===========================================================================

class TestConstantFolding(unittest.TestCase):
    """Test Constant Folding."""

    # -----------------------------------------------------------------------
    # Aritmatika
    # -----------------------------------------------------------------------

    def test_fold_addition(self):
        """5 + 3 -> 8"""
        expr = first_expr("wiwiti angka x = 5 + 3 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 8)

    def test_fold_subtraction(self):
        """10 - 4 -> 6"""
        expr = first_expr("wiwiti angka x = 10 - 4 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 6)

    def test_fold_multiplication(self):
        """10 * 2 -> 20"""
        expr = first_expr("wiwiti angka x = 10 * 2 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 20)

    def test_fold_division(self):
        """9 / 3 -> 3"""
        expr = first_expr("wiwiti angka x = 9 / 3 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 3)

    def test_fold_modulo(self):
        """10 % 3 -> 1"""
        expr = first_expr("wiwiti angka x = 10 % 3 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 1)

    def test_fold_power(self):
        """2 ** 3 -> 8"""
        expr = first_expr("wiwiti angka x = 2 ** 3 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 8)

    def test_fold_float_addition(self):
        """1.5 + 2.5 -> 4.0"""
        expr = first_expr("wiwiti pecahan x = 1.5 + 2.5 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertAlmostEqual(expr.value, 4.0)

    def test_fold_mixed_numeric(self):
        """3 + 1.5 -> 4.5"""
        expr = first_expr("wiwiti pecahan x = 3 + 1.5 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertAlmostEqual(expr.value, 4.5)

    # -----------------------------------------------------------------------
    # Perbandingan
    # -----------------------------------------------------------------------

    def test_fold_eq_true(self):
        """5 == 5 -> bener"""
        expr = first_expr("wiwiti bener_salah x = 5 == 5 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertTrue(expr.value)

    def test_fold_eq_false(self):
        """5 == 6 -> salah"""
        expr = first_expr("wiwiti bener_salah x = 5 == 6 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertFalse(expr.value)

    def test_fold_lt(self):
        """3 < 5 -> bener"""
        expr = first_expr("wiwiti bener_salah x = 3 < 5 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertTrue(expr.value)

    def test_fold_gte(self):
        """5 >= 5 -> bener"""
        expr = first_expr("wiwiti bener_salah x = 5 >= 5 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertTrue(expr.value)

    # -----------------------------------------------------------------------
    # String
    # -----------------------------------------------------------------------

    def test_fold_string_concat(self):
        """\"halo\" + \" dunia\" -> \"halo dunia\" """
        expr = first_expr('wiwiti teks x = "halo" + " dunia" rampung')
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, "halo dunia")

    # -----------------------------------------------------------------------
    # Logika
    # -----------------------------------------------------------------------

    def test_fold_land_both_true(self):
        """bener lan bener -> bener"""
        expr = first_expr("wiwiti bener_salah x = bener lan bener rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertTrue(expr.value)

    def test_fold_land_false(self):
        """bener lan salah -> salah"""
        expr = first_expr("wiwiti bener_salah x = bener lan salah rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertFalse(expr.value)

    def test_fold_or_true(self):
        """salah utawa bener -> bener"""
        expr = first_expr("wiwiti bener_salah x = salah utawa bener rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertTrue(expr.value)

    # -----------------------------------------------------------------------
    # Unary
    # -----------------------------------------------------------------------

    def test_fold_unary_minus(self):
        """-5 -> LiteralNode(-5)"""
        expr = first_expr("wiwiti angka x = -5 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, -5)

    def test_fold_unary_not_true(self):
        """ora bener -> salah"""
        expr = first_expr("wiwiti bener_salah x = ora bener rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertFalse(expr.value)

    def test_fold_unary_not_false(self):
        """ora salah -> bener"""
        expr = first_expr("wiwiti bener_salah x = ora salah rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertTrue(expr.value)


class TestIdentityOptimization(unittest.TestCase):
    """Test Identity Optimization."""

    def test_add_zero_right(self):
        """x + 0 -> x"""
        expr = first_expr("wiwiti angka x = 0 angka y = x + 0 rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "x")

    def test_add_zero_left(self):
        """0 + x -> x"""
        expr = first_expr("wiwiti angka x = 0 angka y = 0 + x rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "x")

    def test_sub_zero(self):
        """x - 0 -> x"""
        expr = first_expr("wiwiti angka x = 5 angka y = x - 0 rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "x")

    def test_mul_one_right(self):
        """x * 1 -> x"""
        expr = first_expr("wiwiti angka x = 5 angka y = x * 1 rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "x")

    def test_mul_one_left(self):
        """1 * x -> x"""
        expr = first_expr("wiwiti angka x = 5 angka y = 1 * x rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "x")

    def test_mul_zero_right(self):
        """x * 0 -> 0"""
        expr = first_expr("wiwiti angka x = 5 angka y = x * 0 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 0)

    def test_mul_zero_left(self):
        """0 * x -> 0"""
        expr = first_expr("wiwiti angka x = 5 angka y = 0 * x rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 0)

    def test_div_one(self):
        """x / 1 -> x"""
        expr = first_expr("wiwiti angka x = 5 angka y = x / 1 rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "x")

    def test_power_one(self):
        """x ** 1 -> x"""
        expr = first_expr("wiwiti angka x = 5 angka y = x ** 1 rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "x")

    def test_power_zero(self):
        """x ** 0 -> 1"""
        expr = first_expr("wiwiti angka x = 5 angka y = x ** 0 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 1)


class TestStrengthReduction(unittest.TestCase):
    """Test Strength Reduction."""

    def test_power_2_to_multiply(self):
        """x ** 2 -> x * x"""
        expr = first_expr("wiwiti angka x = 5 angka y = x ** 2 rampung")
        self.assertIsInstance(expr, BinaryOperationNode)
        self.assertEqual(expr.operator, "*")
        self.assertIsInstance(expr.left, VariableNode)
        self.assertIsInstance(expr.right, VariableNode)
        self.assertEqual(expr.left.name, "x")
        self.assertEqual(expr.right.name, "x")


class TestDeadCodeElimination(unittest.TestCase):
    """Test Dead Code Elimination."""

    def test_if_true_eliminates_else(self):
        """yen bener { A } liyane { B } -> A (BlockNode)"""
        prog = run_opt("""
        wiwiti
            yen bener {
                angka x = 1
            } liyane {
                angka y = 999
            }
        rampung
        """)
        # Seharusnya hanya 1 statement (BlockNode dari then)
        self.assertEqual(len(prog.body), 1)
        stmt = prog.body[0]
        self.assertIsInstance(stmt, BlockNode)
        # Tidak boleh ada y = 999
        self.assertNotIn("y", [
            getattr(s, "name", None) for s in stmt.statements
        ])

    def test_if_false_eliminates_then(self):
        """yen salah { A } liyane { B } -> B"""
        prog = run_opt("""
        wiwiti
            yen salah {
                angka x = 999
            } liyane {
                angka y = 2
            }
        rampung
        """)
        self.assertEqual(len(prog.body), 1)
        stmt = prog.body[0]
        self.assertIsInstance(stmt, BlockNode)
        names = [getattr(s, "name", None) for s in stmt.statements]
        self.assertIn("y", names)
        self.assertNotIn("x", names)

    def test_if_false_no_else_removed(self):
        """yen salah { A } (tanpa else) -> dihapus seluruhnya"""
        prog = run_opt("""
        wiwiti
            yen salah {
                angka x = 999
            }
        rampung
        """)
        self.assertEqual(len(prog.body), 0)

    def test_while_false_removed(self):
        """nalika salah { } -> dihapus"""
        prog = run_opt("""
        wiwiti
            nalika salah {
                angka x = 1
            }
        rampung
        """)
        self.assertEqual(len(prog.body), 0)

    def test_if_with_variable_condition_kept(self):
        """Kondisi variabel — jangan dihapus."""
        prog = run_opt("""
        wiwiti
            bener_salah flag = bener
            yen flag {
                angka x = 1
            }
        rampung
        """)
        # 2 statement: deklarasi flag + if
        self.assertEqual(len(prog.body), 2)
        self.assertIsInstance(prog.body[1], IfNode)


class TestBooleanShortCircuit(unittest.TestCase):
    """Test Boolean Short-Circuit Optimization."""

    def test_true_and_x_gives_x(self):
        """bener lan x -> x"""
        expr = first_expr("wiwiti bener_salah f = bener bener_salah y = bener lan f rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "f")

    def test_false_and_x_gives_false(self):
        """salah lan x -> salah"""
        expr = first_expr("wiwiti bener_salah f = bener bener_salah y = salah lan f rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertFalse(expr.value)

    def test_true_or_x_gives_true(self):
        """bener utawa x -> bener"""
        expr = first_expr("wiwiti bener_salah f = bener bener_salah y = bener utawa f rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertTrue(expr.value)

    def test_false_or_x_gives_x(self):
        """salah utawa x -> x"""
        expr = first_expr("wiwiti bener_salah f = bener bener_salah y = salah utawa f rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "f")


class TestNestedConstantFolding(unittest.TestCase):
    """Test constant folding bertingkat."""

    def test_nested_arithmetic(self):
        """(2 + 3) * (4 - 1) -> 15"""
        expr = first_expr("wiwiti angka x = (2 + 3) * (4 - 1) rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 15)

    def test_deeply_nested(self):
        """1 + 2 + 3 + 4 -> 10"""
        expr = first_expr("wiwiti angka x = 1 + 2 + 3 + 4 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 10)

    def test_mixed_nested(self):
        """2 ** 3 + 4 * 2 -> 16"""
        expr = first_expr("wiwiti angka x = 2 ** 3 + 4 * 2 rampung")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 16)


class TestOptimizationStats(unittest.TestCase):
    """Test statistik optimasi."""

    def test_stats_constant_folds(self):
        _, stats = optimize(make_prog("wiwiti angka x = 5 + 3 rampung"))
        self.assertGreater(stats.constant_folds, 0)
        self.assertGreater(stats.total, 0)

    def test_stats_identity(self):
        _, stats = optimize(make_prog("wiwiti angka x = 5 angka y = x + 0 rampung"))
        self.assertGreater(stats.identity_opts, 0)

    def test_stats_dead_code(self):
        _, stats = optimize(make_prog("""
        wiwiti
            yen salah { angka x = 1 }
        rampung
        """))
        self.assertGreater(stats.dead_code_removed, 0)

    def test_stats_summary_string(self):
        _, stats = optimize(make_prog("wiwiti angka x = 1 + 1 rampung"))
        summary = stats.summary()
        self.assertIn("Optimasi selesai", summary)
        self.assertIn("constant fold", summary)

    def test_no_opts_on_variable_only(self):
        """Program tanpa literal — tidak ada constant folding."""
        _, stats = optimize(make_prog("wiwiti angka x = 5 tampilna(x) rampung"))
        # fold minimal (mungkin ada -5 unary), tapi dead code = 0
        self.assertEqual(stats.dead_code_removed, 0)


class TestNoUnwantedChanges(unittest.TestCase):
    """Pastikan optimizer tidak mengubah hal yang tidak perlu."""

    def test_variable_reference_unchanged(self):
        """Referensi variabel tidak diubah."""
        expr = first_expr("wiwiti angka a = 5 angka b = a rampung")
        self.assertIsInstance(expr, VariableNode)
        self.assertEqual(expr.name, "a")

    def test_function_call_unchanged(self):
        """Pemanggilan fungsi tidak di-fold."""
        stmt = run_opt("""
        wiwiti
            gawe hitung() { balekna 42 }
            angka x = hitung()
        rampung
        """).body[1]
        # Inisialisasi x adalah CallNode
        from joglang_compiler.ast_nodes import CallNode
        self.assertIsInstance(stmt.initializer, CallNode)

    def test_complex_program_structure_intact(self):
        """Struktur program kompleks tetap utuh setelah optimasi."""
        prog = run_opt("""
        wiwiti
            gawe tambah(angka a, angka b) {
                balekna a + b
            }
            angka hasil = tambah(3, 4)
            tampilna(hasil)
        rampung
        """)
        self.assertEqual(len(prog.body), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
