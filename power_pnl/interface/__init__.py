### interface/__init__.py

"""
Pacote `interface`

Define a interface de alto nível para criação simbólica de modelos de
otimização. Permite ao usuário declarar função objetivo com minimizar()
ou maximizar(), e restrições diretamente com operadores simbólicos.

- SymbolicModel: interface principal de modelagem simbólica
- minimizar, maximizar: funções auxiliares para declaração do objetivo

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .model import SymbolicModel
from .objetivo import minimizar, maximizar, objetivo

__all__ = [
    "SymbolicModel",
    "minimizar",
    "maximizar",
    "objetivo",
]
