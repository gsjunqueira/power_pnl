"""
Módulo `derivatives`

Define a classe DerivativesCalculator que calcula o gradiente e a hessiana
de uma expressão simbólica (em geral, a Lagrangeana), com relação às variáveis
fornecidas (por padrão: todas as do VariableSet ou apenas x).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import sympy as sp
from sympy import Expr, diff, hessian
from power_pnl.models import VariableSet


class DerivativesCalculator:
    """
    Calcula derivadas simbólicas de uma expressão com relação a um conjunto de variáveis.
    """

    def __init__(self, expression: Expr, variables: VariableSet):
        """
        Inicializa o objeto com a expressão e o conjunto de variáveis.

        Args:
            expression (Expr): Expressão simbólica a ser derivada (ex: Lagrangeana).
            variables (VariableSet): Conjunto de variáveis (x, lmd, pi, s).
        """
        self.expr = expression
        self.vars = variables

    def gradient(self, subset: str = "all") -> list[Expr]:
        """
        Calcula o gradiente da expressão em relação ao subconjunto de variáveis escolhido.

        Args:
            subset (str): Quais variáveis usar:
                - 'all'  → todas (x, lambda, pi_up, pi_dn, s)
                - 'x'    → somente variáveis de decisão
                - 'lmd'  → somente multiplicadores de igualdade
                - 'pi'   → somente pi_up e pi_dn
                - 's'    → somente variáveis auxiliares

        Returns:
            list[Expr]: Lista com as derivadas parciais (gradiente).
        """
        if subset == "all":
            varset = self.vars.all_symbols()
        elif subset == "x":
            varset = self.vars.x
        elif subset == "lmd":
            varset = self.vars.lmd
        elif subset == "pi":
            varset = self.vars.pi_up + self.vars.pi_dn
        elif subset == "s":
            varset = self.vars.s
        else:
            raise ValueError(f"Subset inválido: {subset}")

        return [diff(self.expr, v) for v in varset]

    def hessian(self, subset: str = "all") -> sp.Matrix:
        """
        Calcula a matriz Hessiana da expressão com base nas variáveis do gradiente.

        Args:
            subset (str): Quais variáveis utilizar ('x', 'all', 'lmd', 'pi', 's').

        Returns:
            Matrix: Matriz Hessiana simbólica ∇²f(v) com v ∈ subset.
        """
        if subset == "all":
            varset = self.vars.all_symbols()
        elif subset == "x":
            varset = self.vars.x
        elif subset == "lmd":
            varset = self.vars.lmd
        elif subset == "pi":
            varset = self.vars.pi_up + self.vars.pi_dn
        elif subset == "s":
            varset = self.vars.s
        else:
            raise ValueError(f"Subset inválido: {subset}")

        return hessian(self.expr, varset)
