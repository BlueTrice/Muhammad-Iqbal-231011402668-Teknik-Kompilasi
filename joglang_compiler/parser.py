"""
parser.py — Recursive Descent Parser untuk JogLang Compiler.

Parser menerima list Token dari Lexer dan membangun AST.
Menggunakan teknik Recursive Descent Parsing (top-down).

Grammar (EBNF):
    program         ::= 'wiwiti' statement* 'rampung'
    statement       ::= var_decl
                      | assignment_stmt
                      | print_stmt
                      | input_stmt
                      | if_stmt
                      | while_stmt
                      | for_stmt
                      | function_decl
                      | return_stmt
                      | break_stmt
                      | continue_stmt
                      | expr_stmt
    var_decl        ::= datatype IDENTIFIER ('=' expression)? ';'?
    assignment_stmt ::= IDENTIFIER assign_op expression ';'?
    assign_op       ::= '=' | '+=' | '-=' | '*=' | '/='
    print_stmt      ::= 'tampilna' '(' expression ')' ';'?
    input_stmt      ::= 'takon' '(' expression? ')' ';'?
    if_stmt         ::= 'yen' expression block
                        ('liyane_yen' expression block)*
                        ('liyane' block)?
    while_stmt      ::= 'nalika' expression block
    for_stmt        ::= 'baleni' for_init ';' expression ';' for_update block
    for_init        ::= var_decl_no_semi | assignment_no_semi
    for_update      ::= assignment_no_semi
    function_decl   ::= 'gawe' IDENTIFIER '(' param_list? ')' block
    param_list      ::= param (',' param)*
    param           ::= datatype IDENTIFIER
    return_stmt     ::= 'balekna' expression? ';'?
    break_stmt      ::= 'mandheg' ';'?
    continue_stmt   ::= 'terusna' ';'?
    block           ::= '{' statement* '}'
    expression      ::= or_expr
    or_expr         ::= and_expr ('utawa' and_expr)*
    and_expr        ::= not_expr ('lan' not_expr)*
    not_expr        ::= 'ora' not_expr | comparison
    comparison      ::= addition (('=='|'!='|'<'|'>'|'<='|'>=') addition)*
    addition        ::= multiplication (('+' | '-') multiplication)*
    multiplication  ::= unary (('*' | '/' | '%') unary)*
    power           ::= unary ('**' unary)*
    unary           ::= '-' unary | primary
    primary         ::= INT_LIT | FLOAT_LIT | STRING_LIT
                      | 'bener' | 'salah' | 'kosong'
                      | IDENTIFIER '(' arg_list? ')'
                      | IDENTIFIER
                      | '(' expression ')'
                      | input_expr
    input_expr      ::= 'takon' '(' expression? ')'
    arg_list        ::= expression (',' expression)*
    datatype        ::= 'angka' | 'pecahan' | 'teks' | 'bener_salah'
"""

from __future__ import annotations
from typing import Optional

from .token import Token, TokenType
from .ast_nodes import (
    ASTNode, ProgramNode, VariableDeclarationNode, AssignmentNode,
    PrintNode, InputNode, ReturnNode, BreakNode, ContinueNode,
    BlockNode, IfNode, WhileNode, ForNode,
    ParameterNode, FunctionNode, CallNode,
    BinaryOperationNode, UnaryOperationNode, VariableNode, LiteralNode,
)
from .errors import SyntaxError_


# Tipe data yang valid sebagai TokenType
DATATYPE_TOKENS = (
    TokenType.DATATYPE_INT,
    TokenType.DATATYPE_FLOAT,
    TokenType.DATATYPE_STR,
    TokenType.DATATYPE_BOOL,
)

# Operator assignment
ASSIGN_OPS = (
    TokenType.ASSIGN,
    TokenType.PLUS_ASSIGN,
    TokenType.MINUS_ASSIGN,
    TokenType.STAR_ASSIGN,
    TokenType.SLASH_ASSIGN,
)

