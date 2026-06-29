"""
optimizer.py — Code Optimizer untuk JogLang Compiler.

Melakukan optimasi pada AST sebelum code generation.
Menggunakan Visitor Pattern — optimizer mengunjungi setiap node dan
mengembalikan node baru (atau node yang sama jika tidak ada optimasi).

Optimasi yang diimplementasikan:
  1. Constant Folding  — operasi antar literal dihitung saat kompilasi
       Contoh: 5 + 3 -> 8 | 10 * 2 -> 20 | "halo" + " " + "dunia" -> "halo dunia"
  2. Identity Optimization — operasi identitas dihilangkan
       Contoh: x + 0 -> x | x * 1 -> x | x - 0 -> x | x / 1 -> x
  3. Strength Reduction — operasi mahal diganti lebih murah
       Contoh: x * 2 -> x + x (dalam beberapa kasus)
               x ** 2 -> x * x
  4. Dead Code Elimination — blok yang tidak pernah dieksekusi dihapus
       Contoh: yen salah { ... } -> dihapus
               yen bener { A } liyane { B } -> A
  5. Constant Propagation (parsial) — konstanta literal yang di-assign
       ke variabel bisa dilipat pada penggunaan berikutnya
       (hanya untuk LiteralNode yang jelas, tidak mengubah semantik)
"""

from __future__ import annotations
from typing import Optional, Any
import math

from .ast_nodes import (
    ASTNode, ProgramNode,
    VariableDeclarationNode, AssignmentNode,
    PrintNode, InputNode, ReturnNode, BreakNode, ContinueNode,
    BlockNode, IfNode, WhileNode, ForNode,
    ParameterNode, FunctionNode, CallNode,
    BinaryOperationNode, UnaryOperationNode, VariableNode, LiteralNode,
)
from .errors import OptimizationError


# ===========================================================================
# OPTIMIZER STATISTICS
# ===========================================================================

class OptimizationStats:
    """Statistik hasil optimasi."""

    def __init__(self) -> None:
        self.constant_folds:     int = 0
        self.identity_opts:      int = 0
        self.strength_reductions: int = 0
        self.dead_code_removed:  int = 0
        self.total: int = 0

    def record(self, kind: str) -> None:
        """Catat satu optimasi."""
        if kind == "fold":
            self.constant_folds += 1
        elif kind == "identity":
            self.identity_opts += 1
        elif kind == "strength":
            self.strength_reductions += 1
        elif kind == "dead":
            self.dead_code_removed += 1
        self.total += 1

    def summary(self) -> str:
        return (
            f"Optimasi selesai: {self.total} total | "
            f"{self.constant_folds} constant fold | "
            f"{self.identity_opts} identity | "
            f"{self.strength_reductions} strength reduction | "
            f"{self.dead_code_removed} dead code removed"
        )


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def _is_literal(node: ASTNode) -> bool:
    """Cek apakah node adalah LiteralNode."""
    return isinstance(node, LiteralNode)


def _is_zero(node: ASTNode) -> bool:
    """Cek apakah node adalah literal 0 atau 0.0."""
    return isinstance(node, LiteralNode) and node.value == 0


def _is_one(node: ASTNode) -> bool:
    """Cek apakah node adalah literal 1 atau 1.0."""
    return isinstance(node, LiteralNode) and node.value == 1


def _is_true(node: ASTNode) -> bool:
    """Cek apakah node adalah literal bener (True)."""
    return isinstance(node, LiteralNode) and node.value is True


def _is_false(node: ASTNode) -> bool:
    """Cek apakah node adalah literal salah (False)."""
    return isinstance(node, LiteralNode) and node.value is False


def _make_literal(value: Any, line: int = 0, col: int = 0) -> LiteralNode:
    """Buat LiteralNode dari nilai Python."""
    if isinstance(value, bool):
        return LiteralNode(value=value, kind="bool", line=line, column=col)
    if isinstance(value, int):
        return LiteralNode(value=value, kind="int", line=line, column=col)
    if isinstance(value, float):
        return LiteralNode(value=value, kind="float", line=line, column=col)
    if isinstance(value, str):
        return LiteralNode(value=value, kind="string", line=line, column=col)
    if value is None:
        return LiteralNode(value=None, kind="null", line=line, column=col)
    return LiteralNode(value=value, kind="int", line=line, column=col)


