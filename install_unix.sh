#!/bin/bash
# install_unix.sh — Installer JogLang Compiler untuk Linux / macOS

set -e

echo ""
echo " ============================================"
echo "   JogLang Compiler v1.0.0 - Installer"
echo "   Basa Jawa Dialek Yogyakarta"
echo " ============================================"
echo ""

# ─── Cek Python ─────────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VERSION=$("$cmd" -c "import sys; print(sys.version_info[:2])")
        if "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" &>/dev/null; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[GAGAL] Python 3.8+ tidak ditemukan."
    echo "        Unduh dari https://python.org"
    exit 1
fi

echo "[INFO] Menggunakan: $($PYTHON --version)"

# ─── Cek pip ────────────────────────────────────────────────────────────────
# Selalu pakai "$PYTHON -m pip" daripada memanggil pip/pip3 langsung,
# supaya instalasi pasti masuk ke environment Python yang sama dengan
# yang dipakai di atas (mencegah kasus 'pip' di PATH mengarah ke
# instalasi Python yang berbeda dari $PYTHON).
"$PYTHON" -m pip --version &>/dev/null
if [ $? -ne 0 ]; then
    echo "[GAGAL] pip tidak ditemukan untuk $PYTHON."
    echo "        Jalankan: $PYTHON -m ensurepip"
    exit 1
fi

# ─── Instalasi ──────────────────────────────────────────────────────────────
echo ""
echo "[INFO] Menginstall JogLang Compiler..."
echo ""

"$PYTHON" -m pip install .

echo ""
echo " ============================================"
echo "   [OK] JogLang Compiler berhasil diinstall!"
echo " ============================================"
echo ""
echo " Cara penggunaan:"
echo "   joglang examples/01_halo_dunia.jog"
echo "   joglang examples/01_halo_dunia.jog --run"
echo "   joglang --help"
echo ""
echo " Atau tanpa instalasi (jalankan dari source):"
echo "   python3 -m joglang_compiler examples/01_halo_dunia.jog"
echo "   python3 main.py examples/01_halo_dunia.jog"
echo ""
