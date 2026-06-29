# Parser — Dokumentasi Teknis

## Ikhtisar

Parser menerima daftar Token dari Lexer dan membangun **Abstract Syntax Tree (AST)**. JogLang menggunakan teknik **Recursive Descent Parsing** (top-down parsing).

File: `joglang_compiler/parser.py`

---

## Teknik: Recursive Descent Parser

Setiap aturan grammar diimplementasikan sebagai satu fungsi Python yang memanggil fungsi lain secara rekursif. Fungsi-fungsi ini sesuai dengan hierarki aturan grammar.

```
parse()              ← entry point
  └─ _parse_program()
       └─ _parse_statement()
            ├─ _parse_var_decl()
            ├─ _parse_assignment()
            ├─ _parse_print()
            ├─ _parse_if()
            │    └─ _parse_expression() → _parse_or() → ... → _parse_primary()
            ├─ _parse_while()
            ├─ _parse_for()
            └─ _parse_function_decl()
```

---

## Grammar (EBNF)

```ebnf
program         ::= 'wiwiti' statement* 'rampung'

statement       ::= var_decl | assignment_stmt | print_stmt
                  | if_stmt  | while_stmt       | for_stmt
                  | function_decl | return_stmt
                  | break_stmt   | continue_stmt | call_stmt

var_decl        ::= datatype IDENTIFIER ('=' expression)? ';'?
assignment_stmt ::= IDENTIFIER assign_op expression ';'?
assign_op       ::= '=' | '+=' | '-=' | '*=' | '/='

print_stmt      ::= 'tampilna' '(' expression ')' ';'?

if_stmt         ::= 'yen' expression block
                    ('liyane_yen' expression block)*
                    ('liyane' block)?

while_stmt      ::= 'nalika' expression block
for_stmt        ::= 'baleni' for_init ';' expression ';' for_update block

function_decl   ::= 'gawe' IDENTIFIER '(' param_list? ')' block
param_list      ::= param (',' param)*
param           ::= datatype IDENTIFIER

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
power           ::= unary ('**' unary)*          (* right-assoc *)
unary           ::= '-' unary | primary
primary         ::= INT_LIT | FLOAT_LIT | STRING_LIT
                  | 'bener' | 'salah' | 'kosong'
                  | IDENTIFIER '(' arg_list? ')'
                  | IDENTIFIER
                  | '(' expression ')'
                  | input_expr

input_expr      ::= 'takon' '(' expression? ')'
arg_list        ::= expression (',' expression)*
datatype        ::= 'angka' | 'pecahan' | 'teks' | 'bener_salah'
```

---

## Operator Precedence

Dari preseden **rendah → tinggi** (ekspresi `or` paling longgar, `primary` paling ketat):

| Level | Operator           | Fungsi parser         | Asosiasi    |
|-------|--------------------|-----------------------|-------------|
| 1     | `utawa`            | `_parse_or()`         | Kiri        |
| 2     | `lan`              | `_parse_and()`        | Kiri        |
| 3     | `ora` (unary)      | `_parse_not()`        | Kanan       |
| 4     | `==` `!=` `<` `>` `<=` `>=` | `_parse_comparison()` | Kiri |
| 5     | `+` `-`            | `_parse_addition()`   | Kiri        |
| 6     | `*` `/` `%`        | `_parse_multiplication()` | Kiri    |
| 7     | `**`               | `_parse_power()`      | **Kanan**   |
| 8     | `-` (unary)        | `_parse_unary()`      | Kanan       |
| 9     | literal, id, `()`  | `_parse_primary()`    | —           |

Contoh: `2 + 3 * 4` dibaca sebagai `2 + (3 * 4) = 14` ✓

---

## Helper Methods

| Method         | Fungsi                                           |
|----------------|--------------------------------------------------|
| `_current`     | Token aktif (tanpa maju)                        |
| `_peek`        | Token berikutnya (lookahead 1, tanpa maju)       |
| `_advance()`   | Ambil token aktif lalu maju                     |
| `_check(*types)`| True jika token aktif bertipe salah satu       |
| `_match(*types)`| Jika cocok: maju & return True                 |
| `_expect(type)`| Maju jika cocok, lempar SyntaxError_ jika tidak |
| `_skip_semicolons()` | Lewati `;` opsional                       |

---

## Pembedaan: Assignment vs Expression Statement

Ketika parser menemukan IDENTIFIER, perlu membedakan dua kasus:

```
IDENTIFIER '=' ...       → AssignmentNode
IDENTIFIER '(' ... ')'  → CallNode (fungsi call)
IDENTIFIER               → VariableNode (referensi variabel)
```

Caranya dengan **lookahead 1 token**:

```python
if self._check(IDENTIFIER) and self._peek.type in ASSIGN_OPS:
    return self._parse_assignment()
# else → expression statement (CallNode atau VariableNode)
```

---

## Penanganan Error

Jika token tidak sesuai ekspektasi, `_expect()` melempar `SyntaxError_`:

```python
def _expect(self, token_type: TokenType, message: str = "") -> Token:
    if self._check(token_type):
        return self._advance()
    tok = self._current
    raise SyntaxError_(
        message or f"Diharapkan '{token_type.name}', ditemukan '{tok.lexeme}'",
        line=tok.line, column=tok.column,
    )
```

Format pesan error:
```
[Baris 5, Kolom 3] SyntaxError_: Diharapkan 'RBRACE', ditemukan 'rampung'
[Baris 1, Kolom 1] SyntaxError_: Program harus dimulai dengan 'wiwiti'
```

---

## Penggunaan API

```python
from joglang_compiler.lexer  import tokenize
from joglang_compiler.parser import Parser, parse

tokens = tokenize(source_code)

# Cara 1 — class
ast = Parser(tokens).parse()

# Cara 2 — shortcut function
ast = parse(tokens)
```

---

## Contoh Parsing

Source code:
```joglang
wiwiti
    angka x = 5 + 3
    tampilna(x)
rampung
```

Hasil AST (disederhanakan):
```
ProgramNode(
  body=[
    VariableDeclarationNode(
      var_type='angka', name='x',
      initializer=BinaryOperationNode(
        left=LiteralNode(value=5, kind='int'),
        operator='+',
        right=LiteralNode(value=3, kind='int')
      )
    ),
    PrintNode(
      expression=VariableNode(name='x')
    )
  ]
)
```
