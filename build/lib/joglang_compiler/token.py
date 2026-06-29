"""
token.py — Definisi semua token untuk JogLang Compiler.

Berisi:
  - Enum TokenType: semua jenis token yang dikenali JogLang
  - Class Token    : representasi satu token dengan metadata
  - TOKEN_SPEC     : daftar pola regex untuk setiap token (urutan penting!)
  - FORBIDDEN_KEYWORDS: keyword bahasa lain yang dilarang
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


# ===========================================================================
# TOKEN TYPE ENUM
# ===========================================================================

class TokenType(Enum):
    """Semua jenis token yang dikenali oleh JogLang."""

    # -----------------------------------------------------------------------
    # KEYWORD — awal / akhir program
    # -----------------------------------------------------------------------
    WIWITI         = auto()   # wiwiti  (awal program)
    RAMPUNG        = auto()   # rampung (akhir program)

    # -----------------------------------------------------------------------
    # KEYWORD — deklarasi & tipe data
    # -----------------------------------------------------------------------
    GAWE           = auto()   # gawe         (function)
    BALEKNA        = auto()   # balekna      (return)
    DATATYPE_INT   = auto()   # angka        (integer)
    DATATYPE_FLOAT = auto()   # pecahan      (float)
    DATATYPE_STR   = auto()   # teks         (string)
    DATATYPE_BOOL  = auto()   # bener_salah  (boolean)

    # -----------------------------------------------------------------------
    # KEYWORD — kontrol aliran
    # -----------------------------------------------------------------------
    YEN            = auto()   # yen          (if)
    LIYANE_YEN     = auto()   # liyane_yen   (else if)
    LIYANE         = auto()   # liyane       (else)
    NALIKA         = auto()   # nalika       (while)
    BALENI         = auto()   # baleni       (for)
    MANDHEG        = auto()   # mandheg      (break)
    TERUSNA        = auto()   # terusna      (continue)

    # -----------------------------------------------------------------------
    # KEYWORD — I/O
    # -----------------------------------------------------------------------
    TAMPILNA       = auto()   # tampilna     (print)
    TAKON          = auto()   # takon        (input)

    # -----------------------------------------------------------------------
    # LITERAL
    # -----------------------------------------------------------------------
    TRUE           = auto()   # bener        (true)
    FALSE          = auto()   # salah        (false)
    NULL           = auto()   # kosong       (null)

    # -----------------------------------------------------------------------
    # OPERATOR LOGIKA
    # -----------------------------------------------------------------------
    LAN            = auto()   # lan          (and)
    UTAWA          = auto()   # utawa        (or)
    ORA            = auto()   # ora          (not)

    # -----------------------------------------------------------------------
    # OPERATOR ARITMATIKA
    # -----------------------------------------------------------------------
    PLUS           = auto()   # +
    MINUS          = auto()   # -
    STAR           = auto()   # *
    SLASH          = auto()   # /
    PERCENT        = auto()   # %
    POWER          = auto()   # **

    # -----------------------------------------------------------------------
    # OPERATOR PERBANDINGAN
    # -----------------------------------------------------------------------
    EQ             = auto()   # ==
    NEQ            = auto()   # !=
    LT             = auto()   # <
    GT             = auto()   # >
    LTE            = auto()   # <=
    GTE            = auto()   # >=

    # -----------------------------------------------------------------------
    # OPERATOR ASSIGNMENT
    # -----------------------------------------------------------------------
    ASSIGN         = auto()   # =
    PLUS_ASSIGN    = auto()   # +=
    MINUS_ASSIGN   = auto()   # -=
    STAR_ASSIGN    = auto()   # *=
    SLASH_ASSIGN   = auto()   # /=

    # -----------------------------------------------------------------------
    # DELIMITER
    # -----------------------------------------------------------------------
    LPAREN         = auto()   # (
    RPAREN         = auto()   # )
    LBRACE         = auto()   # {
    RBRACE         = auto()   # }
    LBRACKET       = auto()   # [
    RBRACKET       = auto()   # ]
    SEMICOLON      = auto()   # ;
    COLON          = auto()   # :
    COMMA          = auto()   # ,
    DOT            = auto()   # .

    # -----------------------------------------------------------------------
    # LITERAL NILAI
    # -----------------------------------------------------------------------
    INT_LIT        = auto()   # 42, 0, 123
    FLOAT_LIT      = auto()   # 3.14, 0.5
    STRING_LIT     = auto()   # "hello", 'world'

    # -----------------------------------------------------------------------
    # IDENTIFIER & SPECIAL
    # -----------------------------------------------------------------------
    IDENTIFIER     = auto()   # nama variabel / fungsi
    NEWLINE        = auto()   # baris baru (untuk tracking baris)
    COMMENT        = auto()   # // komentar (diabaikan)
    WHITESPACE     = auto()   # spasi / tab (diabaikan)
    EOF            = auto()   # end of file


# ===========================================================================
# TOKEN DATA CLASS
# ===========================================================================

@dataclass
class Token:
    """
    Representasi satu token hasil tokenisasi.

    Attributes:
        type   : Jenis token (TokenType)
        lexeme : Teks asli dari source code
        line   : Nomor baris (mulai dari 1)
        column : Nomor kolom (mulai dari 1)
        value  : Nilai sudah dikonversi (int/float/str), opsional
    """
    type   : TokenType
    lexeme : str
    line   : int
    column : int
    value  : Optional[object] = None

    def __repr__(self) -> str:
        val = f", value={self.value!r}" if self.value is not None else ""
        return (
            f"Token({self.type.name}, "
            f"lexeme={self.lexeme!r}, "
            f"line={self.line}, col={self.column}{val})"
        )

    def is_type(self, *types: TokenType) -> bool:
        """Cek apakah token bertipe salah satu dari yang diberikan."""
        return self.type in types


# ===========================================================================
# TOKEN SPECIFICATION — regex patterns (URUTAN SANGAT PENTING!)
# ===========================================================================
# Format: (TokenType, regex_pattern)
# Pola yang lebih spesifik harus didahulukan.

TOKEN_SPEC: list[tuple[TokenType, str]] = [

    # -----------------------------------------------------------------------
    # Komentar — harus sebelum operator
    # -----------------------------------------------------------------------
    (TokenType.COMMENT,        r'//[^\n]*'),          # // komentar satu baris
    (TokenType.COMMENT,        r'/\*[\s\S]*?\*/'),    # /* komentar blok */

    # -----------------------------------------------------------------------
    # Whitespace & Newline
    # -----------------------------------------------------------------------
    (TokenType.NEWLINE,        r'\n'),
    (TokenType.WHITESPACE,     r'[ \t\r]+'),

    # -----------------------------------------------------------------------
    # Float literal — HARUS sebelum INT agar 3.14 tidak jadi 3 + . + 14
    # -----------------------------------------------------------------------
    (TokenType.FLOAT_LIT,      r'\d+\.\d+'),

    # -----------------------------------------------------------------------
    # Integer literal
    # -----------------------------------------------------------------------
    (TokenType.INT_LIT,        r'\d+'),

    # -----------------------------------------------------------------------
    # String literal (double atau single quote)
    # -----------------------------------------------------------------------
    (TokenType.STRING_LIT,     r'"(?:[^"\\]|\\.)*"'),
    (TokenType.STRING_LIT,     r"'(?:[^'\\]|\\.)*'"),

    # -----------------------------------------------------------------------
    # Keyword — HARUS sebelum IDENTIFIER, gunakan \b (word boundary)
    # Keyword multi-kata (liyane_yen) harus lebih dulu dari keyword tunggal
    # -----------------------------------------------------------------------
    (TokenType.WIWITI,         r'\bwiwiti\b'),
    (TokenType.RAMPUNG,        r'\brampung\b'),
    (TokenType.GAWE,           r'\bgawe\b'),
    (TokenType.BALEKNA,        r'\bbalekna\b'),
    (TokenType.LIYANE_YEN,     r'\bliyane_yen\b'),   # HARUS sebelum LIYANE
    (TokenType.LIYANE,         r'\bliyane\b'),
    (TokenType.YEN,            r'\byen\b'),
    (TokenType.NALIKA,         r'\bnalika\b'),
    (TokenType.BALENI,         r'\bbaleni\b'),
    (TokenType.MANDHEG,        r'\bmandheg\b'),
    (TokenType.TERUSNA,        r'\bterusna\b'),
    (TokenType.TAMPILNA,       r'\btampilna\b'),
    (TokenType.TAKON,          r'\btakon\b'),
    (TokenType.DATATYPE_INT,   r'\bangka\b'),
    (TokenType.DATATYPE_FLOAT, r'\bpecahan\b'),
    (TokenType.DATATYPE_STR,   r'\bteks\b'),
    (TokenType.DATATYPE_BOOL,  r'\bbener_salah\b'),  # HARUS sebelum TRUE (bener)
    (TokenType.TRUE,           r'\bbener\b'),
    (TokenType.FALSE,          r'\bsalah\b'),
    (TokenType.NULL,           r'\bkosong\b'),
    (TokenType.LAN,            r'\blan\b'),
    (TokenType.UTAWA,          r'\butawa\b'),
    (TokenType.ORA,            r'\bora\b'),

    # -----------------------------------------------------------------------
    # Operator — multi-karakter HARUS sebelum single karakter
    # -----------------------------------------------------------------------
    (TokenType.POWER,          r'\*\*'),     # ** sebelum *
    (TokenType.EQ,             r'=='),       # == sebelum =
    (TokenType.NEQ,            r'!='),
    (TokenType.LTE,            r'<='),       # <= sebelum <
    (TokenType.GTE,            r'>='),       # >= sebelum >
    (TokenType.PLUS_ASSIGN,    r'\+='),
    (TokenType.MINUS_ASSIGN,   r'-='),
    (TokenType.STAR_ASSIGN,    r'\*='),
    (TokenType.SLASH_ASSIGN,   r'/='),
    (TokenType.LT,             r'<'),
    (TokenType.GT,             r'>'),
    (TokenType.ASSIGN,         r'='),
    (TokenType.PLUS,           r'\+'),
    (TokenType.MINUS,          r'-'),
    (TokenType.STAR,           r'\*'),
    (TokenType.SLASH,          r'/'),
    (TokenType.PERCENT,        r'%'),

    # -----------------------------------------------------------------------
    # Delimiter
    # -----------------------------------------------------------------------
    (TokenType.LPAREN,         r'\('),
    (TokenType.RPAREN,         r'\)'),
    (TokenType.LBRACE,         r'\{'),
    (TokenType.RBRACE,         r'\}'),
    (TokenType.LBRACKET,       r'\['),
    (TokenType.RBRACKET,       r'\]'),
    (TokenType.SEMICOLON,      r';'),
    (TokenType.COLON,          r':'),
    (TokenType.COMMA,          r','),
    (TokenType.DOT,            r'\.'),

    # -----------------------------------------------------------------------
    # Identifier — HARUS paling akhir setelah semua keyword
    # -----------------------------------------------------------------------
    (TokenType.IDENTIFIER,     r'[a-zA-Z_][a-zA-Z0-9_]*'),
]


# ===========================================================================
# FORBIDDEN KEYWORDS — keyword bahasa lain yang DILARANG
# ===========================================================================

FORBIDDEN_KEYWORDS: set[str] = {
    # Python
    "print", "input", "if", "else", "elif", "while", "for",
    "return", "def", "class", "import", "from", "as", "with",
    "try", "except", "finally", "raise", "pass", "lambda",
    "and", "or", "not", "in", "is", "True", "False", "None",
    "global", "nonlocal", "del", "yield", "assert", "break",
    "continue", "switch", "case",

    # Java
    "System", "out", "println", "public", "private", "protected",
    "static", "void", "int", "float", "double", "boolean", "char",
    "String", "new", "this", "super", "extends", "implements",
    "interface", "abstract", "final", "null", "true", "false",
    "Scanner",

    # C/C++
    "printf", "scanf", "cout", "cin", "endl", "include",
    "namespace", "std", "using",

    # C#
    "Console", "WriteLine", "ReadLine",

    # JavaScript
    "var", "let", "const", "function", "console", "log",
    "undefined",

    # SQL / lainnya
    "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE",
    "NULL", "TRUE", "FALSE",
}

# Keyword yang valid milik JogLang (untuk referensi cepat)
JOGLANG_KEYWORDS: set[str] = {
    "wiwiti", "rampung", "gawe", "balekna", "yen", "liyane_yen",
    "liyane", "nalika", "baleni", "mandheg", "terusna", "tampilna",
    "takon", "angka", "pecahan", "teks", "bener_salah", "bener",
    "salah", "kosong", "lan", "utawa", "ora",
}
