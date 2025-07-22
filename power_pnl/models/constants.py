"""
Módulo `constants`

Define a classe ConstantSet que encapsula constantes simbólicas
utilizadas no problema de otimização, como o parâmetro de barreira μ.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import sympy as sp


class ConstantSet:
    """
    Conjunto de constantes simbólicas do problema de otimização.
    """

    def __init__(self, include_mi: bool = False):
        """
        Inicializa as constantes simbólicas.

        Args:
            include_mi (bool): Se True, inclui o parâmetro μ.
        """
        self.mi = sp.Symbol("mi", real=True) if include_mi else None

    def all_symbols(self) -> list:
        """
        Retorna todas as constantes simbólicas definidas.

        Returns:
            list: Lista de símbolos.
        """
        return [c for c in (self.mi,) if c is not None]

    def as_dict(self) -> dict:
        """
        Retorna as constantes em formato dicionário.

        Returns:
            dict: {'mi': Symbol('mi')}
        """
        return {
            "mi": self.mi
        } if self.mi is not None else {}
