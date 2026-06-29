# Code Optimization — Dokumentasi Teknis

## Ikhtisar

Optimizer bekerja pada AST **setelah** Semantic Analyzer memvalidasinya. Tujuannya adalah menghasilkan kode Python yang lebih efisien tanpa mengubah **semantik** (makna) program.

File: `joglang_compiler/optimizer.py`

---

## Teknik yang Diimplementasikan

JogLang Optimizer mengimplementasikan **5 teknik optimasi**:

| No | Teknik                    | Keterangan                                    |
|----|---------------------------|-----------------------------------------------|
| 1  | Constant Folding          | Hitung ekspresi literal saat kompilasi       |
| 2  | Identity Optimization     | Eliminasi operasi identitas                  |
| 3  | Strength Reduction        | Ganti operasi mahal dengan yang lebih murah  |
| 4  | Dead Code Elimination     | Hapus kode yang tidak pernah dieksekusi      |
| 5  | Boolean Short-Circuit     | Sederhanakan ekspresi logika dengan literal  |

---

## 1. Constant Folding

Evaluasi ekspresi yang **kedua operannya adalah literal** pada waktu kompilasi — hasilnya ditulis langsung ke output.

### Aritmatika

| Sebelum        | Sesudah | Catatan                          |
|----------------|---------|----------------------------------|
| `5 + 3`        | `8`     | integer + integer = integer      |
| `10 - 4`       | `6`     |                                  |
| `10 * 2`       | `20`    |                                  |
| `9 / 3`        | `3`     | habis dibagi → int               |
| `10 / 3`       | `3.33…` | tidak habis → float              |
| `10 % 3`       | `1`     |                                  |
| `2 ** 10`      | `1024`  |                                  |
| `1.5 + 2.5`    | `4.0`   | float + float = float            |
| `3 + 1.5`      | `4.5`   | int + float = float              |

### Perbandingan

| Sebelum   | Sesudah  |
|-----------|----------|
| `5 == 5`  | `bener`  |
| `5 == 6`  | `salah`  |
| `3 < 5`   | `bener`  |
| `5 >= 5`  | `bener`  |

### String

| Sebelum               | Sesudah        |
|-----------------------|----------------|
| `"halo" + " dunia"`  | `"halo dunia"` |

### Logika

| Sebelum              | Sesudah  |
|----------------------|----------|
| `bener lan bener`    | `bener`  |
| `bener lan salah`    | `salah`  |
| `salah utawa bener`  | `bener`  |

### Unary

| Sebelum      | Sesudah  |
|--------------|----------|
| `-5`         | `-5`     |
| `ora bener`  | `salah`  |
| `ora salah`  | `bener`  |

### Folding Bertingkat

Constant folding diterapkan **bottom-up**, sehingga ekspresi bersarang juga terlipat:

```
(2 + 3) * (4 - 1)
= 5     * 3
= 15
```

```
1 + 2 + 3 + 4 = 10
```

---

## 2. Identity Optimization

Menghilangkan operasi yang tidak mengubah nilai (elemen identitas):

| Sebelum    | Sesudah | Aturan                  |
|------------|---------|-------------------------|
| `x + 0`    | `x`     | identitas penjumlahan   |
| `0 + x`    | `x`     | identitas penjumlahan   |
| `x - 0`    | `x`     |                         |
| `x * 1`    | `x`     | identitas perkalian     |
| `1 * x`    | `x`     | identitas perkalian     |
| `x / 1`    | `x`     |                         |
| `x ** 1`   | `x`     |                         |
| `x * 0`    | `0`     | zero property           |
| `0 * x`    | `0`     | zero property           |
| `x ** 0`   | `1`     | pangkat nol             |

---

## 3. Strength Reduction

Mengganti operasi mahal dengan operasi yang lebih murah secara komputasi:

| Sebelum   | Sesudah    | Penjelasan                              |
|-----------|------------|-----------------------------------------|
| `x ** 2`  | `x * x`    | Perkalian lebih cepat dari `pow()`     |

> Strength reduction hanya diterapkan saat `x` adalah `VariableNode` atau `LiteralNode` (tidak ada efek samping). Untuk sub-ekspresi kompleks, transformasi tidak dilakukan karena `x` akan dievaluasi dua kali.

---

## 4. Dead Code Elimination

Menghapus blok kode yang **tidak mungkin dieksekusi** berdasarkan kondisi literal:

### yen (if)

