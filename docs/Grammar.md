# JogLang Grammar (EBNF)

## Grammar Lengkap

```ebnf
(*─────────────────────────────────────────────────────────────────*)
(*  JogLang Grammar — EBNF (Extended Backus-Naur Form)            *)
(*  Versi: 1.0.0                                                   *)
(*─────────────────────────────────────────────────────────────────*)

(*── Program ──────────────────────────────────────────────────────*)

program         ::= 'wiwiti' statement* 'rampung'

(*── Statements ───────────────────────────────────────────────────*)

statement       ::= var_decl
                  | assignment_stmt
                  | print_stmt
                  | if_stmt
                  | while_stmt
                  | for_stmt
                  | function_decl
                  | return_stmt
                  | break_stmt
                  | continue_stmt
                  | call_stmt
                  | ';'

(*── Variable Declaration ─────────────────────────────────────────*)

var_decl        ::= datatype IDENTIFIER ('=' expression)? ';'?
datatype        ::= 'angka' | 'pecahan' | 'teks' | 'bener_salah'

(*── Assignment ───────────────────────────────────────────────────*)

assignment_stmt ::= IDENTIFIER assign_op expression ';'?
assign_op       ::= '=' | '+=' | '-=' | '*=' | '/='

(*── I/O ──────────────────────────────────────────────────────────*)

print_stmt      ::= 'tampilna' '(' expression ')' ';'?
input_expr      ::= 'takon' '(' expression? ')'

(*── Control Flow ─────────────────────────────────────────────────*)

if_stmt         ::= 'yen' expression block
                    ('liyane_yen' expression block)*
                    ('liyane' block)?

while_stmt      ::= 'nalika' expression block

for_stmt        ::= 'baleni' for_init ';' expression ';' for_update block
for_init        ::= var_decl_no_semi | assignment_no_semi
for_update      ::= assignment_no_semi

var_decl_no_semi  ::= datatype IDENTIFIER ('=' expression)?
assignment_no_semi ::= IDENTIFIER assign_op expression

(*── Functions ────────────────────────────────────────────────────*)

function_decl   ::= 'gawe' IDENTIFIER '(' param_list? ')' block
param_list      ::= param (',' param)*
param           ::= datatype IDENTIFIER
call_stmt       ::= IDENTIFIER '(' arg_list? ')' ';'?
arg_list        ::= expression (',' expression)*

return_stmt     ::= 'balekna' expression? ';'?
break_stmt      ::= 'mandheg' ';'?
continue_stmt   ::= 'terusna' ';'?

(*── Block ────────────────────────────────────────────────────────*)

block           ::= '{' statement* '}'

(*── Expressions (operator precedence, low → high) ────────────────*)

expression      ::= or_expr

or_expr         ::= and_expr ('utawa' and_expr)*

and_expr        ::= not_expr ('lan' not_expr)*

not_expr        ::= 'ora' not_expr
                  | comparison

comparison      ::= addition (cmp_op addition)*
cmp_op          ::= '==' | '!=' | '<' | '>' | '<=' | '>='

addition        ::= multiplication (('+' | '-') multiplication)*

multiplication  ::= power (('*' | '/' | '%') power)*

power           ::= unary ('**' unary)*           (* right-associative *)

unary           ::= '-' unary
                  | primary

primary         ::= INT_LIT
                  | FLOAT_LIT
                  | STRING_LIT
                  | 'bener'
                  | 'salah'
                  | 'kosong'
                  | IDENTIFIER '(' arg_list? ')'  (* function call *)
                  | IDENTIFIER                     (* variable *)
                  | '(' expression ')'             (* grouped *)
                  | input_expr

(*── Terminals ────────────────────────────────────────────────────*)

IDENTIFIER      ::= [a-zA-Z_][a-zA-Z0-9_]*
INT_LIT         ::= [0-9]+
FLOAT_LIT       ::= [0-9]+ '.' [0-9]+
STRING_LIT      ::= '"' ( [^"\\] | '\\' . )* '"'
                  | "'" ( [^'\\] | '\\' . )* "'"
COMMENT         ::= '//' [^\n]*
                  | '/*' .* '*/'
```

