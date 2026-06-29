"""
semantic.py — Analisis Semantik untuk JogLang Compiler.

Modul ini memeriksa kebenaran semantik AST hasil parsing:
  1. Variabel belum dideklarasikan
  2. Redeklarasi variabel (dalam scope yang sama)
  3. Fungsi belum didefinisikan
  4. Jumlah argumen tidak sesuai parameter
  5. Type mismatch (dasar)
  6. balekna di luar fungsi
  7. mandheg (break) di luar loop
  8. terusna (continue) di luar loop

Pendekatan: Visitor Pattern — SemanticAnalyzer mengunjungi setiap node AST.
"""

from __future__ import annotations
from typing import Optional, Any

from .ast_nodes import (
    ASTNode, ASTVisitor, ProgramNode,
    VariableDeclarationNode, AssignmentNode,
    PrintNode, InputNode, ReturnNode, BreakNode, ContinueNode,
    BlockNode, IfNode, WhileNode, ForNode,
    ParameterNode, FunctionNode, CallNode,
    BinaryOperationNode, UnaryOperationNode, VariableNode, LiteralNode,
)
from .errors import SemanticError


# ===========================================================================
# SYMBOL TABLE
# ===========================================================================

class SymbolInfo:
    """Informasi satu simbol (variabel atau fungsi) dalam symbol table."""

    def __init__(
        self,
        name:       str,
        kind:       str,           # 'variable' | 'function'
        var_type:   Optional[str] = None,   # 'angka' | 'pecahan' | 'teks' | 'bener_salah'
        params:     Optional[list] = None,  # [ParameterNode] untuk fungsi
        line:       int = 0,
        column:     int = 0,
    ) -> None:
        self.name     = name
        self.kind     = kind
        self.var_type = var_type
        self.params   = params or []
        self.line     = line
        self.column   = column

    def __repr__(self) -> str:
        return (
            f"SymbolInfo(name={self.name!r}, kind={self.kind!r}, "
            f"type={self.var_type!r}, line={self.line})"
        )


class Scope:
    """
    Satu level scope (lingkup) dalam symbol table.
    Scope bersarang: scope dalam bisa melihat scope luar (chain).
    """

    def __init__(self, parent: Optional["Scope"] = None, scope_name: str = "global") -> None:
        self._symbols:    dict[str, SymbolInfo] = {}
        self.parent:      Optional[Scope]       = parent
        self.scope_name:  str                   = scope_name

    def define(self, symbol: SymbolInfo) -> None:
        """
        Mendefinisikan simbol dalam scope ini.

        Raises:
            SemanticError: jika simbol sudah ada di scope yang sama.
        """
        if symbol.name in self._symbols:
            existing = self._symbols[symbol.name]
            raise SemanticError(
                f"Redeklarasi '{symbol.name}': sudah dideklarasikan "
                f"di baris {existing.line}, kolom {existing.column}.",
                line=symbol.line,
                column=symbol.column,
            )
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """
        Mencari simbol mulai dari scope ini ke atas (scope luar).

        Returns:
            SymbolInfo jika ditemukan, None jika tidak.
        """
        if name in self._symbols:
            return self._symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[SymbolInfo]:
        """Hanya cari di scope lokal (tidak ke parent)."""
        return self._symbols.get(name)


# ===========================================================================
# TYPE SYSTEM (sederhana)
# ===========================================================================

# Mapping dari keyword tipe JogLang ke nama internal
JOGLANG_TYPES = {"angka", "pecahan", "teks", "bener_salah"}

# Kompatibilitas tipe untuk operasi
# Kunci: (type_kiri, operator, type_kanan) -> type_hasil
# Jika tidak ada kunci, operasi dianggap tidak kompatibel
_TYPE_COMPAT: dict[tuple[str, str, str], str] = {}

# Aritmatika angka
for _op in ("+", "-", "*", "/", "%", "**"):
    _TYPE_COMPAT[("angka",   _op, "angka")]   = "angka"
    _TYPE_COMPAT[("pecahan", _op, "pecahan")] = "pecahan"
    _TYPE_COMPAT[("angka",   _op, "pecahan")] = "pecahan"
    _TYPE_COMPAT[("pecahan", _op, "angka")]   = "pecahan"

# String concatenation
_TYPE_COMPAT[("teks", "+", "teks")] = "teks"

# Perbandingan — selalu menghasilkan bener_salah
for _op in ("==", "!=", "<", ">", "<=", ">="):
    for _t1 in ("angka", "pecahan", "teks", "bener_salah"):
        for _t2 in ("angka", "pecahan", "teks", "bener_salah"):
            # Perbandingan == dan != boleh antar tipe apapun
            if _op in ("==", "!="):
                _TYPE_COMPAT[(_t1, _op, _t2)] = "bener_salah"
            elif _t1 in ("angka", "pecahan") and _t2 in ("angka", "pecahan"):
                _TYPE_COMPAT[(_t1, _op, _t2)] = "bener_salah"
            elif _t1 == "teks" and _t2 == "teks":
                _TYPE_COMPAT[(_t1, _op, _t2)] = "bener_salah"

