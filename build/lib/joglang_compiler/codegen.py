"""
codegen.py — Code Generator untuk JogLang Compiler.

Menghasilkan kode Python yang valid dari AST JogLang yang sudah
melalui analisis semantik dan optimasi.

Strategi:
  - Visitor Pattern: setiap node AST menghasilkan string kode Python
  - Indentasi dikelola dengan stack level
  - Operator JogLang dipetakan 1-ke-1 ke operator Python
  - Keyword JogLang diterjemahkan ke konstruksi Python setara

Pemetaan utama:
  JogLang          Python
  ─────────────────────────────
  wiwiti/rampung   (diabaikan — Python tidak perlu blok utama wajib)
  angka x = 5   -> x = 5
  tampilna(x)   -> print(x)
  takon("X:")   -> input("X:")
  yen/liyane    -> if/elif/else
  nalika        -> while
  baleni        -> for (gaya C diubah ke while)
  gawe          -> def
  balekna       -> return
  mandheg       -> break
  terusna       -> continue
  lan/utawa/ora -> and/or/not
  bener/salah   -> True/False
  kosong        -> None
"""

from __future__ import annotations
from typing import Optional

from .ast_nodes import (
    ASTNode, ProgramNode,
    VariableDeclarationNode, AssignmentNode,
    PrintNode, InputNode, ReturnNode, BreakNode, ContinueNode,
    BlockNode, IfNode, WhileNode, ForNode,
    ParameterNode, FunctionNode, CallNode,
    BinaryOperationNode, UnaryOperationNode, VariableNode, LiteralNode,
)
from .errors import CodeGenerationError


# ===========================================================================
# OPERATOR MAPPING
# ===========================================================================

# Operator JogLang -> Python (binary)
_BINARY_OP_MAP: dict[str, str] = {
    "+":     "+",
    "-":     "-",
    "*":     "*",
    "/":     "/",
    "%":     "%",
    "**":    "**",
    "==":    "==",
    "!=":    "!=",
    "<":     "<",
    ">":     ">",
    "<=":    "<=",
    ">=":    ">=",
    "lan":   "and",
    "utawa": "or",
}

# Operator JogLang -> Python (unary)
_UNARY_OP_MAP: dict[str, str] = {
    "-":   "-",
    "ora": "not ",
}

# Operator assignment JogLang -> Python
_ASSIGN_OP_MAP: dict[str, str] = {
    "=":  "=",
    "+=": "+=",
    "-=": "-=",
    "*=": "*=",
    "/=": "/=",
}

# Literal nilai khusus
_LITERAL_MAP: dict[str | None, str] = {
    True:  "True",
    False: "False",
    None:  "None",
}


# ===========================================================================
# CODE GENERATOR CLASS
# ===========================================================================

