"""
Módulo `variables`

Define a classe VariableSet que encapsula todas as variáveis simbólicas
do problema de otimização (decisão, multiplicadores, auxiliares).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import sympy as sp


class VariableSet:
    """
    Conjunto completo de variáveis simbólicas para o problema de otimização.
    """

    def __init__(self,
                 n_decision: int,
                 n_eq: int = 0,
                 n_ineq_up: int = 0,
                 n_ineq_dn: int = 0,
                 prefix_decision: str = "x"):
        """
        Inicializa todas as variáveis simbólicas.

        Args:
            n_decision (int): Número de variáveis de decisão.
            n_eq (int): Número de restrições de igualdade.
            n_ineq_up (int): Número de restrições ≤.
            n_ineq_dn (int): Número de restrições ≥.
            prefix_decision (str): Prefixo das variáveis de decisão (default = 'x').
        """
        self.x = sp.symbols(f'{prefix_decision}1:{n_decision+1}')
        self.lmd = sp.symbols(f'lambda1:{n_eq+1}') if n_eq > 0 else ()
        self.pi_up = sp.symbols(f'pi_up1:{n_ineq_up+1}') if n_ineq_up > 0 else ()
        self.pi_dn = sp.symbols(f'pi_dn1:{n_ineq_dn+1}') if n_ineq_dn > 0 else ()
        self.n_ineq = n_ineq_up + n_ineq_dn
        self.s = sp.symbols(f's1:{self.n_ineq+1}') if self.n_ineq > 0 else ()


    def all_symbols(self) -> tuple:
        """
        Retorna todas as variáveis simbólicas do modelo.

        Returns:
            tuple: Tupla concatenada com todas as variáveis.
        """
        return list(self.x) + list(self.lmd) + list(self.pi_up) + list(self.pi_dn) + list(self.s)

    def as_dict(self) -> dict:
        """
        Retorna as variáveis agrupadas por tipo.

        Returns:
            dict: Dicionário com chaves ['x', 'lmd', 'pi_up', 'pi_dn', 's']
        """
        return {
            "x": self.x,
            "lmd": self.lmd,
            "pi_up": self.pi_up,
            "pi_dn": self.pi_dn,
            "s": self.s
        }