---

## Operator Precedence Table

| Preseden | Operator                      | Asosiasi  |
|----------|-------------------------------|-----------|
| 1 (rendah) | `utawa`                     | Kiri      |
| 2        | `lan`                         | Kiri      |
| 3        | `ora` (unary prefix)          | Kanan     |
| 4        | `==` `!=` `<` `>` `<=` `>=`  | Kiri      |
| 5        | `+` `-`                       | Kiri      |
| 6        | `*` `/` `%`                   | Kiri      |
| 7        | `**`                          | **Kanan** |
| 8        | `-` (unary prefix)            | Kanan     |
| 9 (tinggi) | literal, identifier, `()`   | —         |

### Contoh Preseden

```
2 + 3 * 4         = 2 + (3 * 4)           = 14
2 ** 3 ** 2       = 2 ** (3 ** 2)         = 512   (kanan-asosiatif)
ora bener lan x   = (ora bener) lan x      = salah lan x
x > 0 lan y > 0  = (x > 0) lan (y > 0)
```

---

## Keyword Lengkap

| Token         | Lexeme        | Kategori     |
|---------------|---------------|--------------|
| `WIWITI`      | `wiwiti`      | Program      |
| `RAMPUNG`     | `rampung`     | Program      |
| `GAWE`        | `gawe`        | Fungsi       |
| `BALEKNA`     | `balekna`     | Fungsi       |
| `YEN`         | `yen`         | Kondisional  |
| `LIYANE_YEN`  | `liyane_yen`  | Kondisional  |
| `LIYANE`      | `liyane`      | Kondisional  |
| `NALIKA`      | `nalika`      | Loop         |
| `BALENI`      | `baleni`      | Loop         |
| `MANDHEG`     | `mandheg`     | Loop control |
| `TERUSNA`     | `terusna`     | Loop control |
| `TAMPILNA`    | `tampilna`    | I/O          |
| `TAKON`       | `takon`       | I/O          |
| `DATATYPE_INT`| `angka`       | Tipe data    |
| `DATATYPE_FLOAT`| `pecahan`   | Tipe data    |
| `DATATYPE_STR`| `teks`        | Tipe data    |
| `DATATYPE_BOOL`| `bener_salah`| Tipe data    |
| `TRUE`        | `bener`       | Literal      |
| `FALSE`       | `salah`       | Literal      |
| `NULL`        | `kosong`      | Literal      |
| `LAN`         | `lan`         | Logika       |
| `UTAWA`       | `utawa`       | Logika       |
| `ORA`         | `ora`         | Logika       |

---

## Keyword Terlarang

Keyword berikut **tidak boleh** digunakan dalam program JogLang. Penggunaan akan menghasilkan `LexicalError`:

```
# Python
print input if else elif while for return def class
True False None and or not in is global import lambda

# Java
System println public static void int float boolean String
Scanner null true false new this

# C/C++
printf scanf cout cin include namespace

# JavaScript
var let const function console log undefined

# C#
Console WriteLine ReadLine
```

---

## Contoh Program

### Minimal

```joglang
wiwiti
rampung
```

### Dengan Semua Konstruksi

```joglang
wiwiti
    // Variabel
    angka angkaku    = 42
    pecahan pecahku  = 3.14
    teks teksku      = "Halo"
    bener_salah flag = bener

    // Fungsi
    gawe kuadrat(angka x) {
        balekna x * x
    }

    // Kondisional
    yen flag lan angkaku > 0 {
        tampilna("Positif!")
    } liyane {
        tampilna("Negatif.")
    }

    // For loop
    baleni angka i = 1 ; i <= 5 ; i += 1 {
        yen i % 2 == 0 { terusna }
        tampilna(kuadrat(i))
    }

    // While loop
    angka j = 10
    nalika j > 0 {
        j = j - 3
        yen j < 0 { mandheg }
    }

    // Input
    teks nama = takon("Nama: ")
    tampilna("Halo, " + nama)
rampung
```
