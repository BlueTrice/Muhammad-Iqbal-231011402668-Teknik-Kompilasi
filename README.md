# Muhammad-Iqbal-231011402668-Teknik-Kompilasi
Mini Compiler Bahasa Jawa Dialek Yogyakarta

# JogLang Compiler

Mini Compiler berbasis **Python** yang menggunakan **Bahasa Jawa Dialek Yogyakarta** sebagai bahasa pemrograman. Proyek ini dibuat sebagai **Ujian Akhir Semester (UAS) Mata Kuliah Teknik Kompilasi**.

JogLang mengimplementasikan tahapan compiler secara lengkap, mulai dari **Lexical Analysis**, **Parsing**, **Abstract Syntax Tree (AST)**, **Semantic Analysis**, **Code Optimization**, hingga **Code Generation**, kemudian menghasilkan source code Python yang dapat langsung dijalankan.

---

## ✨ Features

* Interactive REPL
* Lexer (Lexical Analysis)
* Recursive Descent Parser
* Abstract Syntax Tree (AST)
* Semantic Analyzer
* Code Optimizer
* Python Code Generator
* Installer Windows & Linux/macOS
* Deteksi keyword bahasa lain (misalnya `print`, `if`, `while`, dll.)

---

## 🚀 Installation

Clone repository:

```bash
git clone https://github.com/USERNAME/joglang-compiler.git
cd joglang-compiler
```

Install compiler:

```bash
py -m pip install .
```

atau gunakan installer:

**Windows**

```text
install_windows.bat
```

**Linux / macOS**

```bash
chmod +x install_unix.sh
./install_unix.sh
```

---

## ▶️ Menjalankan Compiler

### Interactive REPL

```bash
py main.py
```

atau

```bash
python -m joglang_compiler
```

Setelah masuk REPL:

```
wiwiti
tampilna "Halo Dunia"
rampung

:run
```

---

### Compile File

```bash
py main.py examples\01_halo_dunia.jog
```

atau

```bash
python -m joglang_compiler examples/01_halo_dunia.jog
```

---

## 📖 Kamus JogLang

| JogLang       | Python        | Arti                |
| ------------- | ------------- | ------------------- |
| `wiwiti`      | Awal Program  | Mulai               |
| `rampung`     | Akhir Program | Selesai             |
| `tampilna`    | `print()`     | Tampilkan           |
| `takon`       | `input()`     | Input               |
| `gawe`        | `def`         | Membuat fungsi      |
| `balekna`     | `return`      | Mengembalikan nilai |
| `yen`         | `if`          | Jika                |
| `liyane_yen`  | `elif`        | Selain jika         |
| `liyane`      | `else`        | Selain itu          |
| `nalika`      | `while`       | Selama              |
| `baleni`      | `for`         | Ulangi              |
| `mandheg`     | `break`       | Berhenti            |
| `terusna`     | `continue`    | Lanjutkan           |
| `angka`       | `int`         | Bilangan bulat      |
| `pecahan`     | `float`       | Bilangan desimal    |
| `teks`        | `str`         | Teks                |
| `bener_salah` | `bool`        | Boolean             |
| `bener`       | `True`        | Benar               |
| `salah`       | `False`       | Salah               |
| `kosong`      | `None`        | Nilai kosong        |
| `lan`         | `and`         | Dan                 |
| `utawa`       | `or`          | Atau                |
| `ora`         | `not`         | Tidak               |

---

## 💻 Contoh Program

```joglang
wiwiti

tampilna "Sugeng Rawuh ing JogLang!"
tampilna "Halo Dunia"

rampung
```

Output:

```
Sugeng Rawuh ing JogLang!
Halo Dunia
```

---

## 🔄 Compiler Pipeline

```
Source Code (.jog / REPL)
        │
        ▼
Lexical Analysis
        │
        ▼
Parsing
        │
        ▼
Abstract Syntax Tree (AST)
        │
        ▼
Semantic Analysis
        │
        ▼
Code Optimization
        │
        ▼
Code Generation
        │
        ▼
Python Code
        │
        ▼
Program Output
```

---

## 📁 Project Structure

```
joglang_project/
│
├── joglang_compiler/
├── examples/
├── output/
├── tests/
├── docs/
├── main.py
├── pyproject.toml
└── README.md
```

---

## 👨‍💻 Author

**Muhammad Iqbal**
NIM: **231011402668**
Teknik Informatika — Universitas Pamulang

---