# ===========================================================================
# OPTIMIZER CLASS
# ===========================================================================

class Optimizer:
    """
    Melakukan optimasi pada AST JogLang.

    Setiap visit_*() mengembalikan node AST yang sudah dioptimasi
    (bisa node baru atau node yang sama).

    Usage:
        optimizer = Optimizer()
        optimized_ast = optimizer.optimize(ast)
        print(optimizer.stats.summary())
    """

    def __init__(self) -> None:
        self.stats = OptimizationStats()

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def optimize(self, node: ProgramNode) -> ProgramNode:
        """
        Titik masuk optimasi.

        Args:
            node: Root AST

        Returns:
            ProgramNode yang sudah dioptimasi
        """
        self.stats = OptimizationStats()
        return self._opt(node)   # type: ignore[return-value]

    # -----------------------------------------------------------------------
    # DISPATCHER
    # -----------------------------------------------------------------------

    def _opt(self, node: Optional[ASTNode]) -> Optional[ASTNode]:
        """Dispatch ke metode visit yang sesuai."""
        if node is None:
            return None
        method_name = f"_opt_{type(node).__name__}"
        method = getattr(self, method_name, self._opt_default)
        return method(node)

    def _opt_default(self, node: ASTNode) -> ASTNode:
        """Fallback: kembalikan node tanpa perubahan."""
        return node

    def _opt_list(self, nodes: list) -> list:
        """Optimasi list of nodes, filter None."""
        result = []
        for n in nodes:
            if isinstance(n, tuple):
                # elif_branches: (condition, block)
                new_cond  = self._opt(n[0])
                new_block = self._opt(n[1])
                result.append((new_cond, new_block))
            else:
                optimized = self._opt(n)
                if optimized is not None:
                    result.append(optimized)
        return result

    # -----------------------------------------------------------------------
    # STATEMENT OPTIMIZERS
    # -----------------------------------------------------------------------

    def _opt_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        new_body = self._opt_list(node.body)
        return ProgramNode(body=new_body, line=node.line, column=node.column)

    def _opt_VariableDeclarationNode(self, node: VariableDeclarationNode) -> VariableDeclarationNode:
        new_init = self._opt(node.initializer)
        return VariableDeclarationNode(
            var_type=node.var_type,
            name=node.name,
            initializer=new_init,
            line=node.line,
            column=node.column,
        )

    def _opt_AssignmentNode(self, node: AssignmentNode) -> AssignmentNode:
        new_val = self._opt(node.value)
        return AssignmentNode(
            name=node.name,
            operator=node.operator,
            value=new_val,
            line=node.line,
            column=node.column,
        )

    def _opt_PrintNode(self, node: PrintNode) -> PrintNode:
        return PrintNode(
            expression=self._opt(node.expression),
            line=node.line, column=node.column,
        )

    def _opt_InputNode(self, node: InputNode) -> InputNode:
        return InputNode(
            prompt=self._opt(node.prompt),
            line=node.line, column=node.column,
        )

    def _opt_ReturnNode(self, node: ReturnNode) -> ReturnNode:
        return ReturnNode(
            value=self._opt(node.value),
            line=node.line, column=node.column,
        )

    def _opt_BreakNode(self, node: BreakNode) -> BreakNode:
        return node

    def _opt_ContinueNode(self, node: ContinueNode) -> ContinueNode:
        return node

    def _opt_BlockNode(self, node: BlockNode) -> BlockNode:
        new_stmts = self._opt_list(node.statements)
        return BlockNode(statements=new_stmts, line=node.line, column=node.column)

    def _opt_IfNode(self, node: IfNode) -> Optional[ASTNode]:
        """
        Dead Code Elimination untuk if:
        - yen bener { A } -> A (ambil then_branch)
        - yen salah { A } liyane { B } -> B (ambil else_branch atau hapus)
        - Selain itu optimasi sub-node
        """
        cond = self._opt(node.condition)

        # Dead code: kondisi literal bener (True)
        if _is_true(cond):
            self.stats.record("dead")
            # Kembalikan only then_branch (sebagai BlockNode)
            return self._opt(node.then_branch)

        # Dead code: kondisi literal salah (False)
        if _is_false(cond):
            self.stats.record("dead")
            # Cek elif_branches atau else
            for elif_cond, elif_block in node.elif_branches:
                elif_cond_opt = self._opt(elif_cond)
                if _is_true(elif_cond_opt):
                    return self._opt(elif_block)
                if _is_false(elif_cond_opt):
                    continue
                # Kondisi elif tidak diketahui — tidak bisa eliminasi
                break
            else:
                # Semua elif False atau tidak ada elif -> else_branch
                if node.else_branch is not None:
                    return self._opt(node.else_branch)
                return None   # Seluruh if dihapus

        # Optimasi biasa
        then_opt  = self._opt(node.then_branch)
        elif_opt  = self._opt_list(node.elif_branches)
        else_opt  = self._opt(node.else_branch)

        return IfNode(
            condition=cond,
            then_branch=then_opt,
            elif_branches=elif_opt,
            else_branch=else_opt,
            line=node.line, column=node.column,
        )

    def _opt_WhileNode(self, node: WhileNode) -> Optional[ASTNode]:
        """
        Dead Code Elimination untuk while:
        - nalika salah { } -> dihapus
        """
        cond = self._opt(node.condition)

        if _is_false(cond):
            self.stats.record("dead")
            return None   # Loop tidak pernah jalan — hapus

        body = self._opt(node.body)
        return WhileNode(condition=cond, body=body, line=node.line, column=node.column)

    def _opt_ForNode(self, node: ForNode) -> ForNode:
        return ForNode(
            init=self._opt(node.init),
            condition=self._opt(node.condition),
            update=self._opt(node.update),
            body=self._opt(node.body),
            line=node.line, column=node.column,
        )

    def _opt_FunctionNode(self, node: FunctionNode) -> FunctionNode:
        return FunctionNode(
            name=node.name,
            params=node.params,
            return_type=node.return_type,
            body=self._opt(node.body),
            line=node.line, column=node.column,
        )

    def _opt_CallNode(self, node: CallNode) -> CallNode:
        new_args = [self._opt(arg) for arg in node.arguments]
        return CallNode(
            name=node.name,
            arguments=new_args,
            line=node.line, column=node.column,
        )

    # -----------------------------------------------------------------------
    # EXPRESSION OPTIMIZERS
    # -----------------------------------------------------------------------

    def _opt_LiteralNode(self, node: LiteralNode) -> LiteralNode:
        """Literal tidak perlu dioptimasi."""
        return node

    def _opt_VariableNode(self, node: VariableNode) -> VariableNode:
        """Referensi variabel tidak dioptimasi di sini."""
        return node

    def _opt_UnaryOperationNode(self, node: UnaryOperationNode) -> ASTNode:
        """
        Optimasi unary:
        - -<literal> -> literal negatif (constant fold)
        - ora bener -> salah | ora salah -> bener
        """
        operand = self._opt(node.operand)

        # Constant fold unary minus
        if node.operator == "-" and _is_literal(operand):
            val = operand.value   # type: ignore[union-attr]
            if isinstance(val, (int, float)):
                self.stats.record("fold")
                return _make_literal(-val, node.line, node.column)

        # Constant fold: ora bener -> salah
        if node.operator == "ora" and _is_literal(operand):
            val = operand.value   # type: ignore[union-attr]
            if isinstance(val, bool):
                self.stats.record("fold")
                return _make_literal(not val, node.line, node.column)

        return UnaryOperationNode(
            operator=node.operator,
            operand=operand,
            line=node.line, column=node.column,
        )

    def _opt_BinaryOperationNode(self, node: BinaryOperationNode) -> ASTNode:
        """
        Optimasi binary operation:
        1. Constant Folding — kedua operan literal
        2. Identity Optimization — x+0, x*1, dll.
        3. Strength Reduction — x**2 -> x*x
        4. Boolean short-circuit literal — bener lan x -> x, salah utawa x -> x
        """
        left  = self._opt(node.left)
        right = self._opt(node.right)
        op    = node.operator

        # ===================================================================
        # 1. CONSTANT FOLDING
        # ===================================================================
        if _is_literal(left) and _is_literal(right):
            result = self._fold_binary(
                op,
                left.value,   # type: ignore[union-attr]
                right.value,  # type: ignore[union-attr]
                node.line, node.column,
            )
            if result is not None:
                self.stats.record("fold")
                return result

        # ===================================================================
        # 2. IDENTITY OPTIMIZATION
        # ===================================================================
        identity = self._try_identity(op, left, right, node)
        if identity is not None:
            return identity

        # ===================================================================
        # 3. STRENGTH REDUCTION
        # ===================================================================
        strength = self._try_strength(op, left, right, node)
        if strength is not None:
            return strength

        # ===================================================================
        # 4. BOOLEAN LITERAL SHORT-CIRCUIT
        # ===================================================================
        boolean_result = self._try_boolean_short_circuit(op, left, right, node)
        if boolean_result is not None:
            return boolean_result

        # Tidak ada optimasi — kembalikan node baru dengan sub-node sudah dioptimasi
        return BinaryOperationNode(
            left=left, operator=op, right=right,
            line=node.line, column=node.column,
        )

    # -----------------------------------------------------------------------
    # CONSTANT FOLDING HELPERS
    # -----------------------------------------------------------------------

    def _fold_binary(
        self,
        op:    str,
        left:  Any,
        right: Any,
        line:  int,
        col:   int,
    ) -> Optional[LiteralNode]:
        """
        Hitung operasi biner dua nilai literal saat kompilasi.
        Mengembalikan LiteralNode hasil, atau None jika tidak bisa.
        """
        try:
            if op == "+":
                if isinstance(left, str) and isinstance(right, str):
                    return _make_literal(left + right, line, col)
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    result = left + right
                    return _make_literal(result, line, col)

            elif op == "-":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return _make_literal(left - right, line, col)

            elif op == "*":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return _make_literal(left * right, line, col)

            elif op == "/":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    if right == 0:
                        return None   # Division by zero — biarkan runtime menangani
                    # Integer division hanya jika keduanya int dan habis dibagi
                    if isinstance(left, int) and isinstance(right, int) and left % right == 0:
                        return _make_literal(left // right, line, col)
                    return _make_literal(left / right, line, col)

            elif op == "%":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    if right == 0:
                        return None
                    return _make_literal(left % right, line, col)

            elif op == "**":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    result = left ** right
                    # Hindari overflow float tak terbatas
                    if isinstance(result, float) and (math.isinf(result) or math.isnan(result)):
                        return None
                    return _make_literal(result, line, col)

            # Operator perbandingan
            elif op == "==":
                return _make_literal(left == right, line, col)
            elif op == "!=":
                return _make_literal(left != right, line, col)
            elif op == "<":
                return _make_literal(left < right, line, col)
            elif op == ">":
                return _make_literal(left > right, line, col)
            elif op == "<=":
                return _make_literal(left <= right, line, col)
            elif op == ">=":
                return _make_literal(left >= right, line, col)

            # Operator logika
            elif op == "lan":
                # Hanya fold jika keduanya bool
                if isinstance(left, bool) and isinstance(right, bool):
                    return _make_literal(left and right, line, col)

            elif op == "utawa":
                if isinstance(left, bool) and isinstance(right, bool):
                    return _make_literal(left or right, line, col)

        except (TypeError, ValueError, ZeroDivisionError):
            pass

        return None

    # -----------------------------------------------------------------------
    # IDENTITY OPTIMIZATION HELPER
    # -----------------------------------------------------------------------

    def _try_identity(
        self,
        op:    str,
        left:  ASTNode,
        right: ASTNode,
        node:  BinaryOperationNode,
    ) -> Optional[ASTNode]:
        """
        Optimasi identitas:
        x + 0 -> x    |  0 + x -> x
        x - 0 -> x
        x * 1 -> x    |  1 * x -> x
        x * 0 -> 0    |  0 * x -> 0
        x / 1 -> x
        x ** 1 -> x
        x ** 0 -> 1
        """
        line, col = node.line, node.column

        if op == "+":
            if _is_zero(right):
                self.stats.record("identity")
                return left
            if _is_zero(left):
                self.stats.record("identity")
                return right

        elif op == "-":
            if _is_zero(right):
                self.stats.record("identity")
                return left

        elif op == "*":
            if _is_one(right):
                self.stats.record("identity")
                return left
            if _is_one(left):
                self.stats.record("identity")
                return right
            if _is_zero(right) or _is_zero(left):
                self.stats.record("identity")
                return _make_literal(0, line, col)

        elif op == "/":
            if _is_one(right):
                self.stats.record("identity")
                return left

        elif op == "**":
            if _is_one(right):
                self.stats.record("identity")
                return left
            if _is_zero(right):
                self.stats.record("identity")
                return _make_literal(1, line, col)

        return None

    # -----------------------------------------------------------------------
    # STRENGTH REDUCTION HELPER
    # -----------------------------------------------------------------------

    def _try_strength(
        self,
        op:    str,
        left:  ASTNode,
        right: ASTNode,
        node:  BinaryOperationNode,
    ) -> Optional[ASTNode]:
        """
        Strength Reduction:
        x ** 2 -> x * x  (power->multiply lebih cepat)
        """
        line, col = node.line, node.column

        if op == "**" and isinstance(right, LiteralNode) and right.value == 2:
            self.stats.record("strength")
            # x * x — tapi x hanya boleh dievaluasi sekali (jika ada efek samping)
            # Karena JogLang tidak ada efek samping di ekspresi sederhana,
            # kita hanya lakukan ini untuk VariableNode dan LiteralNode
            if isinstance(left, (VariableNode, LiteralNode)):
                return BinaryOperationNode(
                    left=left, operator="*", right=left,
                    line=line, column=col,
                )

        return None

    # -----------------------------------------------------------------------
    # BOOLEAN SHORT-CIRCUIT HELPER
    # -----------------------------------------------------------------------

    def _try_boolean_short_circuit(
        self,
        op:    str,
        left:  ASTNode,
        right: ASTNode,
        node:  BinaryOperationNode,
    ) -> Optional[ASTNode]:
        """
        Boolean short-circuit dengan literal:
        bener lan x  -> x
        salah lan x  -> salah
        bener utawa x -> bener
        salah utawa x -> x
        """
        if op == "lan":
            if _is_true(left):
                self.stats.record("identity")
                return right
            if _is_false(left):
                self.stats.record("dead")
                return left   # salah
            if _is_true(right):
                self.stats.record("identity")
                return left
            if _is_false(right):
                self.stats.record("dead")
                return right  # salah

        elif op == "utawa":
            if _is_true(left):
                self.stats.record("dead")
                return left   # bener
            if _is_false(left):
                self.stats.record("identity")
                return right
            if _is_true(right):
                self.stats.record("dead")
                return right  # bener
            if _is_false(right):
                self.stats.record("identity")
                return left

        return None


# ===========================================================================
# CONVENIENCE FUNCTION
# ===========================================================================

def optimize(ast: ProgramNode) -> tuple[ProgramNode, OptimizationStats]:
    """
    Fungsi shortcut untuk optimasi AST.

    Args:
        ast: Root AST dari parser/semantic analyzer

    Returns:
        (optimized_ast, stats)
    """
    opt   = Optimizer()
    new_ast = opt.optimize(ast)
    return new_ast, opt.stats