```joglang
// Sebelum:
yen bener {
    angka x = 1
} liyane {
    angka y = 999   // TIDAK PERNAH DIEKSEKUSI
}

// Sesudah: hanya then-branch yang dipertahankan
angka x = 1
```

```joglang
// Sebelum:
yen salah {
    angka x = 999   // TIDAK PERNAH DIEKSEKUSI
} liyane {
    angka y = 2
}

// Sesudah: hanya else-branch
angka y = 2
```

```joglang
// Sebelum:
yen salah {
    angka x = 999   // TIDAK PERNAH DIEKSEKUSI
}
// (tanpa else)

// Sesudah: seluruh if dihapus (tidak ada output)
```

### nalika (while)

```joglang
// Sebelum:
nalika salah {
    tampilna("tidak pernah")   // TIDAK PERNAH DIEKSEKUSI
}

// Sesudah: loop dihapus seluruhnya
```

> **Catatan:** Dead code elimination **hanya** pada kondisi literal (`bener`/`salah`). Jika kondisi berupa variabel atau ekspresi dinamis, blok dipertahankan.

---

## 5. Boolean Short-Circuit

Menyederhanakan ekspresi logika ketika salah satu operan adalah literal boolean:

### lan (and)

| Sebelum          | Sesudah   | Alasan                          |
|------------------|-----------|---------------------------------|
| `bener lan x`    | `x`       | true AND x = x                  |
| `salah lan x`    | `salah`   | false AND x = false (apapun x)  |
| `x lan bener`    | `x`       | x AND true = x                  |
| `x lan salah`    | `salah`   | x AND false = false             |

### utawa (or)

| Sebelum          | Sesudah   | Alasan                         |
|------------------|-----------|--------------------------------|
| `bener utawa x`  | `bener`   | true OR x = true (apapun x)   |
| `salah utawa x`  | `x`       | false OR x = x                 |
| `x utawa bener`  | `bener`   | x OR true = true               |
| `x utawa salah`  | `x`       | x OR false = x                 |

---

## Statistik Optimasi

`OptimizationStats` mencatat jumlah tiap kategori optimasi:

```python
@dataclass
class OptimizationStats:
    constant_folds:      int = 0
    identity_opts:       int = 0
    strength_reductions: int = 0
    dead_code_removed:   int = 0
    total:               int = 0

    def summary(self) -> str:
        return (
            f"Optimasi selesai: {self.total} total | "
            f"{self.constant_folds} constant fold | "
            f"{self.identity_opts} identity | "
            f"{self.strength_reductions} strength reduction | "
            f"{self.dead_code_removed} dead code removed"
        )
```

Contoh output verbose:
```
▶ Optimizer...
  ✓ Optimasi selesai: 4 total | 3 constant fold | 1 identity | 0 strength reduction | 0 dead code removed
```

---

## Implementasi: Visitor Pattern

Optimizer menggunakan pola yang berbeda dari visitor standar: setiap `_opt_*()` **mengembalikan node baru** (bukan void). Ini memungkinkan penggantian node secara non-destruktif.

```python
class Optimizer:
    def _opt(self, node: Optional[ASTNode]) -> Optional[ASTNode]:
        """Dispatch ke _opt_NamaNode()."""
        method = getattr(self, f"_opt_{type(node).__name__}", self._opt_default)
        return method(node)

    def _opt_BinaryOperationNode(self, node):
        left  = self._opt(node.left)
        right = self._opt(node.right)

        # 1. Constant Folding
        if is_literal(left) and is_literal(right):
            result = fold(node.operator, left.value, right.value)
            if result is not None:
                self.stats.record("fold")
                return result

        # 2. Identity Optimization
        identity = try_identity(node.operator, left, right)
        if identity is not None:
            return identity

        # ... dst
        return BinaryOperationNode(left=left, operator=node.operator, right=right)
```

---

## Penggunaan API

```python
from joglang_compiler.optimizer import Optimizer, optimize

# Cara 1 — class
opt           = Optimizer()
optimized_ast = opt.optimize(ast)
print(opt.stats.summary())

# Cara 2 — shortcut
optimized_ast, stats = optimize(ast)
print(stats.total, "optimasi dilakukan")
```

---

## Batas Optimizer

Optimizer JogLang saat ini bersifat **single-pass** dan tidak mengimplementasikan:
- Constant Propagation penuh (melacak nilai variabel antar-statement)
- Loop Unrolling
- Inlining fungsi
- Common Subexpression Elimination

Optimasi-optimasi lanjutan ini dapat ditambahkan di versi mendatang.
