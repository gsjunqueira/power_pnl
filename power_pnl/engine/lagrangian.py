"""
Módulo `lagrangian`

Define a classe LagrangianBuilder que constrói e armazena a expressão
simbólica da Lagrangeana com base nas variáveis, restrições e objetivo.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import sympy as sp
from power_pnl.models import VariableSet, ConstraintSet, ObjectiveFunction


class LagrangianBuilder:
    """
    Constrói e armazena a Lagrangeana simbólica de um problema com
    restrições de igualdade e desigualdade convertidas com s².
    """

    def __init__(self,
                 objective: ObjectiveFunction,
                 variables: VariableSet,
                 constraints: ConstraintSet,
                 mode: str = "min"):
        """
        Inicializa a construção da Lagrangeana.

        Args:
            objective (ObjectiveFunction): Função objetivo f(x).
            variables (VariableSet): Variáveis simbólicas.
            constraints (ConstraintSet): Conjunto de restrições.
            mode (str): 'min' para minimizar (default) ou 'max' para maximizar.
        """
        self.obj = objective
        self.vars = variables
        self.constraints = constraints
        self.mode = mode
        self.l = self._construir_lagrangeana()

    def _construir_lagrangeana(self) -> sp.Expr:
        """
        Gera a expressão simbólica da Lagrangeana.

        Returns:
            Expr: Lagrangeana simbólica.
        """
        f = self.obj.get()
        l = -f if self.mode == "max" else f

        # Igualdades: -lambda * h(x)
        for i, h in enumerate(self.constraints.equalities):
            l -= self.vars.lmd[i] * h

        # Desigualdades ≤: pi * (g(x) - b + s²)
        for j, (g, bound) in enumerate(self.constraints.inequalities_up):
            s_j = self.vars.s[j]
            expr = g - bound + s_j**2
            sinal = +1 if self.mode == "min" else -1
            l += sinal * self.vars.pi_up[j] * expr

        # Desigualdades ≥: pi * (g(x) - b - s²)
        for k, (g, bound) in enumerate(self.constraints.inequalities_dn):
            s_k = self.vars.s[len(self.constraints.inequalities_up) + k]
            expr = g - bound - s_k**2
            sinal = -1 if self.mode == "min" else +1
            l += sinal * self.vars.pi_dn[k] * expr

        return l

    def get_expression(self) -> sp.Expr:
        """
        Retorna a expressão simbólica da Lagrangeana.

        Returns:
            Expr: L(x, λ, π, s)
        """
        return self.l
