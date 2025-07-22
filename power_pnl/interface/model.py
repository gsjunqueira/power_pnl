"""
Classe `SymbolicModel`

Interface de alto nível para modelagem simbólica de problemas de otimização.
O usuário define a função objetivo com minimizar()/maximizar() e as restrições
com operadores simbólicos (<=, >=, ==). Internamente, essas informações são
convertidas para os objetos do núcleo (VariableSet, ConstraintSet, ObjectiveFunction).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import sympy as sp
from power_pnl.models import VariableSet, ConstraintSet, ObjectiveFunction

class SymbolicModel:
    """
    Interface declarativa para definição simbólica de um problema de otimização.
    Permite definir objetivo e restrições diretamente com expressões SymPy.
    """
    def __init__(self):
        """Inicializa um modelo vazio."""
        self._objective_expr = None
        self._objective_mode = "min"
        self._constraint_exprs = []

        self.variables = None
        self.objective = None
        self.constraints = None
        self.constants = None

    @property
    def mode(self):
        """Modo da função objetivo ('min' ou 'max')."""
        return self._objective_mode

    @property
    def obj(self):
        """Obtém a expressão da função objetivo."""
        return self._objective_expr

    @obj.setter
    def obj(self, value):
        """
        Define a função objetivo do modelo.

        Args:
            value (tuple): Tupla ("min" ou "max", expressão simbólica)
        """
        modo, expr = value
        if modo not in ("min", "max", "auto"):
            raise ValueError("Modo deve ser 'min' ou 'max' ou 'auto'")
        self._objective_mode = modo
        self._objective_expr = expr

    @property
    def constraints(self):
        """Obtém a lista de restrições simbólicas."""
        return self._constraint_exprs

    @constraints.setter
    def constraints(self, exprs):
        """
        Define as restrições do modelo.

        Args:
            exprs (list): Lista de expressões simbólicas com <=, >=, ==
        """
        self._constraint_exprs = exprs

    @property
    def constants(self):
        """Obtém o conjunto de constantes simbólicas."""
        return self._constants

    @constants.setter
    def constants(self, consts):
        """
        Define o conjunto de constantes simbólicas.

        Args:
            consts (ConstantSet): Objeto de constantes como mi.
        """
        self._constants = consts

    def build(self):
        """
        Constrói as representações simbólicas do modelo:
        - extrai variáveis
        - classifica restrições
        - monta VariableSet, ConstraintSet e ObjectiveFunction

        Returns:
            SymbolicModel: a própria instância com os objetos montados.
        """
        if self._objective_expr is None:
            raise ValueError("Função objetivo não definida.")

        todas_expr = [self._objective_expr] + self._constraint_exprs
        simbolos = sorted(list(set().union(*[expr.free_symbols for expr in todas_expr])), key=str)
        n_var = len(simbolos)

        self.variables = VariableSet(n_decision=n_var)

        self.objective = ObjectiveFunction()
        self.objective.set(self._objective_expr)

        restricoes = ConstraintSet()
        for expr in self._constraint_exprs:
            if isinstance(expr, sp.Equality):
                restricoes.equality(expr.lhs - expr.rhs)
            elif isinstance(expr, sp.StrictGreaterThan) or isinstance(expr, sp.GreaterThan):
                restricoes.lower_inequality(expr.lhs, expr.rhs)
            elif isinstance(expr, sp.StrictLessThan) or isinstance(expr, sp.LessThan):
                restricoes.upper_inequality(expr.lhs, expr.rhs)
            else:
                raise ValueError(f"Restricao não reconhecida: {expr}")
        self.constraints = restricoes
        self.variables = VariableSet(
            n_decision=n_var,
            n_eq=len(self.constraints.equalities),
            n_ineq_up=len(self.constraints.inequalities_up),
            n_ineq_dn=len(self.constraints.inequalities_dn)
        )
        self.variables.x = simbolos

        return self
