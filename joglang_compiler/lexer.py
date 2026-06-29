"""
lexer.py — Lexer (tokenizer) untuk JogLang Compiler.

Lexer membaca source code karakter demi karakter menggunakan regex
dan menghasilkan list of Token. Jika ditemukan karakter ilegal atau
keyword bahasa lain, LexicalError akan dilempar dengan lokasi tepat.

Fitur:
  - Tokenisasi berbasis regex (TOKEN_SPEC)
  - Tracking baris dan kolom secara akurat
  - Deteksi keyword terlarang (FORBIDDEN_KEYWORDS)
  - Skip whitespace & komentar
  - Konversi nilai literal (int/float/str)
"""

from __future__ import annotations
import re
from typing import Generator

from .token import Token, TokenType, TOKEN_SPEC, FORBIDDEN_KEYWORDS
from .errors import LexicalError


# ===========================================================================
# PRE-COMPILE REGEX MASTER
# ===========================================================================
# Gabungkan semua pola TOKEN_SPEC menjadi satu regex dengan named groups.
# Named group format: (?P<TYPE_INDEX>pola)
# Regex engine akan mencoba pola dari kiri ke kanan — ini mengapa
# urutan TOKEN_SPEC sangat penting.

def _build_master_pattern() -> re.Pattern[str]:
    """Membangun satu regex gabungan dari TOKEN_SPEC."""
    parts: list[str] = []
    seen_names: dict[TokenType, int] = {}

    for token_type, pattern in TOKEN_SPEC:
        # Nama group harus unik; jika TokenType muncul lebih dari sekali
        # (misal STRING_LIT untuk " dan '), tambahkan suffix _2, _3, dst.
        count = seen_names.get(token_type, 0) + 1
        seen_names[token_type] = count
        group_name = f"{token_type.name}_{count}"
        parts.append(f"(?P<{group_name}>{pattern})")

    return re.compile("|".join(parts), re.MULTILINE | re.DOTALL)


# Master regex dikompilasi sekali saat modul di-import (lebih efisien)
_MASTER_PATTERN: re.Pattern[str] = _build_master_pattern()

# Mapping: nama group -> TokenType (strip suffix _1, _2, dst.)
_GROUP_TO_TYPE: dict[str, TokenType] = {
    f"{tt.name}_{i}": tt
    for tt, _ in TOKEN_SPEC
    for i in range(1, 10)  # max 9 pola per TokenType
}


# ===========================================================================
# LEXER CLASS
# ===========================================================================