# Operator perbandingan
COMPARISON_OPS = (
    TokenType.EQ, TokenType.NEQ,
    TokenType.LT, TokenType.GT,
    TokenType.LTE, TokenType.GTE,
)


class Parser:
    """
    Recursive Descent Parser untuk JogLang.

    Usage:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
    """

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens:  list[Token] = tokens
        self._pos:     int         = 0

    # -----------------------------------------------------------------------
    # HELPER METHODS
    # -----------------------------------------------------------------------

    @property
    def _current(self) -> Token:
        """Token saat ini."""
        return self._tokens[self._pos]

    @property
    def _peek(self) -> Token:
        """Lihat token berikutnya tanpa maju."""
        nxt = self._pos + 1
        if nxt < len(self._tokens):
            return self._tokens[nxt]
        return self._tokens[-1]  # EOF

    def _advance(self) -> Token:
        """Ambil token saat ini dan maju ke berikutnya."""
        tok = self._current
        if self._pos < len(self._tokens) - 1:
            self._pos += 1
        return tok

    def _check(self, *types: TokenType) -> bool:
        """Cek apakah token saat ini bertipe salah satu dari types."""
        return self._current.type in types

    def _match(self, *types: TokenType) -> bool:
        """Jika cocok, maju dan return True; jika tidak, return False."""
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, token_type: TokenType, message: str = "") -> Token:
        """
        Ambil token yang diharapkan. Jika tidak cocok, lempar SyntaxError_.
        """
        if self._check(token_type):
            return self._advance()
        tok = self._current
        msg = message or (
            f"Diharapkan '{token_type.name}', "
            f"tapi ditemukan '{tok.lexeme}' ({tok.type.name})"
        )
        raise SyntaxError_(msg, line=tok.line, column=tok.column)

    def _skip_semicolons(self) -> None:
        """Skip opsional titik-koma."""
        while self._check(TokenType.SEMICOLON):
            self._advance()

    def _at_end(self) -> bool:
        return self._current.type == TokenType.EOF

    def _current_line_col(self) -> tuple[int, int]:
        return self._current.line, self._current.column

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def parse(self) -> ProgramNode:
        """
        Entry point parser.

        Returns:
            ProgramNode — root AST

        Raises:
            SyntaxError_: jika ada kesalahan sintaks
        """
        line, col = self._current_line_col()
        self._expect(TokenType.WIWITI, "Program harus dimulai dengan 'wiwiti'")

        body: list[ASTNode] = []
        while not self._check(TokenType.RAMPUNG) and not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                body.append(stmt)

        self._expect(TokenType.RAMPUNG, "Program harus diakhiri dengan 'rampung'")

        if not self._at_end():
            tok = self._current
            raise SyntaxError_(
                f"Token tidak terduga setelah 'rampung': '{tok.lexeme}'",
                line=tok.line, column=tok.column,
            )

        return ProgramNode(body=body, line=line, column=col)

    # -----------------------------------------------------------------------
    # STATEMENT PARSERS
    # -----------------------------------------------------------------------

    def _parse_statement(self) -> Optional[ASTNode]:
        """Dispatcher utama untuk semua jenis statement."""
        self._skip_semicolons()
        if self._at_end() or self._check(TokenType.RAMPUNG, TokenType.RBRACE):
            return None

        tok = self._current

        # Deklarasi variabel
        if self._check(*DATATYPE_TOKENS):
            return self._parse_var_decl()

        # Function declaration
        if self._check(TokenType.GAWE):
            return self._parse_function_decl()

        # Return
        if self._check(TokenType.BALEKNA):
            return self._parse_return()

        # Break
        if self._check(TokenType.MANDHEG):
            line, col = tok.line, tok.column
            self._advance()
            self._skip_semicolons()
            return BreakNode(line=line, column=col)

        # Continue
        if self._check(TokenType.TERUSNA):
            line, col = tok.line, tok.column
            self._advance()
            self._skip_semicolons()
            return ContinueNode(line=line, column=col)

        # Print
        if self._check(TokenType.TAMPILNA):
            return self._parse_print()

        # If
        if self._check(TokenType.YEN):
            return self._parse_if()

        # While
        if self._check(TokenType.NALIKA):
            return self._parse_while()

        # For
        if self._check(TokenType.BALENI):
            return self._parse_for()

        # Assignment atau expression statement
        # Bedakan: IDENTIFIER diikuti operator assign  => AssignmentNode
        #          selain itu                           => ekspresi biasa
        if self._check(TokenType.IDENTIFIER) and self._peek.type in ASSIGN_OPS:
            return self._parse_assignment()

        # Expression statement (termasuk pemanggilan fungsi standalone)
        expr = self._parse_expression()
        self._skip_semicolons()
        return expr

    def _parse_var_decl(self, allow_semi: bool = True) -> VariableDeclarationNode:
        """
        var_decl ::= datatype IDENTIFIER ('=' expression)? ';'?
        """
        type_tok = self._advance()          # konsumsi tipe data
        var_type = type_tok.lexeme
        line, col = type_tok.line, type_tok.column

        name_tok = self._expect(
            TokenType.IDENTIFIER,
            f"Diharapkan nama variabel setelah '{var_type}'"
        )
        name = name_tok.lexeme

        initializer: Optional[ASTNode] = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()

        if allow_semi:
            self._skip_semicolons()

        return VariableDeclarationNode(
            var_type=var_type, name=name, initializer=initializer,
            line=line, column=col,
        )

    def _parse_assignment(self) -> AssignmentNode:
        """
        assignment_stmt ::= IDENTIFIER assign_op expression ';'?
        """
        name_tok = self._advance()   # IDENTIFIER
        op_tok   = self._advance()   # operator assign
        line, col = name_tok.line, name_tok.column

        value = self._parse_expression()
        self._skip_semicolons()

        return AssignmentNode(
            name=name_tok.lexeme, operator=op_tok.lexeme, value=value,
            line=line, column=col,
        )

    def _parse_print(self) -> PrintNode:
        """
        print_stmt ::= 'tampilna' '(' expression ')' ';'?
        """
        line, col = self._current.line, self._current.column
        self._advance()   # 'tampilna'
        self._expect(TokenType.LPAREN, "Diharapkan '(' setelah 'tampilna'")
        expr = self._parse_expression()
        self._expect(TokenType.RPAREN, "Diharapkan ')' setelah ekspresi tampilna")
        self._skip_semicolons()
        return PrintNode(expression=expr, line=line, column=col)

    def _parse_input_expr(self) -> InputNode:
        """
        input_expr ::= 'takon' '(' expression? ')'
        """
        line, col = self._current.line, self._current.column
        self._advance()   # 'takon'
        self._expect(TokenType.LPAREN, "Diharapkan '(' setelah 'takon'")
        prompt: Optional[ASTNode] = None
        if not self._check(TokenType.RPAREN):
            prompt = self._parse_expression()
        self._expect(TokenType.RPAREN, "Diharapkan ')' setelah prompt takon")
        return InputNode(prompt=prompt, line=line, column=col)

    def _parse_return(self) -> ReturnNode:
        """
        return_stmt ::= 'balekna' expression? ';'?
        """
        line, col = self._current.line, self._current.column
        self._advance()   # 'balekna'

        value: Optional[ASTNode] = None
        # Jika token berikutnya bukan '}', ';', 'rampung', atau EOF
        # maka ada nilai yang dikembalikan
        if not self._check(
            TokenType.RBRACE, TokenType.SEMICOLON,
            TokenType.RAMPUNG, TokenType.EOF
        ):
            value = self._parse_expression()

        self._skip_semicolons()
        return ReturnNode(value=value, line=line, column=col)

    def _parse_if(self) -> IfNode:
        """
        if_stmt ::= 'yen' expression block
                    ('liyane_yen' expression block)*
                    ('liyane' block)?
        """
        line, col = self._current.line, self._current.column
        self._advance()   # 'yen'

        condition   = self._parse_expression()
        then_branch = self._parse_block()

        elif_branches: list[tuple[ASTNode, BlockNode]] = []
        while self._check(TokenType.LIYANE_YEN):
            self._advance()   # 'liyane_yen'
            elif_cond  = self._parse_expression()
            elif_block = self._parse_block()
            elif_branches.append((elif_cond, elif_block))

        else_branch: Optional[BlockNode] = None
        if self._check(TokenType.LIYANE):
            self._advance()   # 'liyane'
            else_branch = self._parse_block()

        return IfNode(
            condition=condition,
            then_branch=then_branch,
            elif_branches=elif_branches,
            else_branch=else_branch,
            line=line, column=col,
        )

    def _parse_while(self) -> WhileNode:
        """
        while_stmt ::= 'nalika' expression block
        """
        line, col = self._current.line, self._current.column
        self._advance()   # 'nalika'
        condition = self._parse_expression()
        body      = self._parse_block()
        return WhileNode(condition=condition, body=body, line=line, column=col)

    def _parse_for(self) -> ForNode:
        """
        for_stmt ::= 'baleni' for_init ';' expression ';' for_update block
        """
        line, col = self._current.line, self._current.column
        self._advance()   # 'baleni'

        # Init: boleh var decl atau assignment
        if self._check(*DATATYPE_TOKENS):
            init = self._parse_var_decl(allow_semi=False)
        else:
            init = self._parse_assignment_no_semi()

        self._expect(TokenType.SEMICOLON, "Diharapkan ';' setelah init baleni")

        condition = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "Diharapkan ';' setelah kondisi baleni")

        update = self._parse_assignment_no_semi()
        body   = self._parse_block()

        return ForNode(
            init=init, condition=condition, update=update, body=body,
            line=line, column=col,
        )

    def _parse_assignment_no_semi(self) -> AssignmentNode:
        """Assignment tanpa mengkonsumsi semicolon (untuk for-loop)."""
        name_tok = self._expect(TokenType.IDENTIFIER, "Diharapkan identifier")
        if not self._check(*ASSIGN_OPS):
            tok = self._current
            raise SyntaxError_(
                f"Diharapkan operator assignment, ditemukan '{tok.lexeme}'",
                line=tok.line, column=tok.column,
            )
        op_tok = self._advance()
        value  = self._parse_expression()
        return AssignmentNode(
            name=name_tok.lexeme, operator=op_tok.lexeme, value=value,
            line=name_tok.line, column=name_tok.column,
        )

    def _parse_function_decl(self) -> FunctionNode:
        """
        function_decl ::= 'gawe' IDENTIFIER '(' param_list? ')' block
        """
        line, col = self._current.line, self._current.column
        self._advance()   # 'gawe'

        name_tok = self._expect(TokenType.IDENTIFIER, "Diharapkan nama fungsi setelah 'gawe'")
        self._expect(TokenType.LPAREN, "Diharapkan '(' setelah nama fungsi")

        params: list[ParameterNode] = []
        if not self._check(TokenType.RPAREN):
            params = self._parse_param_list()

        self._expect(TokenType.RPAREN, "Diharapkan ')' setelah parameter")

        body = self._parse_block()

        return FunctionNode(
            name=name_tok.lexeme, params=params, body=body,
            line=line, column=col,
        )

    def _parse_param_list(self) -> list[ParameterNode]:
        """param_list ::= param (',' param)*"""
        params = [self._parse_param()]
        while self._match(TokenType.COMMA):
            params.append(self._parse_param())
        return params

    def _parse_param(self) -> ParameterNode:
        """param ::= datatype IDENTIFIER"""
        if not self._check(*DATATYPE_TOKENS):
            tok = self._current
            raise SyntaxError_(
                f"Diharapkan tipe data parameter, ditemukan '{tok.lexeme}'",
                line=tok.line, column=tok.column,
            )
        type_tok = self._advance()
        name_tok = self._expect(TokenType.IDENTIFIER, "Diharapkan nama parameter")
        return ParameterNode(
            param_type=type_tok.lexeme, name=name_tok.lexeme,
            line=type_tok.line, column=type_tok.column,
        )

    def _parse_block(self) -> BlockNode:
        """block ::= '{' statement* '}'"""
        tok = self._current
        self._expect(TokenType.LBRACE, "Diharapkan '{' untuk membuka blok")
        line, col = tok.line, tok.column

        statements: list[ASTNode] = []
        while not self._check(TokenType.RBRACE, TokenType.EOF, TokenType.RAMPUNG):
            before = self._pos
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            # Guard: jika posisi tidak maju, skip satu token agar tidak hang
            if self._pos == before:
                self._advance()

        self._expect(TokenType.RBRACE, "Diharapkan '}' untuk menutup blok")
        return BlockNode(statements=statements, line=line, column=col)

    # -----------------------------------------------------------------------
    # EXPRESSION PARSERS (Operator Precedence — dari rendah ke tinggi)
    # -----------------------------------------------------------------------
    # Precedence (rendah -> tinggi):
    #   utawa  (or)
    #   lan    (and)
    #   ora    (not) — unary
    #   ==  !=  <  >  <=  >=
    #   +  -
    #   *  /  %
    #   **  (power)
    #   unary -
    #   primary

    def _parse_expression(self) -> ASTNode:
        return self._parse_or()

    def _parse_or(self) -> ASTNode:
        """or_expr ::= and_expr ('utawa' and_expr)*"""
        left = self._parse_and()
        while self._check(TokenType.UTAWA):
            op  = self._advance()
            right = self._parse_and()
            left  = BinaryOperationNode(
                left=left, operator=op.lexeme, right=right,
                line=op.line, column=op.column,
            )
        return left

    def _parse_and(self) -> ASTNode:
        """and_expr ::= not_expr ('lan' not_expr)*"""
        left = self._parse_not()
        while self._check(TokenType.LAN):
            op    = self._advance()
            right = self._parse_not()
            left  = BinaryOperationNode(
                left=left, operator=op.lexeme, right=right,
                line=op.line, column=op.column,
            )
        return left

    def _parse_not(self) -> ASTNode:
        """not_expr ::= 'ora' not_expr | comparison"""
        if self._check(TokenType.ORA):
            op      = self._advance()
            operand = self._parse_not()
            return UnaryOperationNode(
                operator=op.lexeme, operand=operand,
                line=op.line, column=op.column,
            )
        return self._parse_comparison()

    def _parse_comparison(self) -> ASTNode:
        """comparison ::= addition (cmp_op addition)*"""
        left = self._parse_addition()
        while self._check(*COMPARISON_OPS):
            op    = self._advance()
            right = self._parse_addition()
            left  = BinaryOperationNode(
                left=left, operator=op.lexeme, right=right,
                line=op.line, column=op.column,
            )
        return left

    def _parse_addition(self) -> ASTNode:
        """addition ::= multiplication (('+' | '-') multiplication)*"""
        left = self._parse_multiplication()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op    = self._advance()
            right = self._parse_multiplication()
            left  = BinaryOperationNode(
                left=left, operator=op.lexeme, right=right,
                line=op.line, column=op.column,
            )
        return left

    def _parse_multiplication(self) -> ASTNode:
        """multiplication ::= power (('*' | '/' | '%') power)*"""
        left = self._parse_power()
        while self._check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op    = self._advance()
            right = self._parse_power()
            left  = BinaryOperationNode(
                left=left, operator=op.lexeme, right=right,
                line=op.line, column=op.column,
            )
        return left

    def _parse_power(self) -> ASTNode:
        """power ::= unary ('**' unary)*  (right-associative)"""
        base = self._parse_unary()
        if self._check(TokenType.POWER):
            op  = self._advance()
            exp = self._parse_power()   # right-associative: rekursi kanan
            return BinaryOperationNode(
                left=base, operator=op.lexeme, right=exp,
                line=op.line, column=op.column,
            )
        return base

    def _parse_unary(self) -> ASTNode:
        """unary ::= '-' unary | primary"""
        if self._check(TokenType.MINUS):
            op      = self._advance()
            operand = self._parse_unary()
            return UnaryOperationNode(
                operator=op.lexeme, operand=operand,
                line=op.line, column=op.column,
            )
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        """
        primary ::= INT_LIT | FLOAT_LIT | STRING_LIT
                  | 'bener' | 'salah' | 'kosong'
                  | IDENTIFIER '(' arg_list? ')'
                  | IDENTIFIER
                  | '(' expression ')'
                  | input_expr
        """
        tok = self._current

        # Literal angka bulat
        if self._check(TokenType.INT_LIT):
            self._advance()
            return LiteralNode(value=tok.value, kind="int", line=tok.line, column=tok.column)

        # Literal angka desimal
        if self._check(TokenType.FLOAT_LIT):
            self._advance()
            return LiteralNode(value=tok.value, kind="float", line=tok.line, column=tok.column)

        # Literal string
        if self._check(TokenType.STRING_LIT):
            self._advance()
            return LiteralNode(value=tok.value, kind="string", line=tok.line, column=tok.column)

        # bener (True)
        if self._check(TokenType.TRUE):
            self._advance()
            return LiteralNode(value=True, kind="bool", line=tok.line, column=tok.column)

        # salah (False)
        if self._check(TokenType.FALSE):
            self._advance()
            return LiteralNode(value=False, kind="bool", line=tok.line, column=tok.column)

        # kosong (None)
        if self._check(TokenType.NULL):
            self._advance()
            return LiteralNode(value=None, kind="null", line=tok.line, column=tok.column)

        # Input ekspresi
        if self._check(TokenType.TAKON):
            return self._parse_input_expr()

        # Identifier: fungsi call atau variabel
        if self._check(TokenType.IDENTIFIER):
            self._advance()
            if self._check(TokenType.LPAREN):
                # Function call
                self._advance()   # '('
                args: list[ASTNode] = []
                if not self._check(TokenType.RPAREN):
                    args = self._parse_arg_list()
                self._expect(TokenType.RPAREN, f"Diharapkan ')' setelah argumen '{tok.lexeme}'")
                return CallNode(name=tok.lexeme, arguments=args, line=tok.line, column=tok.column)
            # Referensi variabel
            return VariableNode(name=tok.lexeme, line=tok.line, column=tok.column)

        # Grouped expression
        if self._check(TokenType.LPAREN):
            self._advance()   # '('
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "Diharapkan ')' untuk menutup ekspresi")
            return expr

        # Tidak ada yang cocok
        raise SyntaxError_(
            f"Ekspresi tidak valid: '{tok.lexeme}' ({tok.type.name})",
            line=tok.line, column=tok.column,
        )

    def _parse_arg_list(self) -> list[ASTNode]:
        """arg_list ::= expression (',' expression)*"""
        args = [self._parse_expression()]
        while self._match(TokenType.COMMA):
            args.append(self._parse_expression())
        return args


# ===========================================================================
# CONVENIENCE FUNCTION
# ===========================================================================

def parse(tokens: list[Token]) -> ProgramNode:
    """
    Fungsi shortcut untuk parsing.

    Args:
        tokens: List Token dari Lexer

    Returns:
        ProgramNode — root AST

    Raises:
        SyntaxError_: jika ada kesalahan sintaks
    """
    return Parser(tokens).parse()
