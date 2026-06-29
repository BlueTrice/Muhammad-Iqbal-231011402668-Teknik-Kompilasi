"""
test_lexer.py — Unit test untuk JogLang Lexer.

Menguji:
  1. Tokenisasi keyword
  2. Tokenisasi literal (int, float, string, bool, null)
  3. Tokenisasi operator
  4. Tokenisasi delimiter
  5. Tracking baris & kolom
  6. Keyword terlarang -> LexicalError
  7. Karakter ilegal -> LexicalError
  8. Komentar diabaikan
  9. Program JogLang sederhana (end-to-end)
"""

import sys
import os
import unittest

# Tambahkan root project ke path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from joglang_compiler.lexer import Lexer, tokenize
from joglang_compiler.token import TokenType, Token
from joglang_compiler.errors import LexicalError


def lex(source: str) -> list[Token]:
    """Helper: tokenisasi dan kembalikan token (tanpa EOF)."""
    tokens = tokenize(source)
    return [t for t in tokens if t.type != TokenType.EOF]


def types(tokens: list[Token]) -> list[TokenType]:
    """Helper: ambil hanya tipe token."""
    return [t.type for t in tokens]


def lexemes(tokens: list[Token]) -> list[str]:
    """Helper: ambil hanya lexeme token."""
    return [t.lexeme for t in tokens]


# ===========================================================================

class TestKeywords(unittest.TestCase):
    """Test tokenisasi semua keyword JogLang."""

    def test_program_delimiters(self):
        tokens = lex("wiwiti rampung")
        self.assertEqual(types(tokens), [TokenType.WIWITI, TokenType.RAMPUNG])

    def test_function_keyword(self):
        tokens = lex("gawe")
        self.assertEqual(tokens[0].type, TokenType.GAWE)

    def test_return_keyword(self):
        tokens = lex("balekna")
        self.assertEqual(tokens[0].type, TokenType.BALEKNA)

    def test_datatypes(self):
        src = "angka pecahan teks bener_salah"
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.DATATYPE_INT,
            TokenType.DATATYPE_FLOAT,
            TokenType.DATATYPE_STR,
            TokenType.DATATYPE_BOOL,
        ])

    def test_control_flow(self):
        src = "yen liyane_yen liyane nalika baleni mandheg terusna"
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.YEN,
            TokenType.LIYANE_YEN,
            TokenType.LIYANE,
            TokenType.NALIKA,
            TokenType.BALENI,
            TokenType.MANDHEG,
            TokenType.TERUSNA,
        ])

    def test_io_keywords(self):
        src = "tampilna takon"
        toks = lex(src)
        self.assertEqual(types(toks), [TokenType.TAMPILNA, TokenType.TAKON])

    def test_boolean_literals(self):
        src = "bener salah"
        toks = lex(src)
        self.assertEqual(types(toks), [TokenType.TRUE, TokenType.FALSE])
        self.assertEqual(toks[0].value, True)
        self.assertEqual(toks[1].value, False)

    def test_null_literal(self):
        tokens = lex("kosong")
        self.assertEqual(tokens[0].type, TokenType.NULL)
        self.assertIsNone(tokens[0].value)

    def test_logic_operators(self):
        src = "lan utawa ora"
        toks = lex(src)
        self.assertEqual(types(toks), [TokenType.LAN, TokenType.UTAWA, TokenType.ORA])

    def test_liyane_yen_before_liyane(self):
        """liyane_yen harus tidak terpecah menjadi liyane + identifier."""
        tokens = lex("liyane_yen")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.LIYANE_YEN)

    def test_bener_salah_not_split(self):
        """bener_salah harus satu token DATATYPE_BOOL, bukan bener + salah."""
        tokens = lex("bener_salah")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.DATATYPE_BOOL)


