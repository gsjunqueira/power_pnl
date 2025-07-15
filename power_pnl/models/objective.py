"""
Módulo `objective`

Define a classe ObjectiveFunction para encapsular a função objetivo simbólica
de um problema de otimização. Permite definir e recuperar qualquer expressão
válida no SymPy, incluindo funções não lineares.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from typing import Optional
import sympy as sp
from sympy import Expr


class ObjectiveFunction:
    """
    Representa uma função objetivo simbólica f(x), arbitrária e genérica.
    """

    def __init__(self, expr: Optional[Expr] = None):
        """
        Inicializa a função objetivo.

        Args:
            expr (Expr, optional): Expressão simbólica da função objetivo.
                                   Pode ser definida depois via set().
        """
        self.expr = expr

    def set(self, expr: Expr):
        """
        Define a função objetivo simbolicamente.

        Args:
            expr (Expr): Expressão simbólica f(x).
        """
        self.expr = expr

    def get(self) -> Expr:
        """
        Retorna a função objetivo atual.

        Returns:
            Expr: Expressão simbólica f(x).
        """
        if self.expr is None:
            raise ValueError("A função objetivo ainda não foi definida.")
        return self.expr

    def __str__(self):
        return f"f(x) = {sp.pretty(self.get())}"
