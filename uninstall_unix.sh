#!/bin/bash
# uninstall_unix.sh — Uninstaller JogLang Compiler

echo ""
echo " ============================================"
echo "   JogLang Compiler - Uninstaller"
echo " ============================================"
echo ""
echo "[INFO] Menghapus JogLang Compiler..."

python3 -m pip uninstall joglang -y 2>/dev/null || python -m pip uninstall joglang -y 2>/dev/null || true

echo ""
echo "[OK] JogLang Compiler telah dihapus."
echo ""