class TestLiterals(unittest.TestCase):
    """Test tokenisasi nilai literal."""

    def test_integer(self):
        tokens = lex("42")
        self.assertEqual(tokens[0].type,  TokenType.INT_LIT)
        self.assertEqual(tokens[0].value, 42)

    def test_integer_zero(self):
        tokens = lex("0")
        self.assertEqual(tokens[0].value, 0)

    def test_float(self):
        tokens = lex("3.14")
        self.assertEqual(tokens[0].type,  TokenType.FLOAT_LIT)
        self.assertAlmostEqual(tokens[0].value, 3.14)

    def test_float_not_split(self):
        """3.14 harus satu token FLOAT, bukan INT + DOT + INT."""
        tokens = lex("3.14")
        self.assertEqual(len(tokens), 1)

    def test_string_double_quote(self):
        tokens = lex('"halo dunia"')
        self.assertEqual(tokens[0].type,  TokenType.STRING_LIT)
        self.assertEqual(tokens[0].value, "halo dunia")

    def test_string_single_quote(self):
        tokens = lex("'yogyakarta'")
        self.assertEqual(tokens[0].type,  TokenType.STRING_LIT)
        self.assertEqual(tokens[0].value, "yogyakarta")

    def test_string_empty(self):
        tokens = lex('""')
        self.assertEqual(tokens[0].value, "")

    def test_multiple_literals(self):
        src = "10 3.5 \"teks\""
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.INT_LIT,
            TokenType.FLOAT_LIT,
            TokenType.STRING_LIT,
        ])
        self.assertEqual(toks[0].value, 10)
        self.assertAlmostEqual(toks[1].value, 3.5)
        self.assertEqual(toks[2].value, "teks")


class TestOperators(unittest.TestCase):
    """Test tokenisasi operator."""

    def test_arithmetic(self):
        src = "+ - * / % **"
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
            TokenType.SLASH, TokenType.PERCENT, TokenType.POWER,
        ])

    def test_comparison(self):
        src = "== != < > <= >="
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.EQ, TokenType.NEQ, TokenType.LT,
            TokenType.GT, TokenType.LTE, TokenType.GTE,
        ])

    def test_assignment(self):
        src = "= += -= *= /="
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
            TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN,
        ])

    def test_power_not_two_stars(self):
        """** harus token POWER, bukan dua STAR."""
        tokens = lex("**")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.POWER)

    def test_lte_not_lt_assign(self):
        """<= harus LTE, bukan LT + ASSIGN."""
        tokens = lex("<=")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.LTE)


class TestDelimiters(unittest.TestCase):
    """Test tokenisasi delimiter."""

    def test_all_delimiters(self):
        src = "( ) { } [ ] ; : , ."
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.LPAREN, TokenType.RPAREN,
            TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET,
            TokenType.SEMICOLON, TokenType.COLON,
            TokenType.COMMA, TokenType.DOT,
        ])


class TestPositionTracking(unittest.TestCase):
    """Test akurasi baris dan kolom."""

    def test_single_line_columns(self):
        tokens = lex("angka x = 5")
        self.assertEqual(tokens[0].line,   1)
        self.assertEqual(tokens[0].column, 1)  # 'angka'
        self.assertEqual(tokens[1].column, 7)  # 'x'
        self.assertEqual(tokens[2].column, 9)  # '='
        self.assertEqual(tokens[3].column, 11) # '5'

    def test_multiline(self):
        src = "angka x = 1\nangka y = 2"
        tokens = lex(src)
        # token 'angka' baris 2
        tok_y_line = [t for t in tokens if t.lexeme == "y"][0]
        self.assertEqual(tok_y_line.line, 2)


class TestComments(unittest.TestCase):
    """Test komentar diabaikan."""

    def test_single_line_comment(self):
        src = "// ini komentar\nangka x = 5"
        tokens = lex(src)
        # tidak boleh ada token COMMENT
        for t in tokens:
            self.assertNotEqual(t.type, TokenType.COMMENT)
        self.assertEqual(tokens[0].type,   TokenType.DATATYPE_INT)
        self.assertEqual(tokens[0].line,   2)

    def test_block_comment(self):
        src = "/* komentar\nblok */ angka z = 10"
        tokens = lex(src)
        self.assertEqual(tokens[0].type, TokenType.DATATYPE_INT)

    def test_inline_comment(self):
        src = "angka a = 1 // komentar di sini"
        tokens = lex(src)
        tps = types(tokens)
        self.assertNotIn(TokenType.COMMENT, tps)
        self.assertEqual(len(tokens), 4)  # angka, a, =, 1


