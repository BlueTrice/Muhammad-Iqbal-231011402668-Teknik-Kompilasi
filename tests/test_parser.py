"""
test_parser.py — Unit test untuk JogLang Parser.

Menguji:
  1. Program dasar (wiwiti / rampung)
  2. Deklarasi variabel
  3. Assignment (=, +=, -=, *=, /=)
  4. Ekspresi aritmatika & preseden operator
  5. Ekspresi perbandingan & logika
  6. Print & Input
  7. If / else-if / else
  8. While loop
  9. For loop
 10. Fungsi & return
 11. Break & Continue
 12. Pemanggilan fungsi
 13. Syntax Error yang diharapkan
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from joglang_compiler.lexer import tokenize
from joglang_compiler.parser import parse, Parser
from joglang_compiler.ast_nodes import (
    ProgramNode, VariableDeclarationNode, AssignmentNode,
    PrintNode, InputNode, ReturnNode, BreakNode, ContinueNode,
    BlockNode, IfNode, WhileNode, ForNode,
    FunctionNode, CallNode, ParameterNode,
    BinaryOperationNode, UnaryOperationNode, VariableNode, LiteralNode,
)
from joglang_compiler.errors import SyntaxError_


def compile_parse(source: str) -> ProgramNode:
    """Helper: lex + parse, kembalikan ProgramNode."""
    tokens = tokenize(source)
    return parse(tokens)


def first_stmt(source: str):
    """Helper: ambil statement pertama dari program."""
    prog = compile_parse(source)
    return prog.body[0]


# ===========================================================================

class TestProgramStructure(unittest.TestCase):
    """Test struktur dasar program."""

    def test_empty_program(self):
        prog = compile_parse("wiwiti rampung")
        self.assertIsInstance(prog, ProgramNode)
        self.assertEqual(prog.body, [])

    def test_missing_wiwiti(self):
        with self.assertRaises(SyntaxError_):
            compile_parse("angka x = 1 rampung")

    def test_missing_rampung(self):
        with self.assertRaises(SyntaxError_):
            compile_parse("wiwiti angka x = 1")

    def test_extra_token_after_rampung(self):
        with self.assertRaises(SyntaxError_):
            compile_parse("wiwiti rampung angka x = 1")


class TestVariableDeclaration(unittest.TestCase):
    """Test deklarasi variabel."""

    def test_int_with_value(self):
        node = first_stmt("wiwiti angka umur = 20 rampung")
        self.assertIsInstance(node, VariableDeclarationNode)
        self.assertEqual(node.var_type, "angka")
        self.assertEqual(node.name, "umur")
        self.assertIsInstance(node.initializer, LiteralNode)
        self.assertEqual(node.initializer.value, 20)

    def test_float_declaration(self):
        node = first_stmt("wiwiti pecahan pi = 3.14 rampung")
        self.assertIsInstance(node, VariableDeclarationNode)
        self.assertEqual(node.var_type, "pecahan")
        self.assertAlmostEqual(node.initializer.value, 3.14)

    def test_string_declaration(self):
        node = first_stmt('wiwiti teks nama = "Budi" rampung')
        self.assertIsInstance(node, VariableDeclarationNode)
        self.assertEqual(node.var_type, "teks")
        self.assertEqual(node.initializer.value, "Budi")

    def test_bool_declaration(self):
        node = first_stmt("wiwiti bener_salah aktif = bener rampung")
        self.assertIsInstance(node, VariableDeclarationNode)
        self.assertEqual(node.var_type, "bener_salah")
        self.assertIsInstance(node.initializer, LiteralNode)
        self.assertEqual(node.initializer.value, True)

    def test_null_initializer(self):
        node = first_stmt("wiwiti angka x = kosong rampung")
        self.assertIsInstance(node.initializer, LiteralNode)
        self.assertIsNone(node.initializer.value)

    def test_no_initializer(self):
        node = first_stmt("wiwiti angka x rampung")
        self.assertIsInstance(node, VariableDeclarationNode)
        self.assertIsNone(node.initializer)

    def test_multiple_declarations(self):
        prog = compile_parse("wiwiti angka x = 1 angka y = 2 rampung")
        self.assertEqual(len(prog.body), 2)


class TestAssignment(unittest.TestCase):
    """Test statement assignment."""

    def test_simple_assign(self):
        node = first_stmt("wiwiti angka x = 0 x = 5 rampung")
        # node pertama adalah deklarasi, kedua assignment
        prog = compile_parse("wiwiti angka x = 0 x = 5 rampung")
        asgn = prog.body[1]
        self.assertIsInstance(asgn, AssignmentNode)
        self.assertEqual(asgn.name, "x")
        self.assertEqual(asgn.operator, "=")

    def test_plus_assign(self):
        prog = compile_parse("wiwiti angka x = 0 x += 3 rampung")
        asgn = prog.body[1]
        self.assertEqual(asgn.operator, "+=")

    def test_minus_assign(self):
        prog = compile_parse("wiwiti angka x = 10 x -= 2 rampung")
        self.assertEqual(prog.body[1].operator, "-=")

    def test_star_assign(self):
        prog = compile_parse("wiwiti angka x = 5 x *= 2 rampung")
        self.assertEqual(prog.body[1].operator, "*=")

    def test_slash_assign(self):
        prog = compile_parse("wiwiti angka x = 10 x /= 2 rampung")
        self.assertEqual(prog.body[1].operator, "/=")


class TestExpressions(unittest.TestCase):
    """Test ekspresi dan preseden operator."""

    def _expr(self, expr_src: str) -> VariableDeclarationNode:
        """Helper: parse ekspresi dalam konteks deklarasi."""
        return first_stmt(f"wiwiti angka x = {expr_src} rampung")

    def test_literal_int(self):
        node = self._expr("42")
        self.assertIsInstance(node.initializer, LiteralNode)
        self.assertEqual(node.initializer.value, 42)

    def test_literal_string(self):
        node = first_stmt('wiwiti teks s = "halo" rampung')
        self.assertIsInstance(node.initializer, LiteralNode)
        self.assertEqual(node.initializer.value, "halo")

    def test_binary_add(self):
        node = self._expr("3 + 4")
        op = node.initializer
        self.assertIsInstance(op, BinaryOperationNode)
        self.assertEqual(op.operator, "+")
        self.assertEqual(op.left.value,  3)
        self.assertEqual(op.right.value, 4)

    def test_precedence_mul_over_add(self):
        # 2 + 3 * 4  =>  2 + (3 * 4)
        node = self._expr("2 + 3 * 4")
        op = node.initializer
        self.assertIsInstance(op, BinaryOperationNode)
        self.assertEqual(op.operator, "+")
        self.assertIsInstance(op.right, BinaryOperationNode)
        self.assertEqual(op.right.operator, "*")

    def test_precedence_power(self):
        # 2 ** 3 ** 2  =>  2 ** (3 ** 2)  right-associative
        node = self._expr("2 ** 3 ** 2")
        op = node.initializer
        self.assertEqual(op.operator, "**")
        self.assertIsInstance(op.right, BinaryOperationNode)
        self.assertEqual(op.right.operator, "**")

    def test_unary_minus(self):
        node = self._expr("-5")
        op = node.initializer
        self.assertIsInstance(op, UnaryOperationNode)
        self.assertEqual(op.operator, "-")

    def test_grouped_expression(self):
        # (2 + 3) * 4  =>  mul node dengan left = add
        node = self._expr("(2 + 3) * 4")
        op = node.initializer
        self.assertEqual(op.operator, "*")
        self.assertIsInstance(op.left, BinaryOperationNode)
        self.assertEqual(op.left.operator, "+")

    def test_comparison(self):
        node = self._expr("x > 0")
        op = node.initializer
        self.assertIsInstance(op, BinaryOperationNode)
        self.assertEqual(op.operator, ">")

    def test_logical_and(self):
        node = self._expr("bener lan salah")
        op = node.initializer
        self.assertEqual(op.operator, "lan")

    def test_logical_or(self):
        node = self._expr("bener utawa salah")
        op = node.initializer
        self.assertEqual(op.operator, "utawa")

    def test_logical_not(self):
        node = self._expr("ora bener")
        op = node.initializer
        self.assertIsInstance(op, UnaryOperationNode)
        self.assertEqual(op.operator, "ora")

    def test_variable_reference(self):
        node = self._expr("x")
        self.assertIsInstance(node.initializer, VariableNode)
        self.assertEqual(node.initializer.name, "x")


class TestPrintInput(unittest.TestCase):
    """Test print dan input."""

    def test_print_string(self):
        node = first_stmt('wiwiti tampilna("halo") rampung')
        self.assertIsInstance(node, PrintNode)
        self.assertIsInstance(node.expression, LiteralNode)
        self.assertEqual(node.expression.value, "halo")

    def test_print_expression(self):
        node = first_stmt("wiwiti tampilna(x + 1) rampung")
        self.assertIsInstance(node, PrintNode)
        self.assertIsInstance(node.expression, BinaryOperationNode)

    def test_input_with_prompt(self):
        node = first_stmt('wiwiti teks n = takon("Nama: ") rampung')
        self.assertIsInstance(node, VariableDeclarationNode)
        self.assertIsInstance(node.initializer, InputNode)
        self.assertIsInstance(node.initializer.prompt, LiteralNode)

    def test_input_no_prompt(self):
        node = first_stmt("wiwiti angka n = takon() rampung")
        self.assertIsInstance(node.initializer, InputNode)
        self.assertIsNone(node.initializer.prompt)


class TestIfElse(unittest.TestCase):
    """Test pernyataan if / else-if / else."""

    def test_simple_if(self):
        src = "wiwiti yen x > 0 { tampilna(x) } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node, IfNode)
        self.assertIsNone(node.else_branch)
        self.assertEqual(len(node.elif_branches), 0)

    def test_if_else(self):
        src = "wiwiti yen x > 0 { tampilna(x) } liyane { tampilna(0) } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node, IfNode)
        self.assertIsNotNone(node.else_branch)

    def test_if_elif_else(self):
        src = """wiwiti
            yen x > 0 { tampilna(1) }
            liyane_yen x == 0 { tampilna(0) }
            liyane { tampilna(-1) }
        rampung"""
        node = first_stmt(src)
        self.assertIsInstance(node, IfNode)
        self.assertEqual(len(node.elif_branches), 1)
        self.assertIsNotNone(node.else_branch)

    def test_if_body_is_block(self):
        src = "wiwiti yen bener { angka y = 1 } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node.then_branch, BlockNode)
        self.assertEqual(len(node.then_branch.statements), 1)


class TestWhile(unittest.TestCase):
    """Test while loop."""

    def test_simple_while(self):
        src = "wiwiti nalika i < 10 { tampilna(i) } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node, WhileNode)
        self.assertIsInstance(node.condition, BinaryOperationNode)
        self.assertIsInstance(node.body, BlockNode)

    def test_while_with_break(self):
        src = "wiwiti nalika bener { mandheg } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node.body.statements[0], BreakNode)

    def test_while_with_continue(self):
        src = "wiwiti nalika bener { terusna } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node.body.statements[0], ContinueNode)


class TestFor(unittest.TestCase):
    """Test for loop."""

    def test_simple_for(self):
        src = "wiwiti baleni i = 0; i < 5; i += 1 { tampilna(i) } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node, ForNode)
        self.assertIsInstance(node.init, AssignmentNode)
        self.assertIsInstance(node.condition, BinaryOperationNode)
        self.assertIsInstance(node.update, AssignmentNode)
        self.assertIsInstance(node.body, BlockNode)

    def test_for_with_var_decl_init(self):
        src = "wiwiti baleni angka i = 0; i < 3; i += 1 { tampilna(i) } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node.init, VariableDeclarationNode)

    def test_for_update_operator(self):
        src = "wiwiti baleni i = 0; i < 5; i += 1 { tampilna(i) } rampung"
        node = first_stmt(src)
        self.assertEqual(node.update.operator, "+=")


class TestFunction(unittest.TestCase):
    """Test deklarasi dan pemanggilan fungsi."""

    def test_no_param_function(self):
        src = "wiwiti gawe halo() { tampilna(\"halo\") } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node, FunctionNode)
        self.assertEqual(node.name, "halo")
        self.assertEqual(len(node.params), 0)

    def test_function_with_params(self):
        src = "wiwiti gawe tambah(angka a, angka b) { balekna a + b } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node, FunctionNode)
        self.assertEqual(len(node.params), 2)
        self.assertEqual(node.params[0].name, "a")
        self.assertEqual(node.params[0].param_type, "angka")
        self.assertEqual(node.params[1].name, "b")

    def test_function_body_is_block(self):
        src = "wiwiti gawe tes() { angka x = 1 } rampung"
        node = first_stmt(src)
        self.assertIsInstance(node.body, BlockNode)

    def test_return_with_value(self):
        src = "wiwiti gawe dua() { balekna 2 } rampung"
        func_node = first_stmt(src)
        ret = func_node.body.statements[0]
        self.assertIsInstance(ret, ReturnNode)
        self.assertIsNotNone(ret.value)
        self.assertEqual(ret.value.value, 2)

    def test_return_no_value(self):
        src = "wiwiti gawe kosongkan() { balekna } rampung"
        func_node = first_stmt(src)
        ret = func_node.body.statements[0]
        self.assertIsInstance(ret, ReturnNode)
        self.assertIsNone(ret.value)

    def test_function_call(self):
        src = "wiwiti gawe f() { balekna 1 } angka z = f() rampung"
        prog = compile_parse(src)
        decl = prog.body[1]
        self.assertIsInstance(decl.initializer, CallNode)
        self.assertEqual(decl.initializer.name, "f")

    def test_function_call_with_args(self):
        src = "wiwiti angka r = tambah(3, 4) rampung"
        node = first_stmt(src)
        call = node.initializer
        self.assertIsInstance(call, CallNode)
        self.assertEqual(call.name, "tambah")
        self.assertEqual(len(call.arguments), 2)


class TestSyntaxErrors(unittest.TestCase):
    """Test bahwa syntax error yang diharapkan dilempar."""

    def _assert_syntax_error(self, source: str) -> None:
        with self.assertRaises(SyntaxError_):
            compile_parse(source)

    def test_missing_lparen_print(self):
        self._assert_syntax_error('wiwiti tampilna "halo" rampung')

    def test_missing_rparen_print(self):
        self._assert_syntax_error('wiwiti tampilna("halo" rampung')

    def test_missing_lbrace_if(self):
        self._assert_syntax_error("wiwiti yen x > 0 tampilna(x) rampung")

    def test_missing_rbrace_if(self):
        self._assert_syntax_error("wiwiti yen x > 0 { tampilna(x) rampung")

    def test_invalid_expression(self):
        self._assert_syntax_error("wiwiti angka x = + rampung")

    def test_error_has_location(self):
        """SyntaxError harus menyertakan baris dan kolom."""
        try:
            compile_parse('wiwiti tampilna "halo" rampung')
        except SyntaxError_ as e:
            self.assertGreater(e.line,   0)
            self.assertGreater(e.column, 0)


# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
