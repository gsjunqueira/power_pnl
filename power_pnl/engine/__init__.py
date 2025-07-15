"""
Pacote `engine`

Contém as classes responsáveis pela construção e análise simbólica da estrutura
matemática do problema, com base nos dados definidos no pacote `model`.

- LagrangianBuilder: constrói a Lagrangeana simbólica do problema
- DerivativesCalculator: calcula gradiente e hessiana da expressão simbólica

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .lagrangian import LagrangianBuilder
from .derivatives import DerivativesCalculator
from .convexity import ConvexityAnalyzer

__all__ = [
    "LagrangianBuilder",
    "DerivativesCalculator",
    "ConvexityAnalyzer"
]