class CodeGenerator:
    """
    Menghasilkan kode Python dari AST JogLang.

    Usage:
        gen    = CodeGenerator()
        output = gen.generate(ast)
        print(output)
    """

    # Lebar satu level indentasi
    INDENT = "    "

    def __init__(self) -> None:
        self._lines:        list[str] = []
        self._indent_level: int       = 0

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def generate(self, node: ProgramNode) -> str:
        """
        Titik masuk code generation.

        Args:
            node: Root AST (ProgramNode)

        Returns:
            String kode Python yang siap dieksekusi

        Raises:
            CodeGenerationError: jika ada node yang tidak dikenali
        """
        self._lines        = []
        self._indent_level = 0

        # Header file output
        self._emit("# ============================================================")
        self._emit("# Kode ini di-generate otomatis oleh JogLang Compiler v1.0.0")
        self._emit("# Bahasa sumber: JogLang (Basa Jawa Dialek Yogyakarta)")
        self._emit("# JANGAN edit file ini secara manual!")
        self._emit("# ============================================================")
        self._emit("")

        self._gen(node)

        return "\n".join(self._lines)

    # -----------------------------------------------------------------------
    # EMIT HELPERS
    # -----------------------------------------------------------------------

    def _emit(self, line: str = "") -> None:
        """Tambahkan satu baris kode dengan indentasi saat ini."""
        if line:
            self._lines.append(self.INDENT * self._indent_level + line)
        else:
            self._lines.append("")

    def _indent(self) -> None:
        """Tambah satu level indentasi."""
        self._indent_level += 1

    def _dedent(self) -> None:
        """Kurangi satu level indentasi."""
        if self._indent_level > 0:
            self._indent_level -= 1

    # -----------------------------------------------------------------------
    # DISPATCHER
    # -----------------------------------------------------------------------

    def _gen(self, node: Optional[ASTNode]) -> str:
        """
        Dispatch ke method _gen_<ClassName>.
        Mengembalikan string ekspresi (untuk ekspresi)
        atau string kosong (untuk statement yang di-emit langsung).
        """
        if node is None:
            return "None"
        method_name = f"_gen_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise CodeGenerationError(
                f"Node tidak dikenal: '{type(node).__name__}'",
                line=getattr(node, "line", 0),
                column=getattr(node, "column", 0),
            )
        return method(node)

    def _gen_stmt(self, node: ASTNode) -> None:
        """Generate statement (emit langsung, tidak return string)."""
        self._gen(node)

    # -----------------------------------------------------------------------
    # PROGRAM
    # -----------------------------------------------------------------------

    def _gen_ProgramNode(self, node: ProgramNode) -> str:
        """Generate seluruh body program."""
        for stmt in node.body:
            self._gen_stmt(stmt)
        return ""

    # -----------------------------------------------------------------------
    # STATEMENTS
    # -----------------------------------------------------------------------

    def _gen_VariableDeclarationNode(self, node: VariableDeclarationNode) -> str:
        """
        angka umur = 20    ->  umur = 20
        teks nama = "Budi" ->  nama = "Budi"
        angka x            ->  x = None
        """
        if node.initializer is not None:
            value = self._gen(node.initializer)
        else:
            value = "None"
        self._emit(f"{node.name} = {value}")
        return ""

    def _gen_AssignmentNode(self, node: AssignmentNode) -> str:
        """
        x = 5     ->  x = 5
        x += 1    ->  x += 1
        """
        op    = _ASSIGN_OP_MAP.get(node.operator, node.operator)
        value = self._gen(node.value)
        self._emit(f"{node.name} {op} {value}")
        return ""

    def _gen_PrintNode(self, node: PrintNode) -> str:
        """
        tampilna(x)       ->  print(x)
        tampilna("halo")  ->  print("halo")
        """
        expr = self._gen(node.expression)
        self._emit(f"print({expr})")
        return ""

    def _gen_InputNode(self, node: InputNode) -> str:
        """
        takon("Nama: ")  ->  input("Nama: ")
        takon()          ->  input()

        InputNode biasanya muncul sebagai initializer, bukan statement.
        Jika dipanggil sebagai statement (standalone), emit langsung.
        """
        if node.prompt is not None:
            prompt = self._gen(node.prompt)
            return f"input({prompt})"
        return "input()"

    def _gen_ReturnNode(self, node: ReturnNode) -> str:
        """
        balekna x + 1  ->  return x + 1
        balekna        ->  return
        """
        if node.value is not None:
            val = self._gen(node.value)
            self._emit(f"return {val}")
        else:
            self._emit("return")
        return ""

    def _gen_BreakNode(self, node: BreakNode) -> str:
        """mandheg  ->  break"""
        self._emit("break")
        return ""

    def _gen_ContinueNode(self, node: ContinueNode) -> str:
        """terusna  ->  continue"""
        self._emit("continue")
        return ""

    def _gen_BlockNode(self, node: BlockNode) -> str:
        """
        Generate isi blok (statements).
        Blok kosong menghasilkan 'pass'.
        """
        if not node.statements:
            self._emit("pass")
        else:
            for stmt in node.statements:
                self._gen_stmt(stmt)
        return ""

    def _gen_IfNode(self, node: IfNode) -> str:
        """
        yen x > 0 { ... }
        liyane_yen x == 0 { ... }
        liyane { ... }

        ->

        if x > 0:
            ...
        elif x == 0:
            ...
        else:
            ...
        """
        cond = self._gen(node.condition)
        self._emit(f"if {cond}:")
        self._indent()
        self._gen_BlockNode(node.then_branch)
        self._dedent()

        for elif_cond, elif_block in node.elif_branches:
            ec = self._gen(elif_cond)
            self._emit(f"elif {ec}:")
            self._indent()
            self._gen_BlockNode(elif_block)
            self._dedent()

        if node.else_branch is not None:
            self._emit("else:")
            self._indent()
            self._gen_BlockNode(node.else_branch)
            self._dedent()

        return ""

    def _gen_WhileNode(self, node: WhileNode) -> str:
        """
        nalika i < 10 { ... }
        ->
        while i < 10:
            ...
        """
        cond = self._gen(node.condition)
        self._emit(f"while {cond}:")
        self._indent()
        self._gen_BlockNode(node.body)
        self._dedent()
        return ""

    def _gen_ForNode(self, node: ForNode) -> str:
        """
        baleni angka i = 0 ; i < 5 ; i += 1 { ... }

        Diterjemahkan ke Python dengan try/finally agar update
        selalu dieksekusi meski ada 'continue':

        i = 0
        while i < 5:
            try:
                ...  (body)
            finally:
                i += 1  (update selalu jalan, termasuk saat continue)

        Catatan: 'break' tetap bekerja karena finally tidak memblokir break.
        Namun, untuk menjaga semantik yang lebih bersih dan menghindari
        overhead try/finally pada loop tanpa continue, kita gunakan
        pendekatan langsung jika body tidak mengandung ContinueNode.
        """
        from .ast_nodes import ContinueNode as _CN

        def _has_continue(stmts: list) -> bool:
            """Cek apakah ada ContinueNode di body (semua level, kecuali nested loop)."""
            from .ast_nodes import WhileNode as _WN, ForNode as _FN, IfNode as _IN, BlockNode as _BN
            for s in stmts:
                if isinstance(s, _CN):
                    return True
                # Masuk ke blok if/else tapi BUKAN ke nested loop
                if isinstance(s, _IN):
                    sub = []
                    if s.then_branch:
                        sub.extend(s.then_branch.statements)
                    for _, blk in (s.elif_branches or []):
                        sub.extend(blk.statements)
                    if s.else_branch:
                        sub.extend(s.else_branch.statements)
                    if _has_continue(sub):
                        return True
                # Jangan masuk nested while/for — mereka punya continue sendiri
            return False

        # Init
        self._gen_stmt(node.init)

        # Kondisi
        cond = self._gen(node.condition)
        self._emit(f"while {cond}:")
        self._indent()

        body_stmts = node.body.statements if node.body else []

        if _has_continue(body_stmts):
            # Gunakan try/finally agar update tetap jalan saat continue
            self._emit("try:")
            self._indent()
            self._gen_BlockNode(node.body)
            self._dedent()
            self._emit("finally:")
            self._indent()
            self._gen_stmt(node.update)
            self._dedent()
        else:
            # Tidak ada continue — langsung tulis body lalu update
            self._gen_BlockNode(node.body)
            self._gen_stmt(node.update)

        self._dedent()
        return ""

    def _gen_FunctionNode(self, node: FunctionNode) -> str:
        """
        gawe tambah(angka a, angka b) { balekna a + b }
        ->
        def tambah(a, b):
            return a + b
        """
        # Parameter: buang tipe data, hanya nama
        params = ", ".join(p.name for p in node.params)
        self._emit(f"def {node.name}({params}):")
        self._indent()
        self._gen_BlockNode(node.body)
        self._dedent()
        self._emit("")  # Baris kosong setelah def
        return ""

    def _gen_CallNode(self, node: CallNode) -> str:
        """
        tambah(3, 4)  ->  tambah(3, 4)
        halo()        ->  halo()

        CallNode bisa muncul sebagai ekspresi ATAU statement standalone.
        Jika sebagai statement, emit langsung.
        """
        args = ", ".join(self._gen(arg) for arg in node.arguments)
        call_str = f"{node.name}({args})"

        # Deteksi apakah ini dipanggil sebagai statement (bukan ekspresi)
        # Trick: kalau _indent_level konteks statement, emit langsung
        # Tapi karena _gen dipanggil dari keduanya, kita kembalikan string
        # dan biarkan pemanggil yang emit jika perlu
        return call_str

    # -----------------------------------------------------------------------
    # EXPRESSIONS
    # -----------------------------------------------------------------------

    def _gen_LiteralNode(self, node: LiteralNode) -> str:
        """
        42     -> "42"
        3.14   -> "3.14"
        "halo" -> '"halo"'
        bener  -> "True"
        salah  -> "False"
        kosong -> "None"
        """
        val = node.value
        if val is True:
            return "True"
        if val is False:
            return "False"
        if val is None:
            return "None"
        if isinstance(val, str):
            # Escape tanda kutip dalam string
            escaped = val.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(val, float):
            return repr(val)   # repr lebih akurat untuk float
        return str(val)

    def _gen_VariableNode(self, node: VariableNode) -> str:
        """x  ->  "x" """
        return node.name

    def _gen_BinaryOperationNode(self, node: BinaryOperationNode) -> str:
        """
        a + b     ->  "a + b"
        x > 0     ->  "x > 0"
        f lan g   ->  "f and g"
        """
        left  = self._gen(node.left)
        right = self._gen(node.right)
        op    = _BINARY_OP_MAP.get(node.operator, node.operator)

        # Bungkus sub-ekspresi binary dalam tanda kurung jika perlu
        # untuk mempertahankan preseden yang benar
        left_str  = self._maybe_paren(node.left,  left)
        right_str = self._maybe_paren(node.right, right)

        return f"{left_str} {op} {right_str}"

    def _gen_UnaryOperationNode(self, node: UnaryOperationNode) -> str:
        """
        -x        ->  "-x"
        ora flag  ->  "not flag"
        """
        op      = _UNARY_OP_MAP.get(node.operator, node.operator)
        operand = self._gen(node.operand)

        # Bungkus operan jika binary operation
        if isinstance(node.operand, BinaryOperationNode):
            operand = f"({operand})"

        return f"{op}{operand}"

    def _gen_ParameterNode(self, node: ParameterNode) -> str:
        """Parameter hanya nama (tipe diabaikan di Python)."""
        return node.name

    # -----------------------------------------------------------------------
    # HELPER: PARENTHESIZATION
    # -----------------------------------------------------------------------

    # Preseden operator Python (lebih tinggi = lebih kuat)
    _PRECEDENCE: dict[str, int] = {
        "or":  1,
        "and": 2,
        "not": 3,
        "==":  4, "!=": 4, "<": 4, ">": 4, "<=": 4, ">=": 4,
        "+":   5, "-":  5,
        "*":   6, "/":  6, "%": 6,
        "**":  7,
    }

    def _get_prec(self, op: str) -> int:
        """Ambil preseden operator Python."""
        py_op = _BINARY_OP_MAP.get(op, op)
        return self._PRECEDENCE.get(py_op, 0)

    def _maybe_paren(self, child_node: ASTNode, child_str: str) -> str:
        """
        Tambahkan tanda kurung pada sub-ekspresi binary jika diperlukan
        untuk kejelasan (tidak wajib untuk kebenaran karena Python sudah
        tahu presedennya, tapi membuat output lebih mudah dibaca).
        """
        if isinstance(child_node, BinaryOperationNode):
            # Selalu bungkus binary sub-ekspresi agar aman
            return f"({child_str})"
        return child_str


