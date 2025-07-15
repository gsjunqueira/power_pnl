"""
Módulo `constraints`

Define a classe ConstraintSet, que armazena e organiza restrições simbólicas
de igualdade e desigualdade. Permite adicionar restrições de qualquer tipo simbólico,
com seus respectivos limites (quando necessário).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from typing import List
from sympy import Expr

class ConstraintSet:
    """
    Representa um conjunto de restrições simbólicas organizadas por tipo.
    """

    def __init__(self):
        self.equalities: List[Expr] = []
        self.inequalities_up: List[tuple[Expr, float]] = []
        self.inequalities_dn: List[tuple[Expr, float]] = []

    def equality(self, expr: Expr):
        """
        Adiciona uma restrição de igualdade h(x) = 0.

        Args:
            expr (Expr): Expressão simbólica da igualdade.
        """
        self.equalities.append(expr)

    def upper_inequality(self, expr: Expr, bound: float):
        """
        Adiciona uma desigualdade g(x) ≤ bound.

        Args:
            expr (Expr): Expressão simbólica g(x).
            bound (float): Limite superior.
        """
        self.inequalities_up.append((expr, bound))

    def lower_inequality(self, expr: Expr, bound: float):
        """
        Adiciona uma desigualdade g(x) ≥ bound.

        Args:
            expr (Expr): Expressão simbólica g(x).
            bound (float): Limite inferior.
        """
        self.inequalities_dn.append((expr, bound))

    def get_all(self) -> dict:
        """
        Retorna todas as restrições organizadas por tipo.

        Returns:
            dict: Contendo listas de 'equalities', 'inequalities_up', 'inequalities_dn'.
        """
        return {
            "equalities": self.equalities,
            "inequalities_up": self.inequalities_up,
            "inequalities_dn": self.inequalities_dn,
        }
