# Lexer — Dokumentasi Teknis

## Ikhtisar

Lexer (tokenizer) adalah tahap pertama kompilasi JogLang. Tugasnya adalah membaca source code karakter demi karakter lalu menghasilkan **daftar Token** yang akan dikonsumsi oleh Parser.

File: `joglang_compiler/lexer.py`, `joglang_compiler/token.py`

---

## Konsep Dasar

### Token

Setiap Token menyimpan:

```python
@dataclass
class Token:
    type   : TokenType   # jenis token (IDENTIFIER, INT_LIT, PLUS, ...)
    lexeme : str         # teks asli dari source code
    line   : int         # nomor baris (mulai dari 1)
    column : int         # nomor kolom (mulai dari 1)
    value  : Optional[object] = None  # nilai sudah dikonversi (int/float/str)
```

### TokenType

Semua jenis token didefinisikan dalam enum `TokenType`:

| Kategori        | Contoh TokenType                              |
|----------------|-----------------------------------------------|
| Program        | `WIWITI`, `RAMPUNG`                          |
| Tipe data      | `DATATYPE_INT`, `DATATYPE_FLOAT`, `DATATYPE_STR`, `DATATYPE_BOOL` |
| Kontrol aliran | `YEN`, `LIYANE_YEN`, `LIYANE`, `NALIKA`, `BALENI` |
| Loop control   | `MANDHEG`, `TERUSNA`                         |
| Fungsi         | `GAWE`, `BALEKNA`                            |
| I/O            | `TAMPILNA`, `TAKON`                          |
| Literal bool   | `TRUE` (`bener`), `FALSE` (`salah`), `NULL` (`kosong`) |
| Logika         | `LAN`, `UTAWA`, `ORA`                        |
| Aritmatika     | `PLUS`, `MINUS`, `STAR`, `SLASH`, `PERCENT`, `POWER` |
| Perbandingan   | `EQ`, `NEQ`, `LT`, `GT`, `LTE`, `GTE`       |
| Assignment     | `ASSIGN`, `PLUS_ASSIGN`, `MINUS_ASSIGN`, `STAR_ASSIGN`, `SLASH_ASSIGN` |
| Delimiter      | `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `COMMA`, `SEMICOLON`, ... |
| Literal nilai  | `INT_LIT`, `FLOAT_LIT`, `STRING_LIT`         |
| Khusus         | `IDENTIFIER`, `COMMENT`, `WHITESPACE`, `EOF` |

---

## Implementasi

### Regex Master Pattern

Seluruh pola TOKEN_SPEC digabung menjadi **satu regex besar** dengan named group:

```python
# Contoh pola TOKEN_SPEC (urutan sangat penting!)
TOKEN_SPEC = [
    (TokenType.COMMENT,       r'//[^\n]*'),           # komentar // ...
    (TokenType.COMMENT,       r'/\*[\s\S]*?\*/'),     # komentar /* ... */
    (TokenType.NEWLINE,       r'\n'),
    (TokenType.WHITESPACE,    r'[ \t\r]+'),
    (TokenType.FLOAT_LIT,     r'\d+\.\d+'),           # HARUS sebelum INT
    (TokenType.INT_LIT,       r'\d+'),
    (TokenType.STRING_LIT,    r'"(?:[^"\\]|\\.)*"'),
    (TokenType.LIYANE_YEN,    r'\bliyane_yen\b'),     # HARUS sebelum LIYANE
    (TokenType.LIYANE,        r'\bliyane\b'),
    # ... dst
    (TokenType.IDENTIFIER,    r'[a-zA-Z_][a-zA-Z0-9_]*'),  # HARUS paling akhir
]
```

Alasan urutan penting:
1. `liyane_yen` harus didahulukan dari `liyane` (prefix match)
2. `float` harus sebelum `int` (agar `3.14` tidak terbaca `3` + `.` + `14`)
3. `==` sebelum `=`, `<=` sebelum `<`, dst. (operator multi-karakter dulu)
4. `IDENTIFIER` paling akhir (keyword sudah lebih dahulu di-match)

### Algoritma Tokenisasi

```
pos = 0
while pos < len(source):
    match = master_regex.match(source, pos)
    if match is None:
        raise LexicalError("Karakter ilegal", line, col)

    token_type = group_name_to_type[match.lastgroup]
    lexeme     = match.group()
    token      = process_token(token_type, lexeme, line, col)

    if token is not None:   # skip WHITESPACE & COMMENT
        tokens.append(token)

    advance_position(lexeme)  # update line & column
    pos = match.end()

tokens.append(Token(EOF, "", line, col))
```

### Pengecekan Keyword Terlarang

Setiap IDENTIFIER diperiksa terhadap `FORBIDDEN_KEYWORDS`:

```python
FORBIDDEN_KEYWORDS = {
    "print", "input", "if", "else", "elif", "while", "for",
    "return", "def", "class", "True", "False", "None",
    "System", "printf", "cout", "cin", "Console", "var", "let", ...
}
```

Jika ditemukan → `LexicalError` dengan lokasi baris dan kolom.

### Konversi Nilai Literal

| Token       | Konversi                                 |
|-------------|------------------------------------------|
| `INT_LIT`   | `int(lexeme)`                            |
| `FLOAT_LIT` | `float(lexeme)`                          |
| `STRING_LIT`| strip kutip + decode escape (`\n`, `\t`) |
| `TRUE`      | `True`                                   |
| `FALSE`     | `False`                                  |
| `NULL`      | `None`                                   |

---

## Error

### LexicalError

Dilempar ketika:
1. Karakter tidak dikenali (bukan bagian dari TOKEN_SPEC mana pun)
2. IDENTIFIER yang cocok dengan FORBIDDEN_KEYWORDS

Format pesan:
```
[Baris 3, Kolom 12] LexicalError: Karakter ilegal '@'
[Baris 1, Kolom 8]  LexicalError: Keyword 'print' adalah kata kunci bahasa lain ...
```

---

## Tracking Posisi (Baris & Kolom)

Setiap karakter `\n` yang ditemukan menaikkan `line` dan mereset `col` ke 1. Karakter lain menaikkan `col` sebesar 1.

```python
def _advance_position(self, lexeme: str) -> None:
    for ch in lexeme:
        if ch == '\n':
            self._line += 1
            self._col  = 1
        else:
            self._col += 1
```

---

## Contoh Tokenisasi

Source code:
```joglang
wiwiti
    angka x = 5 + 3
rampung
```

Hasil token (WHITESPACE & COMMENT difilter):
```
Token(WIWITI,       'wiwiti', line=1, col=1)
Token(DATATYPE_INT, 'angka',  line=2, col=5)
Token(IDENTIFIER,   'x',      line=2, col=11)
Token(ASSIGN,       '=',      line=2, col=13)
Token(INT_LIT,      '5',      line=2, col=15, value=5)
Token(PLUS,         '+',      line=2, col=17)
Token(INT_LIT,      '3',      line=2, col=19, value=3)
Token(RAMPUNG,      'rampung',line=3, col=1)
Token(EOF,          '',        line=3, col=8)
```

---

## Penggunaan API

```python
from joglang_compiler.lexer import Lexer, tokenize

# Cara 1 — class
lexer  = Lexer(source_code)
tokens = lexer.tokenize()

# Cara 2 — shortcut function
tokens = tokenize(source_code)

# Generator (lazy)
for token in lexer.token_generator():
    print(token)
```