class Lexer:
    """
    Tokenizer untuk JogLang.

    Usage:
        lexer  = Lexer(source_code)
        tokens = lexer.tokenize()
    """

    def __init__(self, source: str) -> None:
        """
        Args:
            source: Source code JogLang sebagai string.
        """
        self._source: str     = source
        self._line:   int     = 1
        self._col:    int     = 1
        self._tokens: list[Token] = []

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def tokenize(self) -> list[Token]:
        """
        Menjalankan proses tokenisasi penuh.

        Returns:
            List of Token (tidak termasuk WHITESPACE & COMMENT).

        Raises:
            LexicalError: jika ditemukan karakter ilegal.
        """
        self._tokens = []
        self._line   = 1
        self._col    = 1
        pos          = 0
        source_len   = len(self._source)

        while pos < source_len:
            match = _MASTER_PATTERN.match(self._source, pos)

            if match is None:
                # Karakter tidak dikenali
                bad_char = self._source[pos]
                raise LexicalError(
                    f"Karakter ilegal '{bad_char}'",
                    line=self._line,
                    column=self._col,
                )

            # Tentukan TokenType dari nama group yang match
            group_name = match.lastgroup
            token_type = _GROUP_TO_TYPE.get(group_name or "")
            if token_type is None:
                raise LexicalError(
                    f"Grup regex tidak dikenal: '{group_name}'",
                    line=self._line,
                    column=self._col,
                )

            lexeme     = match.group()
            tok_line   = self._line
            tok_col    = self._col

            # Perbarui posisi baris/kolom
            self._advance_position(lexeme)

            # Proses token berdasarkan jenisnya
            token = self._process_token(token_type, lexeme, tok_line, tok_col)

            if token is not None:
                self._tokens.append(token)

            pos = match.end()

        # Tambahkan token EOF
        self._tokens.append(Token(TokenType.EOF, "", self._line, self._col))
        return self._tokens

    def token_generator(self) -> Generator[Token, None, None]:
        """
        Alternatif lazy tokenization (generator).

        Yields:
            Token satu per satu sampai EOF.
        """
        for token in self.tokenize():
            yield token

    # -----------------------------------------------------------------------
    # PRIVATE HELPERS
    # -----------------------------------------------------------------------

    def _advance_position(self, lexeme: str) -> None:
        """
        Memperbarui self._line dan self._col setelah membaca lexeme.
        Setiap \\n menaikkan baris dan mereset kolom.
        """
        for ch in lexeme:
            if ch == "\n":
                self._line += 1
                self._col   = 1
            else:
                self._col  += 1

    def _process_token(
        self,
        token_type: TokenType,
        lexeme:     str,
        line:       int,
        col:        int,
    ) -> Token | None:
        """
        Memproses satu token: konversi nilai & filter token yang tidak perlu.

        Returns:
            Token jika harus disimpan, None jika harus di-skip.

        Raises:
            LexicalError: jika lexeme adalah keyword terlarang.
        """
        # Skip whitespace & komentar — tidak perlu disimpan
        if token_type in (TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE):
            return None

        # --------------------------------------------------------
        # Cek keyword terlarang
        # --------------------------------------------------------
        if token_type == TokenType.IDENTIFIER:
            self._check_forbidden(lexeme, line, col)
            return Token(token_type, lexeme, line, col)

        # --------------------------------------------------------
        # Konversi nilai literal
        # --------------------------------------------------------
        if token_type == TokenType.INT_LIT:
            return Token(token_type, lexeme, line, col, value=int(lexeme))

        if token_type == TokenType.FLOAT_LIT:
            return Token(token_type, lexeme, line, col, value=float(lexeme))

        if token_type == TokenType.STRING_LIT:
            # Hilangkan tanda kutip pembuka/penutup dan proses escape
            raw = lexeme[1:-1]
            val = raw.encode("raw_unicode_escape").decode("unicode_escape")
            return Token(token_type, lexeme, line, col, value=val)

        if token_type == TokenType.TRUE:
            return Token(token_type, lexeme, line, col, value=True)

        if token_type == TokenType.FALSE:
            return Token(token_type, lexeme, line, col, value=False)

        if token_type == TokenType.NULL:
            return Token(token_type, lexeme, line, col, value=None)

        # Semua token lain (keyword, operator, delimiter)
        return Token(token_type, lexeme, line, col)

    def _check_forbidden(self, lexeme: str, line: int, col: int) -> None:
        """
        Memeriksa apakah lexeme adalah keyword bahasa lain yang dilarang.

        Raises:
            LexicalError: jika lexeme ada dalam FORBIDDEN_KEYWORDS.
        """
        if lexeme in FORBIDDEN_KEYWORDS:
            raise LexicalError(
                f"Keyword '{lexeme}' adalah kata kunci bahasa lain dan "
                f"dilarang digunakan dalam JogLang. "
                f"Gunakan keyword JogLang yang sesuai.",
                line=line,
                column=col,
            )


# ===========================================================================
# CONVENIENCE FUNCTION
# ===========================================================================

def tokenize(source: str) -> list[Token]:
    """
    Fungsi shortcut untuk tokenisasi sumber code.

    Args:
        source: Source code JogLang

    Returns:
        List of Token

    Raises:
        LexicalError: jika ada karakter ilegal atau keyword terlarang
    """
    return Lexer(source).tokenize()
