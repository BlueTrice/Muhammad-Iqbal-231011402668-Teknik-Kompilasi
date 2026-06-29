# AST (Abstract Syntax Tree) — Dokumentasi Teknis

## Ikhtisar

AST adalah representasi pohon dari struktur program JogLang. Setiap konstruksi bahasa (deklarasi, ekspresi, pernyataan) direpresentasikan sebagai node dalam pohon ini. AST diproduksi oleh Parser dan digunakan oleh Semantic Analyzer, Optimizer, dan Code Generator.

File: `joglang_compiler/ast_nodes.py`

---

## Desain

### Base Class

Semua node mewarisi dari `ASTNode`:

```python
@dataclass
class ASTNode:
    line:   int = 0    # nomor baris di source code
    column: int = 0    # nomor kolom di source code

    def accept(self, visitor: ASTVisitor) -> Any:
        method_name    = f"visit_{type(self).__name__}"
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)
```

Method `accept()` mengimplementasikan **Visitor Pattern** — memungkinkan Semantic Analyzer, Optimizer, dan Code Generator berjalan di atas AST tanpa mengubah class node.

---

## Hierarki Node

### Program

```
ASTNode
└── ProgramNode          ← root seluruh program
      body: list[ASTNode]
```

### Statement Nodes

```
ASTNode
├── VariableDeclarationNode   angka x = 5
│     var_type: str           'angka' | 'pecahan' | 'teks' | 'bener_salah'
│     name:     str
│     initializer: ASTNode?
│
├── AssignmentNode            x = 10  |  x += 5
│     name:     str
│     operator: str           '=' | '+=' | '-=' | '*=' | '/='
│     value:    ASTNode
│
├── PrintNode                 tampilna(expr)
│     expression: ASTNode
│
├── InputNode                 takon("prompt")
│     prompt: ASTNode?
│
├── ReturnNode                balekna expr
│     value: ASTNode?
│
├── BreakNode                 mandheg
│
└── ContinueNode              terusna
```

### Control Flow Nodes

```
ASTNode
├── BlockNode                 { statement* }
│     statements: list[ASTNode]
│
├── IfNode                    yen ... liyane_yen ... liyane
│     condition:     ASTNode
│     then_branch:   BlockNode
│     elif_branches: list[(ASTNode, BlockNode)]
│     else_branch:   BlockNode?
│
├── WhileNode                 nalika cond { }
│     condition: ASTNode
│     body:      BlockNode
│
└── ForNode                   baleni init ; cond ; update { }
      init:      ASTNode      (VariableDeclarationNode | AssignmentNode)
      condition: ASTNode
      update:    ASTNode      (AssignmentNode)
      body:      BlockNode
```

### Function Nodes

```
ASTNode
├── ParameterNode             angka x  (parameter fungsi)
│     param_type: str
│     name:       str
│
├── FunctionNode              gawe nama(params) { body }
│     name:        str
│     params:      list[ParameterNode]
│     return_type: str?       (belum diimplementasikan di grammar)
│     body:        BlockNode
│
└── CallNode                  nama(args)
      name:      str
      arguments: list[ASTNode]
```

### Expression Nodes

```
ASTNode
├── BinaryOperationNode       left op right
│     left:     ASTNode
│     operator: str           '+' '-' '*' '/' '%' '**'
│     right:    ASTNode       '==' '!=' '<' '>' '<=' '>='
│                             'lan' 'utawa'
│
├── UnaryOperationNode        op operand
│     operator: str           '-' | 'ora'
│     operand:  ASTNode
│
├── VariableNode              nama variabel
│     name: str
│
└── LiteralNode               42 | 3.14 | "halo" | bener | kosong
      value: int|float|str|bool|None
      kind:  str              'int' | 'float' | 'string' | 'bool' | 'null'
```

---

## Visitor Pattern

`ASTVisitor` adalah base class untuk semua komponen yang memproses AST:

```python
class ASTVisitor:
    def generic_visit(self, node: ASTNode) -> Any:
        raise NotImplementedError(...)

    def visit_children(self, node: ASTNode) -> None:
        """Helper: kunjungi semua anak yang merupakan ASTNode."""
        for attr in vars(node).values():
            if isinstance(attr, ASTNode):
                attr.accept(self)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ASTNode):
                        item.accept(self)
```

Implementasi Visitor:

| Visitor           | Tujuan                             |
|-------------------|------------------------------------|
| `SemanticAnalyzer`| Memeriksa kebenaran semantik      |
| `Optimizer`       | Menyederhanakan/mengoptimasi AST  |
| `CodeGenerator`   | Menghasilkan kode Python           |

---

## Contoh AST Lengkap

Source code:
```joglang
wiwiti
    gawe kuadrat(angka x) {
        balekna x * x
    }
    tampilna(kuadrat(5))
rampung
```

AST:
```
ProgramNode(
  body=[
    FunctionNode(
      name='kuadrat',
      params=[ParameterNode(param_type='angka', name='x')],
      body=BlockNode(
        statements=[
          ReturnNode(
            value=BinaryOperationNode(
              left=VariableNode(name='x'),
              operator='*',
              right=VariableNode(name='x')
            )
          )
        ]
      )
    ),
    PrintNode(
      expression=CallNode(
        name='kuadrat',
        arguments=[LiteralNode(value=5, kind='int')]
      )
    )
  ]
)
```

---

## Menambah Node Baru

Untuk menambah konstruksi baru ke JogLang:

1. Buat `@dataclass` baru di `ast_nodes.py` yang mewarisi `ASTNode`
2. Tambahkan method `visit_NamaNodeBaru()` di semua visitor
3. Tambahkan aturan grammar di `parser.py`
4. Tambahkan handler di `codegen.py` untuk menghasilkan Python

Contoh:
```python
@dataclass
class KomentarNode(ASTNode):
    """Komentar yang dipreservasi ke output."""
    text: str = ""
```
