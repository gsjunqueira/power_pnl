"""
Pacote ""power_pnl""

Framework completo para modelagem e resolução simbólica de problemas
não lineares restritos, com construção da Lagrangeana, cálculo de derivadas,
e resolução com detecção automática de linearidade.

Subpacotes:
- models: representação simbólica dos dados de entrada (variáveis, restrições, objetivo)
- engine: montagem e análise simbólica (Lagrangeana, derivadas)
- interface: API de alto nível para uso direto do usuário
- solver: resolução simbólica (linear e não linear)

Autor: Giovani Santiago Junqueira
"""

from . import models
from . import engine
from . import interface
from . import solver
from . import symbolic

__all__ = [
    "models", "engine", "interface", "solver", "symbolic"
]