# Logika — hanya bener_salah
for _op in ("lan", "utawa"):
    _TYPE_COMPAT[("bener_salah", _op, "bener_salah")] = "bener_salah"


def infer_literal_type(node: LiteralNode) -> str:
    """Inferensi tipe dari LiteralNode."""
    kind_map = {
        "int":    "angka",
        "float":  "pecahan",
        "string": "teks",
        "bool":   "bener_salah",
        "null":   "kosong",
    }
    return kind_map.get(node.kind, "kosong")


# ===========================================================================
# SEMANTIC ANALYZER
# ===========================================================================

class SemanticAnalyzer(ASTVisitor):
    """
    Melakukan analisis semantik pada AST JogLang.

    Usage:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)   # melempar SemanticError jika ada masalah
    """

    def __init__(self) -> None:
        # Stack scope: scope[0] = global
        self._scope:        Scope = Scope(scope_name="global")
        self._in_function:  bool  = False   # sedang di dalam fungsi?
        self._in_loop:      int   = 0       # kedalaman loop (>0 = di dalam loop)
        self._current_func: Optional[str] = None
        self._errors:       list[SemanticError] = []

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def analyze(self, node: ProgramNode) -> None:
        """
        Titik masuk analisis semantik.

        Args:
            node: Root AST (ProgramNode)

        Raises:
            SemanticError: Jika ditemukan kesalahan semantik pertama
                           (fail-fast) atau ringkasan semua error.
        """
        self._errors = []
        self.visit_ProgramNode(node)

        if self._errors:
            # Tampilkan semua error yang dikumpulkan
            messages = "\n".join(str(e) for e in self._errors)
            raise SemanticError(
                f"Ditemukan {len(self._errors)} kesalahan semantik:\n{messages}",
                line=0, column=0,
            )

    # -----------------------------------------------------------------------
    # SCOPE MANAGEMENT
    # -----------------------------------------------------------------------

    def _push_scope(self, name: str = "") -> None:
        """Membuat scope baru (masuk ke blok baru)."""
        self._scope = Scope(parent=self._scope, scope_name=name)

    def _pop_scope(self) -> None:
        """Kembali ke scope luar."""
        if self._scope.parent is not None:
            self._scope = self._scope.parent

    def _define(self, symbol: SymbolInfo) -> None:
        """Mendefinisikan simbol; error dikumpulkan, bukan langsung raise."""
        try:
            self._scope.define(symbol)
        except SemanticError as e:
            self._errors.append(e)

    def _lookup(self, name: str, line: int, col: int) -> Optional[SymbolInfo]:
        """Mencari simbol; jika tidak ada, catat error dan kembalikan None."""
        sym = self._scope.lookup(name)
        if sym is None:
            self._errors.append(SemanticError(
                f"'{name}' belum dideklarasikan.",
                line=line, column=col,
            ))
        return sym

    # -----------------------------------------------------------------------
    # VISITOR METHODS
    # -----------------------------------------------------------------------

    def visit_ProgramNode(self, node: ProgramNode) -> None:
        """Kunjungi semua statement dalam program."""
        for stmt in node.body:
            self._visit(stmt)

    def visit_VariableDeclarationNode(self, node: VariableDeclarationNode) -> None:
        """
        Periksa deklarasi variabel:
        - Tipe harus valid
        - Tidak boleh redeklarasi di scope yang sama
        - Inisialisasi (jika ada) harus tipe kompatibel
        """
        # Periksa tipe valid
        if node.var_type not in JOGLANG_TYPES:
            self._errors.append(SemanticError(
                f"Tipe '{node.var_type}' tidak dikenal.",
                line=node.line, column=node.column,
            ))

        # Daftarkan variabel
        self._define(SymbolInfo(
            name=node.name,
            kind="variable",
            var_type=node.var_type,
            line=node.line,
            column=node.column,
        ))

        # Periksa inisialisasi
        if node.initializer is not None:
            init_type = self._infer_type(node.initializer)
            self._check_type_compat_assign(node.var_type, init_type, node.initializer)
            self._visit(node.initializer)

    def visit_AssignmentNode(self, node: AssignmentNode) -> None:
        """
        Periksa assignment:
        - Variabel harus sudah dideklarasikan
        - Tipe nilai harus kompatibel
        """
        sym = self._lookup(node.name, node.line, node.column)
        if sym is not None and sym.kind == "function":
            self._errors.append(SemanticError(
                f"'{node.name}' adalah fungsi, tidak bisa di-assign.",
                line=node.line, column=node.column,
            ))

        if node.value is not None:
            self._visit(node.value)
            if sym is not None and sym.var_type:
                val_type = self._infer_type(node.value)
                self._check_type_compat_assign(sym.var_type, val_type, node.value)

    def visit_PrintNode(self, node: PrintNode) -> None:
        """Periksa ekspresi yang dicetak."""
        if node.expression is not None:
            self._visit(node.expression)

    def visit_InputNode(self, node: InputNode) -> None:
        """Periksa prompt input (opsional)."""
        if node.prompt is not None:
            self._visit(node.prompt)

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """
        balekna hanya valid di dalam fungsi.
        """
        if not self._in_function:
            self._errors.append(SemanticError(
                "'balekna' digunakan di luar fungsi.",
                line=node.line, column=node.column,
            ))
        if node.value is not None:
            self._visit(node.value)

    def visit_BreakNode(self, node: BreakNode) -> None:
        """mandheg hanya valid di dalam loop."""
        if self._in_loop == 0:
            self._errors.append(SemanticError(
                "'mandheg' (break) digunakan di luar loop.",
                line=node.line, column=node.column,
            ))

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """terusna hanya valid di dalam loop."""
        if self._in_loop == 0:
            self._errors.append(SemanticError(
                "'terusna' (continue) digunakan di luar loop.",
                line=node.line, column=node.column,
            ))

    def visit_BlockNode(self, node: BlockNode) -> None:
        """Kunjungi semua statement dalam blok."""
        for stmt in node.statements:
            self._visit(stmt)

    def visit_IfNode(self, node: IfNode) -> None:
        """Periksa kondisi if dan semua cabang."""
        if node.condition is not None:
            self._visit(node.condition)
            cond_type = self._infer_type(node.condition)
            if cond_type not in ("bener_salah", "kosong", None):
                # Hanya peringatan ringan — banyak bahasa izinkan truthy value
                pass

        if node.then_branch is not None:
            self._push_scope("if_then")
            self.visit_BlockNode(node.then_branch)
            self._pop_scope()

        for elif_cond, elif_block in node.elif_branches:
            self._visit(elif_cond)
            self._push_scope("if_elif")
            self.visit_BlockNode(elif_block)
            self._pop_scope()

        if node.else_branch is not None:
            self._push_scope("if_else")
            self.visit_BlockNode(node.else_branch)
            self._pop_scope()

    def visit_WhileNode(self, node: WhileNode) -> None:
        """Periksa kondisi dan body while loop."""
        if node.condition is not None:
            self._visit(node.condition)

        self._in_loop += 1
        if node.body is not None:
            self._push_scope("while")
            self.visit_BlockNode(node.body)
            self._pop_scope()
        self._in_loop -= 1

    def visit_ForNode(self, node: ForNode) -> None:
        """Periksa for loop: init, kondisi, update, dan body."""
        self._push_scope("for")

        if node.init is not None:
            self._visit(node.init)
        if node.condition is not None:
            self._visit(node.condition)
        if node.update is not None:
            self._visit(node.update)

        self._in_loop += 1
        if node.body is not None:
            # Body for-loop berbagi scope dengan init
            self.visit_BlockNode(node.body)
        self._in_loop -= 1

        self._pop_scope()

    def visit_FunctionNode(self, node: FunctionNode) -> None:
        """
        Deklarasi fungsi:
        - Daftarkan ke scope global (atau scope saat ini)
        - Masuk ke scope baru, daftarkan parameter
        - Periksa body
        """
        # Daftarkan fungsi ke scope luar
        self._define(SymbolInfo(
            name=node.name,
            kind="function",
            params=node.params,
            line=node.line,
            column=node.column,
        ))

        # Masuk scope fungsi
        prev_in_function  = self._in_function
        prev_current_func = self._current_func
        self._in_function  = True
        self._current_func = node.name
        self._push_scope(f"function_{node.name}")

        # Daftarkan parameter
        for param in node.params:
            self._define(SymbolInfo(
                name=param.name,
                kind="variable",
                var_type=param.param_type,
                line=param.line,
                column=param.column,
            ))

        # Periksa body
        if node.body is not None:
            self.visit_BlockNode(node.body)

        self._pop_scope()
        self._in_function  = prev_in_function
        self._current_func = prev_current_func

    def visit_CallNode(self, node: CallNode) -> None:
        """
        Pemanggilan fungsi:
        - Fungsi harus sudah dideklarasikan
        - Jumlah argumen harus sesuai parameter
        """
        sym = self._lookup(node.name, node.line, node.column)

        if sym is not None:
            if sym.kind != "function":
                self._errors.append(SemanticError(
                    f"'{node.name}' adalah variabel, bukan fungsi.",
                    line=node.line, column=node.column,
                ))
            else:
                # Periksa jumlah argumen
                expected = len(sym.params)
                got      = len(node.arguments)
                if expected != got:
                    self._errors.append(SemanticError(
                        f"Fungsi '{node.name}' membutuhkan {expected} argumen, "
                        f"tapi diberikan {got}.",
                        line=node.line, column=node.column,
                    ))

        # Periksa setiap argumen
        for arg in node.arguments:
            self._visit(arg)

    def visit_BinaryOperationNode(self, node: BinaryOperationNode) -> None:
        """Periksa kedua operan binary operation."""
        if node.left is not None:
            self._visit(node.left)
        if node.right is not None:
            self._visit(node.right)

    def visit_UnaryOperationNode(self, node: UnaryOperationNode) -> None:
        """Periksa operan unary operation."""
        if node.operand is not None:
            self._visit(node.operand)

        # 'ora' hanya valid pada bener_salah
        if node.operator == "ora":
            op_type = self._infer_type(node.operand) if node.operand else None
            if op_type not in ("bener_salah", None, "kosong"):
                self._errors.append(SemanticError(
                    f"Operator 'ora' (not) hanya bisa digunakan pada tipe 'bener_salah', "
                    f"bukan '{op_type}'.",
                    line=node.line, column=node.column,
                ))

    def visit_VariableNode(self, node: VariableNode) -> None:
        """Variabel harus sudah dideklarasikan."""
        self._lookup(node.name, node.line, node.column)

    def visit_LiteralNode(self, node: LiteralNode) -> None:
        """Literal selalu valid."""
        pass

    def visit_ParameterNode(self, node: ParameterNode) -> None:
        """Parameter diproses di visit_FunctionNode."""
        pass

    # -----------------------------------------------------------------------
    # TYPE INFERENCE
    # -----------------------------------------------------------------------

    def _infer_type(self, node: Optional[ASTNode]) -> Optional[str]:
        """
        Menginferensikan tipe dari ekspresi AST.

        Returns:
            Nama tipe JogLang ('angka', 'pecahan', 'teks', 'bener_salah', 'kosong')
            atau None jika tidak bisa ditentukan.
        """
        if node is None:
            return None

        if isinstance(node, LiteralNode):
            return infer_literal_type(node)

        if isinstance(node, VariableNode):
            sym = self._scope.lookup(node.name)
            return sym.var_type if sym else None

        if isinstance(node, BinaryOperationNode):
            left_type  = self._infer_type(node.left)
            right_type = self._infer_type(node.right)
            if left_type is None or right_type is None:
                return None
            result = _TYPE_COMPAT.get((left_type, node.operator, right_type))
            return result

        if isinstance(node, UnaryOperationNode):
            op_type = self._infer_type(node.operand)
            if node.operator == "-":
                return op_type   # -angka = angka, -pecahan = pecahan
            if node.operator == "ora":
                return "bener_salah"
            return op_type

        if isinstance(node, CallNode):
            sym = self._scope.lookup(node.name)
            # Tipe return fungsi belum ditentukan secara eksplisit di grammar
            return None

        if isinstance(node, InputNode):
            # takon selalu mengembalikan string (dari user input)
            return "teks"

        return None

    def _check_type_compat_assign(
        self,
        declared_type: str,
        value_type:    Optional[str],
        node:          ASTNode,
    ) -> None:
        """
        Cek kompatibilitas tipe assignment.
        Hanya periksa jika kedua tipe diketahui.
        Izinkan angka = pecahan (implicit widening).
        """
        if value_type is None or value_type == "kosong":
            return   # tidak bisa disimpulkan, lewati

        # Widening: angka bisa menerima pecahan dan sebaliknya
        numeric = {"angka", "pecahan"}
        if declared_type in numeric and value_type in numeric:
            return

        if declared_type != value_type:
            self._errors.append(SemanticError(
                f"Type mismatch: variabel bertipe '{declared_type}' "
                f"tidak bisa menerima nilai bertipe '{value_type}'.",
                line=node.line, column=node.column,
            ))

    # -----------------------------------------------------------------------
    # HELPER
    # -----------------------------------------------------------------------

    def _visit(self, node: Optional[ASTNode]) -> None:
        """Kunjungi node jika tidak None."""
        if node is not None:
            node.accept(self)

    def generic_visit(self, node: ASTNode) -> None:
        """Fallback: kunjungi anak-anak node."""
        self.visit_children(node)


# ===========================================================================
# CONVENIENCE FUNCTION
# ===========================================================================

def analyze(ast: ProgramNode) -> None:
    """
    Fungsi shortcut untuk analisis semantik.

    Args:
        ast: Root AST dari parser

    Raises:
        SemanticError: jika ditemukan kesalahan semantik
    """
    SemanticAnalyzer().analyze(ast)