# ===========================================================================
# STANDALONE STATEMENT WRAPPER
# ===========================================================================

def _is_expr_node(node: ASTNode) -> bool:
    """Cek apakah node adalah ekspresi (bukan statement)."""
    return isinstance(node, (
        BinaryOperationNode, UnaryOperationNode,
        VariableNode, LiteralNode, CallNode, InputNode,
    ))


# Patch: CallNode dan InputNode sebagai statement standalone
_original_gen_program = CodeGenerator._gen_ProgramNode


def _patched_gen_program(self: CodeGenerator, node: ProgramNode) -> str:
    """Generate program dengan handling CallNode sebagai statement."""
    for stmt in node.body:
        # CallNode sebagai statement top-level perlu di-emit
        if isinstance(stmt, CallNode):
            call_str = self._gen_CallNode(stmt)
            self._emit(call_str)
        else:
            self._gen_stmt(stmt)
    return ""


CodeGenerator._gen_ProgramNode = _patched_gen_program


def _patched_gen_block(self: CodeGenerator, node: BlockNode) -> str:
    """Generate block dengan handling CallNode sebagai statement."""
    if not node.statements:
        self._emit("pass")
        return ""
    for stmt in node.statements:
        if isinstance(stmt, CallNode):
            call_str = self._gen_CallNode(stmt)
            self._emit(call_str)
        elif isinstance(stmt, InputNode):
            # InputNode standalone (jarang, tapi mungkin)
            inp_str = self._gen_InputNode(stmt)
            self._emit(inp_str)
        else:
            self._gen_stmt(stmt)
    return ""


CodeGenerator._gen_BlockNode = _patched_gen_block


# ===========================================================================
# CONVENIENCE FUNCTION
# ===========================================================================

def generate(ast: ProgramNode) -> str:
    """
    Fungsi shortcut untuk code generation.

    Args:
        ast: Root AST dari optimizer

    Returns:
        String kode Python siap dieksekusi

    Raises:
        CodeGenerationError: jika ada node yang tidak dikenali
    """
    return CodeGenerator().generate(ast)