class TestForbiddenKeywords(unittest.TestCase):
    """Test bahwa keyword bahasa lain ditolak."""

    def _assert_forbidden(self, keyword: str) -> None:
        with self.assertRaises(LexicalError) as ctx:
            tokenize(keyword)
        self.assertIn(keyword, str(ctx.exception))

    def test_python_print(self):
        self._assert_forbidden("print")

    def test_python_if(self):
        self._assert_forbidden("if")

    def test_python_return(self):
        self._assert_forbidden("return")

    def test_python_while(self):
        self._assert_forbidden("while")

    def test_python_for(self):
        self._assert_forbidden("for")

    def test_python_def(self):
        self._assert_forbidden("def")

    def test_python_true(self):
        self._assert_forbidden("True")

    def test_java_system(self):
        self._assert_forbidden("System")

    def test_cpp_cout(self):
        self._assert_forbidden("cout")

    def test_csharp_console(self):
        self._assert_forbidden("Console")

    def test_error_has_location(self):
        """Error harus menyertakan baris dan kolom."""
        source = "angka x = print"  # 'print' ada di posisi tertentu
        with self.assertRaises(LexicalError) as ctx:
            tokenize(source)
        err = ctx.exception
        self.assertGreater(err.line,   0)
        self.assertGreater(err.column, 0)
        self.assertIn("Baris", str(err))
        self.assertIn("Kolom", str(err))


class TestIllegalCharacters(unittest.TestCase):
    """Test karakter ilegal menghasilkan LexicalError."""

    def test_at_sign(self):
        with self.assertRaises(LexicalError):
            tokenize("angka x = @5")

    def test_hash(self):
        with self.assertRaises(LexicalError):
            tokenize("# ini bukan komentar JogLang")

    def test_dollar(self):
        with self.assertRaises(LexicalError):
            tokenize("$x = 5")

    def test_backslash(self):
        with self.assertRaises(LexicalError):
            tokenize("angka x = 5 \\ 2")


class TestEndToEnd(unittest.TestCase):
    """Test program JogLang sederhana secara keseluruhan."""

    def test_variable_declaration(self):
        src = "angka umur = 20"
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.DATATYPE_INT,
            TokenType.IDENTIFIER,
            TokenType.ASSIGN,
            TokenType.INT_LIT,
        ])
        self.assertEqual(toks[1].lexeme, "umur")
        self.assertEqual(toks[3].value,  20)

    def test_print_statement(self):
        src = 'tampilna("Sugeng rawuh!")'
        toks = lex(src)
        self.assertEqual(types(toks), [
            TokenType.TAMPILNA,
            TokenType.LPAREN,
            TokenType.STRING_LIT,
            TokenType.RPAREN,
        ])

    def test_if_else(self):
        src = "yen x > 0 { tampilna(x) } liyane { tampilna(0) }"
        toks = lex(src)
        tps  = types(toks)
        self.assertIn(TokenType.YEN,     tps)
        self.assertIn(TokenType.LIYANE,  tps)
        self.assertIn(TokenType.TAMPILNA, tps)

    def test_full_mini_program(self):
        src = """
wiwiti
    angka nilai = 100
    teks nama = "Budi"
    tampilna(nama)
    tampilna(nilai)
rampung
"""
        toks = lex(src)
        tps  = types(toks)
        self.assertIn(TokenType.WIWITI,      tps)
        self.assertIn(TokenType.RAMPUNG,     tps)
        self.assertIn(TokenType.DATATYPE_INT, tps)
        self.assertIn(TokenType.DATATYPE_STR, tps)
        self.assertIn(TokenType.STRING_LIT,  tps)
        self.assertIn(TokenType.TAMPILNA,    tps)

    def test_function_definition(self):
        src = "gawe tambah(angka a, angka b) { balekna a + b }"
        toks = lex(src)
        tps  = types(toks)
        self.assertIn(TokenType.GAWE,         tps)
        self.assertIn(TokenType.DATATYPE_INT,  tps)
        self.assertIn(TokenType.BALEKNA,       tps)
        self.assertIn(TokenType.PLUS,          tps)

    def test_while_loop(self):
        src = "nalika i < 10 { tampilna(i) }"
        toks = lex(src)
        tps  = types(toks)
        self.assertIn(TokenType.NALIKA, tps)
        self.assertIn(TokenType.LT,     tps)

    def test_for_loop(self):
        src = "baleni i = 0; i < 5; i += 1 { tampilna(i) }"
        toks = lex(src)
        tps  = types(toks)
        self.assertIn(TokenType.BALENI,      tps)
        self.assertIn(TokenType.SEMICOLON,   tps)
        self.assertIn(TokenType.PLUS_ASSIGN, tps)

    def test_eof_token(self):
        """Harus selalu diakhiri dengan token EOF."""
        all_tokens = tokenize("angka x = 1")
        self.assertEqual(all_tokens[-1].type, TokenType.EOF)


# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
