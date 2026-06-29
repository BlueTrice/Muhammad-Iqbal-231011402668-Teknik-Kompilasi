# Panduan Pengguna JogLang

## 1. Instalasi

### Windows
```bat
install_windows.bat
```

### Linux / macOS
```bash
chmod +x install_unix.sh
./install_unix.sh
```

### Manual
```bash
pip install .
```

Verifikasi instalasi:
```bash
joglang --version
# JogLang Compiler v1.0.0
```

---

## 2. Struktur Program

Setiap program JogLang **wajib** diawali `wiwiti` dan diakhiri `rampung`:

```joglang
wiwiti
    // kode program di sini
rampung
```

---

## 3. Tipe Data

| Keyword      | Tipe      | Contoh nilai               |
|--------------|-----------|----------------------------|
| `angka`      | Integer   | `42`, `-7`, `0`            |
| `pecahan`    | Float     | `3.14`, `-0.5`, `100.0`    |
| `teks`       | String    | `"Halo"`, `'Dunia'`        |
| `bener_salah`| Boolean   | `bener`, `salah`           |

---

## 4. Variabel

### Deklarasi dengan nilai awal

```joglang
angka    umur    = 20
pecahan  tinggi  = 170.5
teks     nama    = "Budi"
bener_salah aktif = bener
```

### Deklarasi tanpa nilai awal (kosong/None)

```joglang
angka x
teks  pesan
```

### Assignment

```joglang
x = 10
x += 5     // x = x + 5
x -= 2     // x = x - 2
x *= 3     // x = x * 3
x /= 2     // x = x / 2
```

---

## 5. Komentar

```joglang
// komentar satu baris

/* komentar
   beberapa baris */
```

---

## 6. Operator

### Aritmatika

```joglang
angka a = 10
angka b = 3

tampilna(a + b)    // 13
tampilna(a - b)    // 7
tampilna(a * b)    // 30
tampilna(a / b)    // 3.3333...
tampilna(a % b)    // 1  (sisa bagi)
tampilna(a ** b)   // 1000  (pangkat)
```

### Perbandingan (menghasilkan bener/salah)

```joglang
tampilna(5 == 5)   // bener
tampilna(5 != 6)   // bener
tampilna(3 < 5)    // bener
tampilna(5 > 10)   // salah
tampilna(5 <= 5)   // bener
tampilna(6 >= 7)   // salah
```

### Logika

```joglang
bener_salah a = bener
bener_salah b = salah

tampilna(a lan b)   // salah  (and)
tampilna(a utawa b) // bener  (or)
tampilna(ora a)     // salah  (not)
```

---

## 7. Input & Output

### Output (tampilna)

```joglang
tampilna("Halo, Dunia!")        // teks literal
tampilna(42)                     // angka
tampilna(x)                      // variabel
tampilna("Nilai: " + nama)       // concatenation
tampilna(3 + 4)                  // ekspresi
```

### Input (takon)

```joglang
teks nama  = takon("Masukkan nama: ")
teks jawab = takon()              // tanpa prompt
```

> **Catatan:** `takon` selalu mengembalikan teks. Untuk mendapat angka, kompilasi ke Python dan lakukan konversi manual jika diperlukan.

---

## 8. Kondisional

### if sederhana

```joglang
yen x > 0 {
    tampilna("positif")
}
```

### if-else

```joglang
yen x > 0 {
    tampilna("positif")
} liyane {
    tampilna("nol atau negatif")
}
```

### if-elif-else

```joglang
angka nilai = 85

yen nilai >= 90 {
    tampilna("A")
} liyane_yen nilai >= 80 {
    tampilna("B")
} liyane_yen nilai >= 70 {
    tampilna("C")
} liyane_yen nilai >= 60 {
    tampilna("D")
} liyane {
    tampilna("E")
}
```

---

## 9. Loop While

```joglang
angka i = 1
nalika i <= 10 {
    tampilna(i)
    i = i + 1
}
```

Loop tak terbatas (dengan mandheg):

```joglang
angka n = 0
nalika bener {
    n = n + 1
    yen n >= 5 {
        mandheg        // keluar dari loop
    }
}
```

