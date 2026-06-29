"""
errors.py — Definisi kelas error untuk JogLang Compiler.

Semua error yang mungkin terjadi selama proses kompilasi
didefinisikan di sini agar konsisten dan mudah diidentifikasi.
"""


class JogLangError(Exception):
    """Base class untuk semua error JogLang."""

    def __init__(self, message: str, line: int = 0, column: int = 0) -> None:
        self.message = message
        self.line    = line
        self.column  = column
        super().__init__(self._format())

    def _format(self) -> str:
        if self.line:
            return f"[Baris {self.line}, Kolom {self.column}] {self.__class__.__name__}: {self.message}"
        return f"{self.__class__.__name__}: {self.message}"

    def __str__(self) -> str:
        return self._format()


class LexicalError(JogLangError):
    """Error saat proses tokenisasi (Lexer)."""
    pass


class SyntaxError_(JogLangError):
    """Error saat proses parsing (Parser). Nama diakhiri _ agar tidak tabrakan dengan built-in."""
    pass


class SemanticError(JogLangError):
    """Error saat analisis semantik."""
    pass


class CodeGenerationError(JogLangError):
    """Error saat proses code generation."""
    pass


class OptimizationError(JogLangError):
    """Error saat proses optimasi."""
    pass
