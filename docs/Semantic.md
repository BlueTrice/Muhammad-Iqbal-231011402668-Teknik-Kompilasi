# Semantic Analysis — Dokumentasi Teknis

## Ikhtisar

Analisis Semantik adalah tahap ketiga kompilasi JogLang. Parser hanya memverifikasi **struktur** kode (sintaks). Semantic Analyzer memverifikasi **makna** kode — apakah konstruksi yang secara sintaksis valid juga bermakna secara logika.

File: `joglang_compiler/semantic.py`

---

## Apa yang Diperiksa?

| No | Pemeriksaan                      | Contoh Error                               |
|----|----------------------------------|--------------------------------------------|
| 1  | Variabel belum dideklarasikan    | `tampilna(x)` — `x` tidak ada            |
| 2  | Redeklarasi variabel (scope sama)| `angka x = 1` dua kali berturutan         |
| 3  | Fungsi belum dideklarasikan      | `hasil()` — `hasil` tidak ada            |
| 4  | Jumlah argumen salah             | `tambah(1)` — fungsi butuh 2 argumen     |
| 5  | Memanggil variabel sebagai fungsi| `angka x = 5` lalu `x()`                |
| 6  | Assign ke fungsi                 | `gawe f() {...}` lalu `f = 5`            |
| 7  | Type mismatch pada deklarasi     | `teks nama = 42`                          |
| 8  | Type mismatch pada assignment    | `angka x = 5` lalu `x = "halo"`         |
| 9  | `balekna` di luar fungsi         | `wiwiti balekna 5 rampung`               |
| 10 | `mandheg` di luar loop           | `wiwiti mandheg rampung`                 |
| 11 | `terusna` di luar loop           | `wiwiti terusna rampung`                 |
| 12 | Operator `ora` pada non-boolean  | `ora 42` — hanya valid untuk bener_salah |

---

## Arsitektur

### Symbol Table

Symbol table menyimpan semua simbol (variabel dan fungsi) yang dideklarasikan:

```python
class SymbolInfo:
    name:     str            # nama simbol
    kind:     str            # 'variable' | 'function'
    var_type: Optional[str]  # 'angka' | 'pecahan' | 'teks' | 'bener_salah'
    params:   list           # [ParameterNode] — untuk fungsi
    line:     int
    column:   int
```

### Scope Bersarang

`Scope` mengimplementasikan **lexical scoping** dengan parent-chaining:

```
Scope global
  ├── x: angka
  ├── tambah: function
  └── Scope fungsi (tambah)
        ├── a: angka
        ├── b: angka
        └── Scope if (di dalam tambah)
              └── temp: angka
```

```python
class Scope:
    def define(self, symbol: SymbolInfo) -> None:
        # Cek redeklarasi di scope LOKAL saja
        if symbol.name in self._symbols:
            raise SemanticError("Redeklarasi ...")
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        # Cari dari scope ini ke atas (parent)
        if name in self._symbols:
            return self._symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
```

Redeklarasi hanya error jika di **scope yang sama**. Variabel dengan nama sama di scope berbeda diizinkan.

### Visitor Pattern

`SemanticAnalyzer` mengimplementasikan `ASTVisitor`. Setiap node dikunjungi:

```python
class SemanticAnalyzer(ASTVisitor):
    def visit_VariableDeclarationNode(self, node): ...
    def visit_AssignmentNode(self, node):          ...
    def visit_FunctionNode(self, node):            ...
    def visit_CallNode(self, node):                ...
    def visit_ReturnNode(self, node):              ...
    def visit_BreakNode(self, node):               ...
    # ... dst
```

### Error Accumulation

Analyzer **mengumpulkan semua error** sebelum melempar exception (bukan berhenti di error pertama):

```python
def analyze(self, node: ProgramNode) -> None:
    self._errors = []
    self.visit_ProgramNode(node)

    if self._errors:
        first    = self._errors[0]
        messages = "\n".join(str(e) for e in self._errors)
        raise SemanticError(
            f"Ditemukan {len(self._errors)} kesalahan semantik:\n{messages}",
            line=first.line, column=first.column,
        )
```

---

## Sistem Tipe (Type System)

JogLang menggunakan **static typing** dasar. Tipe diinferensikan dari ekspresi:

### Mapping Tipe

| JogLang     | Inferensi dari                              |
|-------------|---------------------------------------------|
| `angka`     | `INT_LIT`, deklarasi `angka`               |
| `pecahan`   | `FLOAT_LIT`, deklarasi `pecahan`           |
| `teks`      | `STRING_LIT`, deklarasi `teks`             |
| `bener_salah` | `bener`/`salah`, deklarasi `bener_salah` |
| `kosong`    | `kosong`, return type tidak diketahui      |

### Aturan Kompatibilitas

```
angka   op angka   → angka
pecahan op pecahan → pecahan
angka   op pecahan → pecahan    (numeric widening)
pecahan op angka   → pecahan    (numeric widening)
teks    +  teks    → teks       (concatenation)
any    == any      → bener_salah
any    != any      → bener_salah
bener_salah lan bener_salah → bener_salah
bener_salah utawa bener_salah → bener_salah
```

Assignment: `angka = pecahan` dan `pecahan = angka` diizinkan (numeric widening).

---

## State Tracking

Analyzer melacak konteks eksekusi:

```python
self._in_function: bool = False  # sedang di dalam fungsi?
self._in_loop:     int  = 0      # kedalaman loop (>0 = dalam loop)
```

- `_in_function` diset True saat masuk `FunctionNode`, kembali False saat keluar
- `_in_loop` dinaikkan saat masuk `WhileNode`/`ForNode`, diturunkan saat keluar
- `balekna` hanya valid saat `_in_function == True`
- `mandheg`/`terusna` hanya valid saat `_in_loop > 0`

---

## Contoh Error

```joglang
wiwiti
    angka x = 5
    teks y = x          // [Baris 3] type mismatch: 'teks' vs 'angka'
    tampilna(z)         // [Baris 4] 'z' belum dideklarasikan
    balekna 10          // [Baris 5] 'balekna' di luar fungsi
rampung
```

Output error (semua dikumpulkan):
```
SemanticError: Ditemukan 3 kesalahan semantik:
[Baris 3, Kolom 5] SemanticError: Type mismatch: 'teks' tidak bisa menerima 'angka'
[Baris 4, Kolom 15] SemanticError: 'z' belum dideklarasikan.
[Baris 5, Kolom 5] SemanticError: 'balekna' digunakan di luar fungsi.
```

---

## Penggunaan API

```python
from joglang_compiler.semantic import SemanticAnalyzer, analyze

# Cara 1 — class
analyzer = SemanticAnalyzer()
analyzer.analyze(ast)   # raise SemanticError jika ada masalah

# Cara 2 — shortcut
analyze(ast)
```