---

## 10. Loop For

Sintaks: `baleni init ; kondisi ; update { }`

```joglang
baleni angka i = 1 ; i <= 10 ; i += 1 {
    tampilna(i)
}
```

Dengan `terusna` (continue):

```joglang
baleni angka i = 1 ; i <= 10 ; i += 1 {
    yen i % 2 == 0 {
        terusna        // skip bilangan genap
    }
    tampilna(i)        // hanya bilangan ganjil: 1 3 5 7 9
}
```

---

## 11. Fungsi

### Definisi fungsi

```joglang
gawe sapa(teks nama) {
    tampilna("Halo, " + nama + "!")
}
```

### Fungsi dengan nilai kembalian

```joglang
gawe tambah(angka a, angka b) {
    balekna a + b
}

angka hasil = tambah(3, 4)
tampilna(hasil)    // 7
```

### Fungsi rekursif

```joglang
gawe faktorial(angka n) {
    yen n <= 1 {
        balekna 1
    }
    balekna n * faktorial(n - 1)
}

tampilna(faktorial(5))    // 120
```

### Pemanggilan fungsi dalam ekspresi

```joglang
tampilna(tambah(tambah(1, 2), 3))   // 6
angka x = faktorial(5) + faktorial(3)
```

---

## 12. Break & Continue

### mandheg (break) — keluar dari loop

```joglang
baleni angka i = 0 ; i < 100 ; i += 1 {
    yen i == 10 {
        mandheg    // berhenti di i=10
    }
    tampilna(i)
}
```

### terusna (continue) — lanjut ke iterasi berikutnya

```joglang
baleni angka i = 1 ; i <= 20 ; i += 1 {
    yen i % 3 != 0 {
        terusna    // skip yang bukan kelipatan 3
    }
    tampilna(i)    // 3 6 9 12 15 18
}
```

---

## 13. Menggunakan CLI

```bash
# Kompilasi saja (simpan ke output/)
joglang contoh.jog

# Kompilasi + langsung jalankan
joglang contoh.jog --run

# Pilih direktori output
joglang contoh.jog -o hasil/

# Tampilkan progress setiap tahap
joglang contoh.jog --verbose

# Nonaktifkan optimizer (untuk debug)
joglang contoh.jog --no-optimize

# Debug: lihat daftar token
joglang contoh.jog --tokens

# Debug: lihat AST
joglang contoh.jog --ast

# Tampilkan versi
joglang --version

# Bantuan
joglang --help
```

---

## 14. Memahami Error

### LexicalError — karakter/keyword ilegal

```
[Baris 2, Kolom 14] LexicalError: Karakter ilegal '@'
[Baris 3, Kolom 5]  LexicalError: Keyword 'print' dilarang — gunakan 'tampilna'
```

### SyntaxError_ — struktur tidak valid

```
[Baris 1, Kolom 1] SyntaxError_: Program harus dimulai dengan 'wiwiti'
[Baris 5, Kolom 3] SyntaxError_: Diharapkan '}', ditemukan 'rampung'
```

### SemanticError — makna tidak valid

```
[Baris 3, Kolom 15] SemanticError: 'x' belum dideklarasikan
[Baris 4, Kolom 5]  SemanticError: 'balekna' digunakan di luar fungsi
[Baris 6, Kolom 3]  SemanticError: Fungsi 'hitung' butuh 2 argumen, diberikan 1
```

---

## 15. Aturan Penting

1. **Keyword asing dilarang** — `print`, `if`, `return`, `True`, `null`, dll. menyebabkan LexicalError
2. **Tipe data wajib** saat deklarasi variabel baru
3. **wiwiti dan rampung wajib** membungkus seluruh program
4. **Blok kode dengan `{ }`** — bukan indentasi seperti Python
5. **Titik koma `;` opsional** kecuali sebagai pemisah di dalam `baleni`
6. **Variabel belum dideklarasikan** tidak bisa digunakan
7. **`balekna` hanya di dalam fungsi** — di luar fungsi menyebabkan SemanticError
8. **`mandheg` dan `terusna` hanya di dalam loop** — di luar loop menyebabkan SemanticError
