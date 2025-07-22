"""
Pacote `models`

Contém as classes responsáveis por representar simbolicamente os dados de entrada
do problema de otimização não linear:

- VariableSet: conjunto de variáveis simbólicas (x, λ, π, s)
- ConstraintSet: restrições de igualdade e desigualdade
- ObjectiveFunction: expressão simbólica da função objetivo

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .variables import VariableSet
from .constants import ConstantSet
from .constraints import ConstraintSet
from .objective import ObjectiveFunction

__all__ = [
    "VariableSet",
    "ConstantSet",
    "ConstraintSet",
    "ObjectiveFunction",
]
