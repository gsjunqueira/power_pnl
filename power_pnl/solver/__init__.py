"""
Pacote solver

Contém os módulos de resolução simbólica e numérica de sistemas gerados a partir
da Lagrangeana. Atualmente, o pacote inclui:

- SymbolicSolver: resolve sistemas lineares via inversão e não lineares via Newton simbólico

Futuras extensões podem incluir: métodos de barreira, penalidade, resolução iterativa com
aproximações da Hessiana.

Autor: Giovani Santiago Junqueira
"""

from .solver import SymbolicSolver

__all__ = [
    "SymbolicSolver"
]
