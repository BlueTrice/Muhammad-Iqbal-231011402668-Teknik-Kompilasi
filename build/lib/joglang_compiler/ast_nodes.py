"""
ast_nodes.py — Definisi semua node AST untuk JogLang Compiler.

Catatan: Semua field wajib (tanpa default) harus ditulis sebelum
field opsional (dengan default) karena aturan Python dataclass.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any


# ===========================================================================
# BASE NODE
# ===========================================================================

@dataclass
class ASTNode:
    """Base class untuk semua node AST."""
    line:   int = field(default=0, repr=False)
    column: int = field(default=0, repr=False)

    def accept(self, visitor: "ASTVisitor") -> Any:
        method_name   = f"visit_{type(self).__name__}"
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)


# ===========================================================================
# PROGRAM
# ===========================================================================

@dataclass
class ProgramNode(ASTNode):
    """Root node seluruh program JogLang. wiwiti ... rampung"""
    body: list = field(default_factory=list)


# ===========================================================================
# STATEMENT NODES
# ===========================================================================

@dataclass
class VariableDeclarationNode(ASTNode):
    """
    Deklarasi variabel dengan tipe.
    Contoh: angka umur = 20
    Field wajib (var_type, name) di depan, opsional di belakang.
    """
    var_type:    str           = ""
    name:        str           = ""
    initializer: Optional[Any] = None   # ASTNode | None


@dataclass
class AssignmentNode(ASTNode):
    """
    Assignment ke variabel yang sudah ada.
    Contoh: x = 10 | x += 5
    """
    name:     str           = ""
    operator: str           = "="
    value:    Optional[Any] = None   # ASTNode


@dataclass
class PrintNode(ASTNode):
    """Statement output. Contoh: tampilna(ekspresi)"""
    expression: Optional[Any] = None   # ASTNode


@dataclass
class InputNode(ASTNode):
    """Statement input dari user. Contoh: takon("Masukkan nama: ")"""
    prompt: Optional[Any] = None   # ASTNode | None


@dataclass
class ReturnNode(ASTNode):
    """Statement return. Contoh: balekna x + 1"""
    value: Optional[Any] = None   # ASTNode | None


@dataclass
class BreakNode(ASTNode):
    """Statement break dari loop. Contoh: mandheg"""
    pass


@dataclass
class ContinueNode(ASTNode):
    """Statement continue dalam loop. Contoh: terusna"""
    pass


# ===========================================================================
# BLOCK / CONTROL FLOW NODES
# ===========================================================================

@dataclass
class BlockNode(ASTNode):
    """Blok pernyataan. { statement* }"""
    statements: list = field(default_factory=list)


@dataclass
class IfNode(ASTNode):
    """
    Pernyataan kondisional.
    yen expr { } liyane_yen expr { } liyane { }
    """
    condition:     Optional[Any] = None    # ASTNode
    then_branch:   Optional[Any] = None    # BlockNode
    elif_branches: list          = field(default_factory=list)   # [(ASTNode, BlockNode)]
    else_branch:   Optional[Any] = None    # BlockNode | None


@dataclass
class WhileNode(ASTNode):
    """Loop while. nalika expr { }"""
    condition: Optional[Any] = None   # ASTNode
    body:      Optional[Any] = None   # BlockNode


@dataclass
class ForNode(ASTNode):
    """
    Loop for (tiga bagian).
    baleni init ; condition ; update { }
    """
    init:      Optional[Any] = None   # VariableDeclarationNode | AssignmentNode
    condition: Optional[Any] = None   # ASTNode
    update:    Optional[Any] = None   # AssignmentNode
    body:      Optional[Any] = None   # BlockNode


# ===========================================================================
# FUNCTION NODES
# ===========================================================================

@dataclass
class ParameterNode(ASTNode):
    """Parameter fungsi. Contoh: angka x"""
    param_type: str = ""
    name:       str = ""


@dataclass
class FunctionNode(ASTNode):
    """
    Deklarasi fungsi.
    gawe nama(params) { body }
    """
    name:        str           = ""
    params:      list          = field(default_factory=list)   # [ParameterNode]
    return_type: Optional[str] = None
    body:        Optional[Any] = None   # BlockNode


@dataclass
class CallNode(ASTNode):
    """Pemanggilan fungsi. Contoh: tambah(3, 4)"""
    name:      str  = ""
    arguments: list = field(default_factory=list)   # [ASTNode]


# ===========================================================================
# EXPRESSION NODES
# ===========================================================================

@dataclass
class BinaryOperationNode(ASTNode):
    """
    Operasi biner.
    Contoh: a + b | x > 0 | bener lan salah
    """
    left:     Optional[Any] = None   # ASTNode
    operator: str           = ""
    right:    Optional[Any] = None   # ASTNode


@dataclass
class UnaryOperationNode(ASTNode):
    """Operasi unari. Contoh: -x | ora bener"""
    operator: str           = ""
    operand:  Optional[Any] = None   # ASTNode


@dataclass
class VariableNode(ASTNode):
    """Referensi ke variabel. Contoh: x, umur"""
    name: str = ""


@dataclass
class LiteralNode(ASTNode):
    """Nilai literal. Contoh: 42, 3.14, "halo", bener, kosong"""
    value: Any = None    # int | float | str | bool | None
    kind:  str = ""      # 'int' | 'float' | 'string' | 'bool' | 'null'


# ===========================================================================
# VISITOR BASE CLASS
# ===========================================================================

class ASTVisitor:
    """Base class untuk semua visitor AST (Visitor Pattern)."""

    def generic_visit(self, node: ASTNode) -> Any:
        raise NotImplementedError(
            f"Visitor '{type(self).__name__}' belum mengimplementasikan "
            f"'visit_{type(node).__name__}'"
        )

    def visit_children(self, node: ASTNode) -> None:
        """Helper: kunjungi semua atribut yang merupakan ASTNode."""
        for attr_name in vars(node):
            attr = getattr(node, attr_name)
            if isinstance(attr, ASTNode):
                attr.accept(self)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ASTNode):
                        item.accept(self)
                    elif isinstance(item, tuple):
                        for sub in item:
                            if isinstance(sub, ASTNode):
                                sub.accept(self)
