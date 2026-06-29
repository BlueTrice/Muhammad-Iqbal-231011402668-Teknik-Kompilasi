# Dokumentasi Lengkap JogLang Compiler

**Versi:** 1.0.0  
**Bahasa:** JogLang — Bahasa Pemrograman Basa Jawa Dialek Yogyakarta  
**Platform:** Python 3.8+, Windows / Linux / macOS  
**Lisensi:** MIT

---

## Daftar Isi

1. [Gambaran Umum](#1-gambaran-umum)
2. [Instalasi](#2-instalasi)
3. [Struktur Proyek](#3-struktur-proyek)
4. [Bahasa JogLang](#4-bahasa-joglang)
   - 4.1 [Keyword](#41-keyword)
   - 4.2 [Tipe Data](#42-tipe-data)
   - 4.3 [Operator](#43-operator)
   - 4.4 [Sintaks & Grammar](#44-sintaks--grammar)
   - 4.5 [Keyword Terlarang](#45-keyword-terlarang)
5. [Arsitektur Compiler](#5-arsitektur-compiler)
6. [Modul-Modul Compiler](#6-modul-modul-compiler)
   - 6.1 [token.py — Definisi Token](#61-tokenpy--definisi-token)
   - 6.2 [lexer.py — Lexical Analyzer](#62-lexerpy--lexical-analyzer)
   - 6.3 [ast_nodes.py — Abstract Syntax Tree](#63-ast_nodespy--abstract-syntax-tree)
   - 6.4 [parser.py — Syntax Analyzer](#64-parserpy--syntax-analyzer)
   - 6.5 [semantic.py — Semantic Analyzer](#65-semanticpy--semantic-analyzer)
   - 6.6 [optimizer.py — Code Optimizer](#66-optimizerpy--code-optimizer)
   - 6.7 [codegen.py — Code Generator](#67-codegenpy--code-generator)
   - 6.8 [compiler.py — Pipeline Utama](#68-compilerpy--pipeline-utama)
   - 6.9 [errors.py — Hierarki Error](#69-errorspy--hierarki-error)
   - 6.10 [utils.py — Fungsi Utilitas](#610-utilspy--fungsi-utilitas)
7. [CLI — Command Line Interface](#7-cli--command-line-interface)
   - 7.1 [cli.py — Implementasi CLI](#71-clipy--implementasi-cli)
   - 7.2 [main.py — Entry Point](#72-mainpy--entry-point)
   - 7.3 [\_\_main\_\_.py — Module Entry Point](#73-__main__py--module-entry-point)
8. [Interactive REPL](#8-interactive-repl)
   - 8.1 [Cara Menjalankan](#81-cara-menjalankan)
   - 8.2 [Daftar Perintah](#82-daftar-perintah)
   - 8.3 [Alur Penggunaan](#83-alur-penggunaan)
   - 8.4 [Arsitektur REPL](#84-arsitektur-repl)
   - 8.5 [Integrasi dengan Pipeline Compiler](#85-integrasi-dengan-pipeline-compiler)
9. [Contoh Program](#9-contoh-program)
10. [Penanganan Error](#10-penanganan-error)
11. [Testing](#11-testing)
12. [Referensi API](#12-referensi-api)

---

## 1. Gambaran Umum

JogLang Compiler adalah **mini compiler sungguhan** yang dibuat sebagai proyek UAS Mata Kuliah Compiler Construction. Compiler ini mengimplementasikan seluruh tahapan kompilasi dari source code ke kode Python yang dapat dieksekusi.

**Yang membuat JogLang unik:** Seluruh keyword menggunakan **Bahasa Jawa dialek Yogyakarta**. Kata `if` digantikan `yen`, `while` menjadi `nalika`, `function` menjadi `gawe`, dan seterusnya.

### Fitur Utama

- ✅ **6 tahap kompilasi** sungguhan: Lexer → Parser → AST → Semantic Analysis → Optimizer → Code Generation
- ✅ **Interactive REPL** — tulis dan jalankan kode secara langsung di terminal
- ✅ **Optimizer 5 teknik** — constant folding, identity, strength reduction, dead code elimination, boolean short-circuit
- ✅ **Deteksi keyword terlarang** — menolak `print`, `if`, `while`, dan keyword bahasa lain
- ✅ **250 unit test** dengan coverage menyeluruh
- ✅ **12 contoh program** dari halo dunia hingga bilangan prima
- ✅ **Instalasi via pip** — tersedia command `joglang` setelah install

### Alur Kompilasi

```
Source Code (.jog)
        │
        ▼
  ┌─────────────┐
  │    LEXER    │  Tokenisasi → List[Token]
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │   PARSER    │  Parsing → ProgramNode (AST)
  └─────────────┘
        │
        ▼
  ┌──────────────────────┐
  │  SEMANTIC ANALYZER   │  Validasi semantik
  └──────────────────────┘
        │
        ▼
  ┌─────────────┐
  │  OPTIMIZER  │  Optimasi AST
  └─────────────┘
        │
        ▼
  ┌──────────────────┐
  │  CODE GENERATOR  │  AST → Python Code
  └──────────────────┘
        │
        ▼
  Output Python (.py)
```

---

## 2. Instalasi

### Prasyarat

- Python 3.8 atau lebih baru
- pip (Python package manager)

### Windows

```bat
install_windows.bat
```

Script otomatis memeriksa versi Python, memverifikasi pip, lalu menjalankan `pip install .`.

### Linux / macOS

```bash
chmod +x install_unix.sh
./install_unix.sh
```

Script mendeteksi otomatis `python3`/`python` dan `pip3`/`pip`, memverifikasi versi ≥ 3.8, lalu menginstal.

### Manual (semua platform)

```bash
pip install .
```

### Verifikasi Instalasi

```bash
joglang --version
# JogLang Compiler v1.0.0
```

### Uninstall

```bash
# Linux/macOS
./uninstall_unix.sh

# Windows
uninstall_windows.bat

# Manual
pip uninstall joglang
```

---

## 3. Struktur Proyek

```
joglang_project/
│
├── joglang_compiler/              # Package utama compiler
│   ├── __init__.py                # Versi, metadata package
│   ├── __main__.py                # Entry: python -m joglang_compiler
│   ├── token.py                   # TokenType enum, Token class, TOKEN_SPEC, FORBIDDEN_KEYWORDS
│   ├── lexer.py                   # Lexer berbasis regex master pattern
│   ├── ast_nodes.py               # 17 kelas node AST + ASTVisitor base class
│   ├── parser.py                  # Recursive Descent Parser
│   ├── semantic.py                # Semantic Analyzer: SymbolInfo, Scope, SemanticAnalyzer
│   ├── optimizer.py               # Code Optimizer: 5 teknik optimasi
│   ├── codegen.py                 # Code Generator → Python
│   ├── compiler.py                # Pipeline: Compiler class + CompileResult
│   ├── cli.py                     # CLI: argparse + mode handlers + REPL trigger
│   ├── repl.py                    # Interactive REPL: JogLangREPL class
│   ├── errors.py                  # Hierarki exception JogLang
│   └── utils.py                   # read_source_file, write_output_file, print_banner
│
├── examples/                      # 12 contoh program .jog
│   ├── 01_halo_dunia.jog
│   ├── 02_variabel.jog
│   ├── 03_aritmatika.jog
│   ├── 04_kondisional.jog
│   ├── 05_while_loop.jog
│   ├── 06_for_loop.jog
│   ├── 07_fungsi.jog
│   ├── 08_faktorial.jog
│   ├── 09_fibonacci.jog
│   ├── 10_break_continue.jog
│   ├── 11_kalkulator.jog
│   └── 12_bilangan_prima.jog
│
├── output/                        # File .py hasil kompilasi
│
├── tests/                         # 250 unit test
│   ├── __init__.py
│   ├── test_lexer.py              # 53 test tokenisasi
│   ├── test_parser.py             # 55 test parsing & AST
│   ├── test_semantic.py           # 46 test analisis semantik
│   ├── test_optimizer.py          # 50 test optimasi
│   └── test_compiler.py          # 46 test pipeline end-to-end
│
├── docs/                          # Dokumentasi teknis
│   ├── Grammar.md
│   ├── Lexer.md
│   ├── Parser.md
│   ├── AST.md
│   ├── Semantic.md
│   ├── Optimization.md
│   ├── UserGuide.md
│   └── Dokumentasi.md             # ← file ini
│
├── main.py                        # Thin wrapper → cli.main()
├── pyproject.toml                 # Build config, entry_points
├── README.md
├── LICENSE
├── install_windows.bat
├── install_unix.sh
├── uninstall_windows.bat
└── uninstall_unix.sh
```

---

## 4. Bahasa JogLang

### 4.1 Keyword

Seluruh keyword JogLang berasal dari kosakata Bahasa Jawa dialek Yogyakarta:

| Keyword JogLang | Padanan Python | Arti Harfiah     | Kategori      |
|-----------------|----------------|------------------|---------------|
| `wiwiti`        | *(awal)*        | mulai, awali     | Program       |
| `rampung`       | *(akhir)*       | selesai, tamat   | Program       |
| `gawe`          | `def`           | buat             | Fungsi        |
| `balekna`       | `return`        | kembalikan       | Fungsi        |
| `yen`           | `if`            | jika             | Kondisional   |
| `liyane_yen`    | `elif`          | selain jika      | Kondisional   |
| `liyane`        | `else`          | selain itu       | Kondisional   |
| `nalika`        | `while`         | selama, ketika   | Loop          |
| `baleni`        | `for`           | ulangi           | Loop          |
| `mandheg`       | `break`         | berhenti         | Loop Control  |
| `terusna`       | `continue`      | lanjutkan        | Loop Control  |
| `tampilna`      | `print()`       | tampilkan        | I/O           |
| `takon`         | `input()`       | tanya            | I/O           |
| `angka`         | `int`           | angka/bilangan   | Tipe Data     |
| `pecahan`       | `float`         | bilangan pecahan | Tipe Data     |
| `teks`          | `str`           | teks/tulisan     | Tipe Data     |
| `bener_salah`   | `bool`          | benar-salah      | Tipe Data     |
| `bener`         | `True`          | benar            | Literal       |
| `salah`         | `False`         | salah            | Literal       |
| `kosong`        | `None`          | kosong/nihil     | Literal       |
| `lan`           | `and`           | dan              | Logika        |
| `utawa`         | `or`            | atau             | Logika        |
| `ora`           | `not`           | tidak/bukan      | Logika        |

### 4.2 Tipe Data

JogLang mendukung 4 tipe data primitif:

| Tipe        | Keyword      | Contoh Nilai              | Keterangan                     |
|-------------|--------------|---------------------------|--------------------------------|
| Integer     | `angka`      | `42`, `-7`, `0`           | Bilangan bulat                 |
| Float       | `pecahan`    | `3.14`, `-0.5`, `100.0`   | Bilangan desimal               |
| String      | `teks`       | `"Halo"`, `'Dunia'`       | Teks, kutip tunggal atau ganda |
| Boolean     | `bener_salah`| `bener`, `salah`          | Nilai logika benar/salah       |

Tipe data wajib ditulis saat deklarasi variabel baru:

```joglang
angka    umur   = 20
pecahan  tinggi = 170.5
teks     nama   = "Budi Santoso"
bener_salah aktif = bener
```

Deklarasi tanpa nilai awal menghasilkan `None` di Python:

```joglang
angka x          // x = None
teks  pesan      // pesan = None
```

### 4.3 Operator

#### Aritmatika

| Operator | Fungsi        | Contoh    | Hasil |
|----------|---------------|-----------|-------|
| `+`      | Penjumlahan   | `10 + 3`  | `13`  |
| `-`      | Pengurangan   | `10 - 3`  | `7`   |
| `*`      | Perkalian     | `10 * 3`  | `30`  |
| `/`      | Pembagian     | `10 / 3`  | `3.33…` |
| `%`      | Sisa bagi     | `10 % 3`  | `1`   |
| `**`     | Pangkat       | `2 ** 8`  | `256` |

#### Perbandingan (selalu menghasilkan `bener` atau `salah`)

| Operator | Fungsi            | Contoh    | Hasil   |
|----------|-------------------|-----------|---------|
| `==`     | Sama dengan       | `5 == 5`  | `bener` |
| `!=`     | Tidak sama dengan | `5 != 6`  | `bener` |
| `<`      | Kurang dari       | `3 < 5`   | `bener` |
| `>`      | Lebih dari        | `5 > 10`  | `salah` |
| `<=`     | Kurang sama       | `5 <= 5`  | `bener` |
| `>=`     | Lebih sama        | `6 >= 7`  | `salah` |

#### Logika

| Operator | Python | Keterangan                             |
|----------|--------|----------------------------------------|
| `lan`    | `and`  | Benar jika kedua operan benar          |
| `utawa`  | `or`   | Benar jika salah satu operan benar     |
| `ora`    | `not`  | Membalik nilai boolean                 |

#### Assignment

| Operator | Keterangan        | Contoh     | Setara dengan |
|----------|-------------------|------------|---------------|
| `=`      | Assign biasa      | `x = 10`   | `x = 10`      |
| `+=`     | Tambah dan assign | `x += 5`   | `x = x + 5`   |
| `-=`     | Kurang dan assign | `x -= 2`   | `x = x - 2`   |
| `*=`     | Kali dan assign   | `x *= 3`   | `x = x * 3`   |
| `/=`     | Bagi dan assign   | `x /= 2`   | `x = x / 2`   |

#### Preseden Operator (rendah → tinggi)

| Level | Operator                          | Asosiasi  |
|-------|-----------------------------------|-----------|
| 1     | `utawa`                           | Kiri      |
| 2     | `lan`                             | Kiri      |
| 3     | `ora` (unary)                     | Kanan     |
| 4     | `==` `!=` `<` `>` `<=` `>=`      | Kiri      |
| 5     | `+` `-`                           | Kiri      |
| 6     | `*` `/` `%`                       | Kiri      |
| 7     | `**`                              | **Kanan** |
| 8     | `-` (unary negatif)               | Kanan     |
| 9     | literal, variabel, `(ekspresi)`   | —         |

### 4.4 Sintaks & Grammar

#### Struktur Program

Setiap program JogLang **wajib** dibungkus `wiwiti` dan `rampung`:

```joglang
wiwiti
    // isi program di sini
rampung
```

Program minimal yang valid:

```joglang
wiwiti
rampung
```

#### Komentar

```joglang
// Komentar satu baris

/* Komentar
   beberapa baris */
```

#### Deklarasi Variabel

```joglang
angka    x = 10
pecahan  pi = 3.14
teks     salam = "Halo"
bener_salah lulus = bener
angka    y          // tanpa nilai awal → None
```

#### Assignment

```joglang
x = 20
x += 5      // x = x + 5
x -= 3      // x = x - 3
x *= 2      // x = x * 2
x /= 4      // x = x / 4
```

#### Input & Output

```joglang
tampilna("Halo Dunia!")          // print string
tampilna(x)                       // print variabel
tampilna(3 + 4)                   // print ekspresi
tampilna("Nilai: " + nama)        // string concatenation

teks nama  = takon("Masukkan nama: ")  // input dengan prompt
teks kode  = takon()                    // input tanpa prompt
```

#### Kondisional

```joglang
yen x > 0 {
    tampilna("positif")
} liyane_yen x == 0 {
    tampilna("nol")
} liyane {
    tampilna("negatif")
}
```

#### Loop While

```joglang
angka i = 1
nalika i <= 10 {
    tampilna(i)
    i = i + 1
}
```

#### Loop For

Sintaks: `baleni <init> ; <kondisi> ; <update> { }`

```joglang
baleni angka i = 1 ; i <= 10 ; i += 1 {
    tampilna(i)
}
```

#### Break & Continue

```joglang
nalika bener {
    angka n = takon("Angka: ")
    yen n == 0 { mandheg }    // keluar loop
    yen n < 0  { terusna }    // lanjut iterasi berikutnya
    tampilna(n)
}
```

#### Fungsi

```joglang
gawe tambah(angka a, angka b) {
    balekna a + b
}

angka hasil = tambah(3, 4)    // pemanggilan: hasil = 7
```

Fungsi rekursif:

```joglang
gawe faktorial(angka n) {
    yen n <= 1 {
        balekna 1
    }
    balekna n * faktorial(n - 1)
}
```

#### Grammar EBNF Lengkap

```ebnf
program         ::= 'wiwiti' statement* 'rampung'

statement       ::= var_decl | assignment_stmt | print_stmt
                  | if_stmt  | while_stmt | for_stmt
                  | function_decl | return_stmt
                  | break_stmt | continue_stmt | call_stmt

var_decl        ::= datatype IDENTIFIER ('=' expression)? ';'?
assignment_stmt ::= IDENTIFIER assign_op expression ';'?
print_stmt      ::= 'tampilna' '(' expression ')' ';'?
if_stmt         ::= 'yen' expression block
                    ('liyane_yen' expression block)*
                    ('liyane' block)?
while_stmt      ::= 'nalika' expression block
for_stmt        ::= 'baleni' for_init ';' expression ';' for_update block
function_decl   ::= 'gawe' IDENTIFIER '(' param_list? ')' block
return_stmt     ::= 'balekna' expression? ';'?
break_stmt      ::= 'mandheg' ';'?
continue_stmt   ::= 'terusna' ';'?
block           ::= '{' statement* '}'

expression      ::= or_expr
or_expr         ::= and_expr ('utawa' and_expr)*
and_expr        ::= not_expr ('lan' not_expr)*
not_expr        ::= 'ora' not_expr | comparison
comparison      ::= addition (cmp_op addition)*
addition        ::= multiplication (('+' | '-') multiplication)*
multiplication  ::= power (('*' | '/' | '%') power)*
power           ::= unary ('**' unary)*
unary           ::= '-' unary | primary
primary         ::= INT_LIT | FLOAT_LIT | STRING_LIT
                  | 'bener' | 'salah' | 'kosong'
                  | IDENTIFIER '(' arg_list? ')'
                  | IDENTIFIER
                  | '(' expression ')'
                  | 'takon' '(' expression? ')'
```

### 4.5 Keyword Terlarang

Compiler **menolak** semua keyword dari bahasa pemrograman lain. Penggunaan menghasilkan `LexicalError`:

| Bahasa     | Keyword yang Dilarang                                                               |
|------------|-------------------------------------------------------------------------------------|
| Python     | `print` `input` `if` `else` `elif` `while` `for` `return` `def` `class` `True` `False` `None` `and` `or` `not` `import` `global` `lambda` ... |
| Java       | `System` `out` `println` `int` `float` `boolean` `String` `new` `null` `true` `false` `Scanner` ... |
| C/C++      | `printf` `scanf` `cout` `cin` `include` `namespace` ...                            |
| C#         | `Console` `WriteLine` `ReadLine`                                                   |
| JavaScript | `var` `let` `const` `function` `console` `log` `undefined`                        |

---

## 5. Arsitektur Compiler

JogLang Compiler terdiri dari 6 komponen utama yang membentuk pipeline linear:

```
┌──────────────────────────────────────────────────────────────┐
│                     compiler.py (Compiler)                    │
│                                                              │
│  source  ┌─────────┐  tokens  ┌────────┐  AST              │
│  ──────► │  Lexer  │ ───────► │ Parser │ ────►              │
│  (str)   └─────────┘          └────────┘      │             │
│                                                ▼             │
│          ┌──────────────────────────────────────────┐       │
│          │         SemanticAnalyzer                 │       │
│          │  - SymbolTable (Scope bersarang)         │       │
│          │  - Type checking                         │       │
│          └──────────────────────────────────────────┘       │
│                                                │             │
│                                                ▼             │
│          ┌───────────────────────────────────────┐          │
│          │             Optimizer                  │          │
│          │  - Constant Folding                    │          │
│          │  - Identity Optimization               │          │
│          │  - Strength Reduction                  │          │
│          │  - Dead Code Elimination               │          │
│          │  - Boolean Short-Circuit               │          │
│          └───────────────────────────────────────┘          │
│                                                │             │
│                                                ▼             │
│          ┌───────────────────────────────────────┐          │
│          │           CodeGenerator                │          │
│          │  AST → Python source code (str)        │          │
│          └───────────────────────────────────────┘          │
│                                                │             │
│                                           python_code        │
│                                           (str)              │
└──────────────────────────────────────────────────────────────┘
```

Semua tahap terhubung melalui `CompileResult` yang menyimpan hasil setiap tahap:

```python
@dataclass
class CompileResult:
    success:       bool                        # True jika berhasil
    source_path:   Optional[str]               # path file .jog
    output_path:   Optional[str]               # path file .py output
    python_code:   str                         # kode Python hasil generate
    tokens:        list                        # hasil Lexer (jika verbose)
    ast:           Optional[ProgramNode]       # hasil Parser
    optimized_ast: Optional[ProgramNode]       # hasil Optimizer
    opt_stats:     Optional[OptimizationStats] # statistik optimasi
    error:         Optional[JogLangError]      # error jika gagal
    elapsed_ms:    float                       # waktu kompilasi (ms)
    stage:         str                         # tahap terakhir berjalan
```

---

## 6. Modul-Modul Compiler

### 6.1 token.py — Definisi Token

Mendefinisikan semua elemen leksikal JogLang.

#### TokenType (Enum)

```python
class TokenType(Enum):
    # Program
    WIWITI, RAMPUNG

    # Fungsi
    GAWE, BALEKNA

    # Tipe data
    DATATYPE_INT, DATATYPE_FLOAT, DATATYPE_STR, DATATYPE_BOOL

    # Kontrol aliran
    YEN, LIYANE_YEN, LIYANE, NALIKA, BALENI, MANDHEG, TERUSNA

    # I/O
    TAMPILNA, TAKON

    # Literal
    TRUE, FALSE, NULL

    # Logika
    LAN, UTAWA, ORA

    # Aritmatika
    PLUS, MINUS, STAR, SLASH, PERCENT, POWER

    # Perbandingan
    EQ, NEQ, LT, GT, LTE, GTE

    # Assignment
    ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, STAR_ASSIGN, SLASH_ASSIGN

    # Delimiter
    LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET
    SEMICOLON, COLON, COMMA, DOT

    # Literal nilai
    INT_LIT, FLOAT_LIT, STRING_LIT

    # Lainnya
    IDENTIFIER, COMMENT, NEWLINE, WHITESPACE, EOF
```

#### Token (Dataclass)

```python
@dataclass
class Token:
    type:   TokenType         # jenis token
    lexeme: str               # teks asli dari source code
    line:   int               # nomor baris (mulai 1)
    column: int               # nomor kolom (mulai 1)
    value:  Optional[object]  # nilai sudah dikonversi (int/float/str/bool/None)
```

#### TOKEN_SPEC

Daftar pola regex yang **urutan penting** (lebih spesifik duluan):

```python
TOKEN_SPEC = [
    (TokenType.COMMENT,       r'//[^\n]*'),
    (TokenType.COMMENT,       r'/\*[\s\S]*?\*/'),
    (TokenType.FLOAT_LIT,     r'\d+\.\d+'),        # sebelum INT_LIT
    (TokenType.INT_LIT,       r'\d+'),
    (TokenType.STRING_LIT,    r'"(?:[^"\\]|\\.)*"'),
    (TokenType.LIYANE_YEN,    r'\bliyane_yen\b'),   # sebelum LIYANE
    (TokenType.LIYANE,        r'\bliyane\b'),
    # ... semua keyword ...
    (TokenType.POWER,         r'\*\*'),              # sebelum STAR
    (TokenType.EQ,            r'=='),                # sebelum ASSIGN
    # ... semua operator ...
    (TokenType.IDENTIFIER,    r'[a-zA-Z_][a-zA-Z0-9_]*'),  # paling akhir
]
```

#### FORBIDDEN_KEYWORDS & JOGLANG_KEYWORDS

```python
FORBIDDEN_KEYWORDS: set[str] = {
    "print", "input", "if", "else", "elif", "while", "for",
    "return", "def", "class", "True", "False", "None", ...
}

JOGLANG_KEYWORDS: set[str] = {
    "wiwiti", "rampung", "gawe", "balekna", "yen", ...
}
```

---

### 6.2 lexer.py — Lexical Analyzer

Mengubah source code menjadi daftar token menggunakan **regex master pattern**.

#### Kelas Lexer

```python
class Lexer:
    def __init__(self, source: str) -> None
    def tokenize(self) -> list[Token]        # tokenisasi seluruh source
    def token_generator(self) -> Generator   # generator (lazy)
```

#### Fungsi shortcut

```python
def tokenize(source: str) -> list[Token]
```

#### Algoritma

1. Gabungkan semua pola `TOKEN_SPEC` menjadi satu regex master dengan named groups
2. Jalankan `re.match()` dari posisi saat ini secara berulang
3. Jika tidak ada match → `LexicalError` (karakter ilegal)
4. Setiap IDENTIFIER diperiksa terhadap `FORBIDDEN_KEYWORDS`
5. `WHITESPACE` dan `COMMENT` difilter (tidak masuk hasil)
6. Tracking baris dan kolom diperbarui setiap karakter `\n`

#### Contoh tokenisasi

Source code:
```joglang
angka x = 5 + 3
```

Token yang dihasilkan:
```
Token(DATATYPE_INT, 'angka', line=1, col=1)
Token(IDENTIFIER,   'x',     line=1, col=7)
Token(ASSIGN,       '=',     line=1, col=9)
Token(INT_LIT,      '5',     line=1, col=11, value=5)
Token(PLUS,         '+',     line=1, col=13)
Token(INT_LIT,      '3',     line=1, col=15, value=3)
Token(EOF,          '',      line=1, col=16)
```

---

### 6.3 ast_nodes.py — Abstract Syntax Tree

Mendefinisikan 17 kelas node AST beserta `ASTVisitor` base class.

#### Hierarki Node

```
ASTNode (base, memiliki: line, column)
│
├── ProgramNode              body: list[ASTNode]
│
├── Statement Nodes
│   ├── VariableDeclarationNode    var_type, name, initializer
│   ├── AssignmentNode             name, operator, value
│   ├── PrintNode                  expression
│   ├── InputNode                  prompt
│   ├── ReturnNode                 value
│   ├── BreakNode
│   └── ContinueNode
│
├── Control Flow Nodes
│   ├── BlockNode                  statements: list
│   ├── IfNode                     condition, then_branch, elif_branches, else_branch
│   ├── WhileNode                  condition, body
│   └── ForNode                    init, condition, update, body
│
├── Function Nodes
│   ├── ParameterNode              param_type, name
│   ├── FunctionNode               name, params, return_type, body
│   └── CallNode                   name, arguments
│
└── Expression Nodes
    ├── BinaryOperationNode        left, operator, right
    ├── UnaryOperationNode         operator, operand
    ├── VariableNode               name
    └── LiteralNode                value, kind ('int'|'float'|'string'|'bool'|'null')
```

#### ASTVisitor (Visitor Pattern)

```python
class ASTVisitor:
    def generic_visit(self, node: ASTNode) -> Any: ...
    def visit_children(self, node: ASTNode) -> None: ...
```

Setiap node memanggil `accept(visitor)` yang mendispatch ke `visit_NamaNode()`:

```python
def accept(self, visitor: ASTVisitor) -> Any:
    method = getattr(visitor, f"visit_{type(self).__name__}", visitor.generic_visit)
    return method(self)
```

---

### 6.4 parser.py — Syntax Analyzer

Mengubah token menjadi AST menggunakan **Recursive Descent Parser**.

#### Kelas Parser

```python
class Parser:
    def __init__(self, tokens: list[Token]) -> None
    def parse(self) -> ProgramNode
```

#### Fungsi shortcut

```python
def parse(tokens: list[Token]) -> ProgramNode
```

#### Helper Methods

| Method             | Fungsi                                                   |
|--------------------|----------------------------------------------------------|
| `_current`         | Token aktif (tidak maju)                                |
| `_peek`            | Token satu langkah ke depan (lookahead 1)               |
| `_advance()`       | Ambil token aktif, maju ke berikutnya                   |
| `_check(*types)`   | `True` jika token aktif bertipe salah satu dari `types` |
| `_match(*types)`   | Jika cocok: maju dan return `True`                      |
| `_expect(type)`    | Maju jika cocok, lempar `SyntaxError_` jika tidak       |
| `_skip_semicolons()`| Lewati titik koma opsional                             |

#### Fungsi Parse per Konstruksi

| Fungsi                  | Menangani                   |
|-------------------------|-----------------------------|
| `_parse_statement()`    | Dispatcher utama            |
| `_parse_var_decl()`     | `angka x = 5`               |
| `_parse_assignment()`   | `x = 10`, `x += 5`          |
| `_parse_print()`        | `tampilna(expr)`            |
| `_parse_if()`           | `yen ... liyane_yen ... liyane` |
| `_parse_while()`        | `nalika cond { }`           |
| `_parse_for()`          | `baleni init ; cond ; update { }` |
| `_parse_function()`     | `gawe nama(params) { }`     |
| `_parse_return()`       | `balekna expr`              |
| `_parse_expression()`   | Ekspresi (dispatcher)       |
| `_parse_or()` … `_parse_primary()` | Hierarki preseden |

---

### 6.5 semantic.py — Semantic Analyzer

Memvalidasi kebenaran makna program menggunakan **Visitor Pattern** dan **Symbol Table bersarang**.

#### Kelas-kelas

```python
class SymbolInfo:
    name:     str
    kind:     str            # 'variable' | 'function'
    var_type: Optional[str]  # 'angka' | 'pecahan' | 'teks' | 'bener_salah'
    params:   list           # [ParameterNode] untuk fungsi
    line:     int
    column:   int

class Scope:
    def define(self, symbol: SymbolInfo) -> None   # daftarkan simbol
    def lookup(self, name: str) -> Optional[SymbolInfo]   # cari ke atas
    def lookup_local(self, name: str) -> Optional[SymbolInfo]  # hanya lokal

class SemanticAnalyzer(ASTVisitor):
    def analyze(self, node: ProgramNode) -> None   # entry point
```

#### Fungsi shortcut

```python
def analyze(ast: ProgramNode) -> None
```

#### Pemeriksaan Semantik

| No | Pemeriksaan                         | Trigger Error                        |
|----|-------------------------------------|--------------------------------------|
| 1  | Variabel belum dideklarasikan       | `tampilna(x)` tanpa `angka x`       |
| 2  | Redeklarasi variabel (scope sama)   | `angka x = 1` dua kali              |
| 3  | Fungsi belum dideklarasikan         | `hasil()` tanpa `gawe hasil()`      |
| 4  | Jumlah argumen tidak sesuai         | `tambah(1)` untuk fungsi 2 param    |
| 5  | Memanggil variabel sebagai fungsi   | `angka x = 5` lalu `x()`           |
| 6  | Assign ke fungsi                    | `gawe f() {...}` lalu `f = 5`      |
| 7  | Type mismatch pada deklarasi        | `teks nama = 42`                    |
| 8  | Type mismatch pada assignment       | `angka x = 5` lalu `x = "halo"`   |
| 9  | `balekna` di luar fungsi            | `wiwiti balekna 5 rampung`          |
| 10 | `mandheg` di luar loop              | `wiwiti mandheg rampung`            |
| 11 | `terusna` di luar loop              | `wiwiti terusna rampung`            |
| 12 | `ora` pada tipe non-boolean         | `ora 42`                            |

#### Scope Bersarang (Lexical Scoping)

```
Scope global
  ├── x: angka
  ├── tambah: function(a, b)
  └── Scope fungsi "tambah"
        ├── a: angka
        ├── b: angka
        └── Scope if (di dalam tambah)
              └── temp: angka
```

Variabel di scope dalam bisa mengakses scope luar. Redeklarasi hanya error jika di scope yang **sama**.

---

### 6.6 optimizer.py — Code Optimizer

Melakukan 5 teknik optimasi pada AST setelah validasi semantik.

#### Kelas

```python
class OptimizationStats:
    constant_folds:       int
    identity_opts:        int
    strength_reductions:  int
    dead_code_removed:    int
    total:                int
    def summary(self) -> str

class Optimizer:
    def optimize(self, node: ProgramNode) -> ProgramNode
    @property
    def stats(self) -> OptimizationStats
```

#### Fungsi shortcut

```python
def optimize(ast: ProgramNode) -> tuple[ProgramNode, OptimizationStats]
```

#### Teknik Optimasi

**1. Constant Folding** — evaluasi ekspresi literal saat kompilasi:

| Sebelum             | Sesudah        |
|---------------------|----------------|
| `5 + 3`             | `8`            |
| `10 * 2`            | `20`           |
| `2 ** 8`            | `256`          |
| `"halo" + " dunia"` | `"halo dunia"` |
| `5 == 5`            | `bener`        |
| `ora bener`         | `salah`        |
| `-5`                | `-5`           |

**2. Identity Optimization** — eliminasi operasi identitas:

| Sebelum  | Sesudah | Aturan               |
|----------|---------|----------------------|
| `x + 0`  | `x`     | identitas penjumlahan |
| `0 + x`  | `x`     |                      |
| `x - 0`  | `x`     |                      |
| `x * 1`  | `x`     | identitas perkalian  |
| `1 * x`  | `x`     |                      |
| `x / 1`  | `x`     |                      |
| `x ** 1` | `x`     |                      |
| `x * 0`  | `0`     | zero property        |
| `0 * x`  | `0`     |                      |
| `x ** 0` | `1`     | pangkat nol          |

**3. Strength Reduction** — ganti operasi mahal dengan yang lebih murah:

| Sebelum  | Sesudah  | Keterangan                         |
|----------|----------|------------------------------------|
| `x ** 2` | `x * x`  | Pangkat 2 → perkalian biasa       |

**4. Dead Code Elimination** — hapus kode yang tidak mungkin dieksekusi:

| Sebelum                                      | Sesudah            |
|----------------------------------------------|--------------------|
| `yen bener { A } liyane { B }`              | `A`                |
| `yen salah { A } liyane { B }`              | `B`                |
| `yen salah { A }` (tanpa else)              | *(dihapus)*        |
| `nalika salah { ... }`                       | *(dihapus)*        |

**5. Boolean Short-Circuit** — sederhanakan ekspresi logika dengan literal:

| Sebelum         | Sesudah   |
|-----------------|-----------|
| `bener lan x`   | `x`       |
| `salah lan x`   | `salah`   |
| `bener utawa x` | `bener`   |
| `salah utawa x` | `x`       |

Optimizer berjalan **single-pass bottom-up**: optimasi bertingkat terjadi otomatis karena sub-ekspresi dioptimasi sebelum ekspresi parent.

---

### 6.7 codegen.py — Code Generator

Mengubah AST yang sudah dioptimasi menjadi kode Python yang valid.

#### Kelas

```python
class CodeGenerator:
    def generate(self, node: ProgramNode) -> str
```

#### Fungsi shortcut

```python
def generate(ast: ProgramNode) -> str
```

#### Pemetaan JogLang → Python

| JogLang                            | Python                         |
|------------------------------------|--------------------------------|
| `angka x = 5`                      | `x = 5`                        |
| `angka x` (tanpa init)             | `x = None`                     |
| `tampilna(x)`                      | `print(x)`                     |
| `takon("prompt")`                  | `input("prompt")`              |
| `gawe f(angka a, angka b) { }`     | `def f(a, b):`                 |
| `balekna x`                        | `return x`                     |
| `yen cond { }`                     | `if cond:`                     |
| `liyane_yen cond { }`              | `elif cond:`                   |
| `liyane { }`                       | `else:`                        |
| `nalika cond { }`                  | `while cond:`                  |
| `baleni init ; cond ; update { }`  | `init` + `while cond:` + update|
| `mandheg`                          | `break`                        |
| `terusna`                          | `continue`                     |
| `lan` / `utawa` / `ora`           | `and` / `or` / `not`          |
| `bener` / `salah` / `kosong`      | `True` / `False` / `None`     |

#### Penanganan For Loop

Karena semantik `baleni` lebih mirip C-style for (bukan Python for-in), compiler mengubahnya menjadi while:

```joglang
baleni angka i = 1 ; i <= 10 ; i += 1 {
    tampilna(i)
}
```

Menjadi:

```python
i = 1
while i <= 10:
    print(i)
    i += 1
```

**Kasus khusus `terusna` dalam `baleni`:** Jika ada `terusna` (continue) di dalam body for, update statement disisipkan sebelum `continue` agar tidak terjadi infinite loop:

```python
i = 1
while i <= 10:
    if i % 2 == 0:
        i += 1        # ← update disisipkan sebelum continue
        continue
    print(i)
    i += 1
```

---

### 6.8 compiler.py — Pipeline Utama

Mengintegrasikan semua tahap kompilasi.

#### Class Compiler

```python
class Compiler:
    def __init__(
        self,
        verbose:    bool = False,
        optimize:   bool = True,
        output_dir: str  = "output",
    ) -> None

    def compile_source(
        self,
        source:      str,
        source_path: Optional[str] = None,
        save_output: bool          = False,
    ) -> CompileResult

    def compile_file(self, filepath: str) -> CompileResult
```

#### Fungsi shortcut

```python
def compile(source: str, optimize: bool = True) -> CompileResult
def compile_file(filepath: str, optimize: bool = True) -> CompileResult
def compile_and_run(source: str, optimize: bool = True) -> None
```

#### Penggunaan

```python
from joglang_compiler.compiler import Compiler, compile

# Cara 1 — class
result = Compiler(verbose=True).compile_source(source_code)
if result.success:
    print(result.python_code)
else:
    print(result.error)

# Cara 2 — shortcut
result = compile("wiwiti tampilna(42) rampung")
print(result.python_code)  # → print(42)

# Cara 3 — dari file
result = Compiler().compile_file("examples/halo.jog")
```

---

### 6.9 errors.py — Hierarki Error

```
JogLangError (base)
    ├── LexicalError          # karakter ilegal, keyword terlarang
    ├── SyntaxError_          # struktur tidak sesuai grammar
    ├── SemanticError         # makna tidak valid
    ├── CodeGenerationError   # node tidak dikenal saat generate
    └── OptimizationError     # error saat optimasi (jarang)
```

Semua error menyimpan `line` dan `column`:

```python
class JogLangError(Exception):
    message: str
    line:    int
    column:  int
    # Format: "[Baris 3, Kolom 12] LexicalError: ..."
```

---

### 6.10 utils.py — Fungsi Utilitas

```python
def read_source_file(filepath: str) -> str
    # Baca file .jog, raise FileNotFoundError / ValueError

def write_output_file(filepath: str, content: str) -> None
    # Tulis file .py, buat direktori jika belum ada

def get_output_path(source_path: str, output_dir: str = "output") -> str
    # examples/halo.jog → output/halo.py

def print_banner() -> None
    # Tampilkan banner ASCII art JogLang
```

---

## 7. CLI — Command Line Interface

### 7.1 cli.py — Implementasi CLI

Implementasi lengkap argparse CLI dengan semua mode operasi.

#### Opsi CLI

```
joglang [file.jog] [opsi]

Positional:
  file              File source JogLang (.jog)

Opsi:
  -o, --output DIR  Direktori output (default: output/)
  -v, --verbose     Tampilkan informasi lengkap (token, AST, stats)
  --no-optimize     Nonaktifkan optimizer
  --run             Kompilasi lalu jalankan hasilnya langsung
  --tokens          Debug: tampilkan hasil tokenisasi
  --ast             Debug: tampilkan AST hasil parsing
  --version         Tampilkan versi
  -h, --help        Tampilkan bantuan
```

#### Mode Operasi

| Kondisi                       | Mode yang Aktif                  |
|-------------------------------|----------------------------------|
| Tanpa argumen (`joglang`)     | **Interactive REPL**             |
| `joglang file.jog`            | **Compile** → simpan ke output/  |
| `joglang file.jog --run`      | **Compile + Run**                |
| `joglang file.jog --tokens`   | **Debug Tokens**                 |
| `joglang file.jog --ast`      | **Debug AST**                    |

### 7.2 main.py — Entry Point

File tipis (*thin wrapper*) yang mendelegasikan ke `cli.main()`:

```python
# main.py
from joglang_compiler.cli import main
if __name__ == "__main__":
    sys.exit(main())
```

Keberadaannya mempertahankan kompatibilitas `python main.py ...` dari direktori proyek.

### 7.3 \_\_main\_\_.py — Module Entry Point

Memungkinkan `python -m joglang_compiler`:

```python
# joglang_compiler/__main__.py
from .cli import main
if __name__ == "__main__":
    sys.exit(main())
```

#### Tiga Cara Menjalankan (Setara)

```bash
python main.py examples/halo.jog        # dari direktori proyek
python -m joglang_compiler examples/halo.jog   # module mode
joglang examples/halo.jog              # setelah pip install
```

---

## 8. Interactive REPL

### 8.1 Cara Menjalankan

REPL aktif otomatis ketika **tidak ada argumen file**:

```bash
python main.py              # → Interactive REPL
python -m joglang_compiler  # → Interactive REPL
joglang                     # → Interactive REPL (setelah install)
```

Tampilan awal REPL:

```
════════════════════════════════════════════════════
  JogLang Compiler v1.0.0
  Basa Jawa Dialek Yogyakarta
  Interactive REPL
════════════════════════════════════════════════════

  Perintah tersedia:
    :run                  Compile dan jalankan source code
    :save                 Simpan source code ke file .jog
    :clear                Hapus seluruh source code
    :new                  Buat source code baru
    :show                 Tampilkan source code saat ini
    :help                 Tampilkan bantuan ini
    :exit                 Keluar dari REPL

  Ketik source code JogLang lalu :run untuk menjalankan.
  Baris input dimulai dengan nomor otomatis.

────────────────────────────────────────────────────
```

### 8.2 Daftar Perintah

| Perintah | Fungsi                                                    |
|----------|-----------------------------------------------------------|
| `:run`   | Kompilasi buffer lalu jalankan, tampilkan output          |
| `:save`  | Simpan buffer ke `examples/<nama>.jog`                    |
| `:clear` | Hapus seluruh buffer, nomor baris kembali ke `01`         |
| `:new`   | Buat sesi baru (tanya konfirmasi jika belum disimpan)     |
| `:show`  | Tampilkan seluruh buffer dengan nomor baris               |
| `:help`  | Tampilkan daftar perintah dan tips                        |
| `:exit`  | Keluar dari REPL (tanya konfirmasi jika belum disimpan)   |

Perintah tidak peka huruf besar/kecil: `:Run`, `:RUN`, `:run` semua valid.

Perintah tidak dikenal ditampilkan sebagai pesan ramah, bukan error crash.

### 8.3 Alur Penggunaan

#### Menulis dan Menjalankan Program

```
  01 │ wiwiti
  02 │     angka x = 10 * 2 + 5
  03 │     tampilna(x)
  04 │ rampung
  05 │ :run
```

Output:

```
────────────────────────────────────────────────────
  ✓ Lexical Analysis
  ✓ Parser
  ✓ Semantic Analysis
  ✓ Optimizer
  ✓ Code Generation
────────────────────────────────────────────────────

  Program Output
────────────────────────────────────────────────────

25

────────────────────────────────────────────────────
```

> Nilai `25` adalah hasil `10 * 2 + 5` — constant folding bekerja: `10 * 2 → 20`, lalu `20 + 5 → 25`.

#### Melihat Source Code yang Sudah Diketik

```
  05 │ :show
```

```
────────────────────────────────────────────────────
  Source Code Saat Ini:
────────────────────────────────────────────────────
  01 │ wiwiti
  02 │     angka x = 10 * 2 + 5
  03 │     tampilna(x)
  04 │ rampung
────────────────────────────────────────────────────
```

#### Menyimpan ke File

```
  05 │ :save
  Nama file (tanpa .jog): latihan1
  ✓ Disimpan ke: examples/latihan1.jog
```

Jika file sudah ada:

```
  Nama file (tanpa .jog): latihan1
  File 'examples/latihan1.jog' sudah ada. Overwrite? [Y/N]: Y
  ✓ Disimpan ke: examples/latihan1.jog
```

Nama file disanitasi otomatis: karakter selain alfanumerik, `_`, `-` diganti `_`.

#### Ketika Ada Error

```
  01 │ wiwiti
  02 │     tampilna(belumAda)
  03 │ rampung
  04 │ :run
```

```
────────────────────────────────────────────────────
  ✓ Lexical Analysis
  ✓ Parser
  ✗ Semantic Analysis

  Error: SemanticError: Ditemukan 1 kesalahan semantik:
  [Baris 2, Kolom 15] SemanticError: 'belumAda' belum dideklarasikan.
────────────────────────────────────────────────────
```

#### Keluar dengan Konfirmasi

```
  04 │ :exit
  Source code belum disimpan. Keluar? [Y/N]: N
  Tetap di REPL.

  05 │ :exit
  Source code belum disimpan. Keluar? [Y/N]: Y

  Matur nuwun sampun nggunakaken JogLang!
```

Jika buffer kosong atau sudah disimpan, REPL langsung keluar tanpa konfirmasi.

`Ctrl+C` atau `Ctrl+D` memicu konfirmasi yang sama seperti `:exit`.

### 8.4 Arsitektur REPL

File: `joglang_compiler/repl.py`

```python
class JogLangREPL:
    _buffer:       list[str]   # baris-baris source code
    _saved:        bool        # True = tidak ada perubahan belum disimpan
    _examples_dir: str         # direktori untuk :save
    _compiler:     Compiler    # instance pipeline compiler

    def run(self) -> None                    # loop utama REPL

    # Perintah
    def _cmd_run(self)   -> None
    def _cmd_save(self)  -> None
    def _cmd_clear(self) -> None
    def _cmd_new(self)   -> None
    def _cmd_show(self)  -> None
    def _cmd_help(self)  -> None
    def _confirm_exit(self) -> bool

def start_repl(examples_dir: str = "examples", optimize: bool = True) -> None
```

#### State Machine REPL

```
         ┌──────────────────────────────┐
         ▼                              │
    ┌─────────┐  baris teks             │
    │  IDLE   │ ─────────────► buffer.append(baris)
    │ (prompt)│                         │
    └─────────┘                         │
         │ perintah :xxx                │
         ▼                              │
    ┌─────────────┐                     │
    │  DISPATCH   │                     │
    └─────────────┘                     │
         │                              │
    ┌────┴────────────────────┐         │
    │                         │         │
    ▼                         ▼         │
  :run                      :save       │
  :clear                    :new        │
  :show                     :help       │
    │                         │         │
    └──────────────┬──────────┘         │
                   │                    │
                   └────────────────────┘
                         │ :exit + Y
                         ▼
                      EXIT
```

### 8.5 Integrasi dengan Pipeline Compiler

REPL **tidak memiliki compiler sendiri** — seluruh proses kompilasi didelegasikan ke `Compiler.compile_source()` yang sudah ada:

```python
def _cmd_run(self) -> None:
    source = "\n".join(self._buffer)        # gabungkan buffer

    result = self._compiler.compile_source( # pipeline YANG SUDAH ADA
        source,
        source_path="<repl>",
        save_output=False,                  # tidak simpan ke disk
    )

    if result.success:
        exec(compile(result.python_code, "<repl>", "exec"), {})
```

Pipeline yang digunakan identik dengan mode file:
```
buffer → Lexer → Parser → Semantic → Optimizer → CodeGen → exec()
```

Setiap `:run` menjalankan kompilasi **fresh dari awal** (tidak incremental). Namespace `exec()` bersih setiap kali `:run` agar variabel tidak bocor antar sesi.

---

## 9. Contoh Program

### 01 — Halo Dunia

```joglang
wiwiti
    tampilna("Sugeng rawuh ing JogLang!")
    tampilna("Halo, Dunia!")
rampung
```

### 02 — Variabel & Tipe Data

```joglang
wiwiti
    angka    umur   = 20
    pecahan  tinggi = 170.5
    teks     nama   = "Budi Santoso"
    bener_salah aktif = bener

    tampilna(nama)
    tampilna(umur)
    tampilna(tinggi)
    tampilna(aktif)
rampung
```

### 03 — Aritmatika

```joglang
wiwiti
    angka a = 10
    angka b = 3
    tampilna(a + b)    // 13
    tampilna(a - b)    // 7
    tampilna(a * b)    // 30
    tampilna(a % b)    // 1
    tampilna(a ** b)   // 1000
rampung
```

### 04 — Kondisional

```joglang
wiwiti
    angka nilai = 85
    yen nilai >= 90 {
        tampilna("A")
    } liyane_yen nilai >= 80 {
        tampilna("B")
    } liyane_yen nilai >= 70 {
        tampilna("C")
    } liyane {
        tampilna("D atau E")
    }
rampung
```

### 05 — While Loop

```joglang
wiwiti
    angka i = 1
    angka jumlah = 0
    nalika i <= 100 {
        jumlah = jumlah + i
        i = i + 1
    }
    tampilna(jumlah)    // 5050
rampung
```

### 06 — For Loop

```joglang
wiwiti
    baleni angka i = 1 ; i <= 10 ; i += 1 {
        tampilna(i)
    }
rampung
```

### 07 — Fungsi

```joglang
wiwiti
    gawe tambah(angka a, angka b) {
        balekna a + b
    }
    gawe kuadrat(angka n) {
        balekna n * n
    }
    tampilna(tambah(3, 4))    // 7
    tampilna(kuadrat(5))      // 25
rampung
```

### 08 — Faktorial Rekursif

```joglang
wiwiti
    gawe faktorial(angka n) {
        yen n <= 1 { balekna 1 }
        balekna n * faktorial(n - 1)
    }
    tampilna(faktorial(5))     // 120
    tampilna(faktorial(10))    // 3628800
rampung
```

### 09 — Fibonacci

```joglang
wiwiti
    gawe fib(angka n) {
        yen n <= 0 { balekna 0 }
        yen n == 1 { balekna 1 }
        balekna fib(n - 1) + fib(n - 2)
    }
    baleni angka i = 0 ; i < 8 ; i += 1 {
        tampilna(fib(i))
    }
rampung
```

### 10 — Break & Continue

```joglang
wiwiti
    baleni angka i = 1 ; i <= 20 ; i += 1 {
        yen i % 2 == 0 { terusna }    // skip genap
        yen i > 10     { mandheg }    // berhenti di > 10
        tampilna(i)
    }
rampung
```

### 11 — Kalkulator

```joglang
wiwiti
    gawe bagi(pecahan a, pecahan b) {
        yen b == 0 {
            tampilna("Kesalahan: pembagi tidak boleh nol!")
            balekna 0
        }
        balekna a / b
    }
    tampilna(bagi(12, 4))    // 3.0
    bagi(10, 0)               // pesan error
rampung
```

### 12 — Bilangan Prima

```joglang
wiwiti
    gawe adalah_prima(angka n) {
        yen n < 2 { balekna salah }
        angka i = 2
        nalika i * i <= n {
            yen n % i == 0 { balekna salah }
            i = i + 1
        }
        balekna bener
    }
    baleni angka n = 2 ; n <= 50 ; n += 1 {
        yen adalah_prima(n) { tampilna(n) }
    }
rampung
```

---

## 10. Penanganan Error

Semua error mewarisi `JogLangError` dan menampilkan lokasi baris dan kolom:

```
[Baris 3, Kolom 12] TipeError: Pesan error
```

### LexicalError — Tahap Lexer

| Penyebab                | Contoh                          |
|-------------------------|---------------------------------|
| Karakter tidak dikenal  | `angka x = @5`                  |
| Keyword terlarang       | `print("halo")`                 |
| String tidak ditutup    | `teks s = "lupa tutup`          |

```
[Baris 1, Kolom 11] LexicalError: Karakter ilegal '@'
[Baris 1, Kolom 1]  LexicalError: 'print' adalah keyword terlarang...
```

### SyntaxError_ — Tahap Parser

| Penyebab                       | Contoh                        |
|--------------------------------|-------------------------------|
| Program tanpa `wiwiti`         | `angka x = 5 rampung`        |
| Program tanpa `rampung`        | `wiwiti angka x = 5`         |
| Blok tidak dibuka/ditutup      | `yen x > 0 tampilna(x)`      |
| Token tidak terduga            | `angka = 5` (tanpa nama)     |

```
[Baris 1, Kolom 1] SyntaxError_: Program harus dimulai dengan 'wiwiti'
[Baris 5, Kolom 3] SyntaxError_: Diharapkan '}', ditemukan 'rampung'
```

### SemanticError — Tahap Semantic

```
[Baris 3, Kolom 15] SemanticError: 'xyz' belum dideklarasikan.
[Baris 5, Kolom 5]  SemanticError: 'balekna' digunakan di luar fungsi.
[Baris 7, Kolom 3]  SemanticError: Fungsi 'hitung' butuh 2 argumen, diberikan 1.
[Baris 4, Kolom 5]  SemanticError: Type mismatch: 'teks' tidak bisa menerima 'angka'.
```

Semantic Analyzer mengumpulkan **semua error sekaligus** (tidak berhenti di error pertama), sehingga semua masalah dilaporkan dalam satu kali kompilasi.

### Runtime Error — Saat Eksekusi

Runtime error (pembagian nol, stack overflow, dll.) ditangkap oleh REPL dan CLI dengan pesan:

```
[Runtime Error] ZeroDivisionError: division by zero
```

Set environment variable `JOGLANG_DEBUG=1` untuk melihat full traceback Python.

---

## 11. Testing

Proyek memiliki **250 unit test** yang mencakup semua komponen.

### Menjalankan Test

```bash
# Semua test
python -m pytest tests/ -v

# Per modul
python -m pytest tests/test_lexer.py
python -m pytest tests/test_parser.py
python -m pytest tests/test_semantic.py
python -m pytest tests/test_optimizer.py
python -m pytest tests/test_compiler.py

# Ringkasan singkat
python -m pytest tests/ -q
```

### Distribusi Test

| File               | Jumlah | Mencakup                                                |
|--------------------|--------|---------------------------------------------------------|
| `test_lexer.py`    | 53     | Tokenisasi semua tipe token, keyword terlarang, error   |
| `test_parser.py`   | 55     | Parsing semua konstruksi, preseden operator, error      |
| `test_semantic.py` | 46     | 12 jenis pemeriksaan semantik, scope, type system       |
| `test_optimizer.py`| 50     | 5 teknik optimasi, statistik, kasus tepi               |
| `test_compiler.py` | 46     | Pipeline end-to-end, compile + run, error propagation  |
| **Total**          | **250**| |

### Contoh Test (test_optimizer.py)

```python
def test_fold_multiplication(self):
    """10 * 2 -> 20"""
    expr = first_expr("wiwiti angka x = 10 * 2 rampung")
    self.assertIsInstance(expr, LiteralNode)
    self.assertEqual(expr.value, 20)

def test_dead_code_while_false(self):
    """nalika salah { } -> dihapus"""
    prog = run_opt("wiwiti nalika salah { angka x = 1 } rampung")
    self.assertEqual(len(prog.body), 0)
```

---

## 12. Referensi API

### Penggunaan Programatik

```python
from joglang_compiler.compiler import Compiler, compile, compile_file

# Kompilasi dari string
result = compile("""
wiwiti
    tampilna("Halo dari API!")
rampung
""")

if result.success:
    print(result.python_code)
    print(f"Waktu: {result.elapsed_ms:.1f}ms")
    if result.opt_stats:
        print(result.opt_stats.summary())
else:
    print(f"Error di tahap {result.stage}: {result.error}")

# Kompilasi dari file
result = compile_file("examples/08_faktorial.jog")

# Dengan opsi lengkap
result = Compiler(
    verbose=True,      # simpan tokens & AST di result
    optimize=True,     # aktifkan optimizer
    output_dir="dist", # direktori output
).compile_source(source, source_path="program.jog", save_output=True)
```

### Menggunakan REPL Secara Programatik

```python
from joglang_compiler.repl import JogLangREPL, start_repl

# Cara 1 — shortcut
start_repl(examples_dir="examples", optimize=True)

# Cara 2 — class (lebih fleksibel)
repl = JogLangREPL(
    examples_dir="examples",
    optimize=True,
)
repl.run()
```

### Menggunakan Komponen Individual

```python
from joglang_compiler.lexer    import tokenize
from joglang_compiler.parser   import parse
from joglang_compiler.semantic import analyze
from joglang_compiler.optimizer import optimize
from joglang_compiler.codegen  import generate

# Pipeline manual
tokens        = tokenize(source)
ast           = parse(tokens)
analyze(ast)                          # raise SemanticError jika ada masalah
optimized, stats = optimize(ast)
python_code   = generate(optimized)

print(python_code)
print(stats.summary())
```

---

*Dokumentasi ini mencakup JogLang Compiler v1.0.0 secara lengkap.*  
*Dibuat sebagai bagian dari Proyek UAS Mata Kuliah Compiler Construction.*
