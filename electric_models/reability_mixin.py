"""
Módulo `reliability_mixin`

Define o mixin `ReliabilityMixin`, que adiciona suporte a parâmetros de confiabilidade
(como taxa de falha, MTTR, FOR etc.) para qualquer componente do sistema elétrico.

Autor: Giovani Santiago Junqueira
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ReliabilityMixin:
    """
    Mixin para adicionar atributos de confiabilidade a equipamentos elétricos.

    Atributos:
        taxa_falha (Optional[float]): λ - Taxa de falha [1/h].
        taxa_falha_transitoria (Optional[float]): λ' - Taxa de falha transiente [1/h].
        taxa_reparo (Optional[float]): μ - Taxa de reparo [1/h].
        mttr (Optional[float]): Tempo médio para reparo [h].
        mttf (Optional[float]): Tempo médio para falha [h].
        for_ (Optional[float]): Fator de saída forçada (FOR = λ / (λ + μ)).
    """
    taxa_falha: Optional[float] = None
    taxa_falha_transitoria: Optional[float] = None
    taxa_reparo: Optional[float] = None
    mttr: Optional[float] = None
    mttf: Optional[float] = None
    for_: Optional[float] = None

    def compute_reliability(self, verbose: bool = False):
        """
        Calcula os parâmetros de confiabilidade a partir dos dados existentes.

        A regra é:
        - Se o valor já existe, ele é mantido.
        - Se estiver ausente, será calculado com base nos outros, se possível.
        - Apenas o FOR depende de dois parâmetros.

        Args:
            verbose (bool): Se True, imprime os valores calculados.
        """
        # Repara e falha a partir de MTTR e MTTF
        if self.mttr is not None and self.taxa_reparo is None:
            self.taxa_reparo = 1 / self.mttr

        if self.mttf is not None and self.taxa_falha is None:
            self.taxa_falha = 1 / self.mttf

        # MTTR e MTTF a partir de taxas
        if self.taxa_reparo is not None and self.mttr is None:
            self.mttr = 1 / self.taxa_reparo

        if self.taxa_falha is not None and self.mttf is None:
            self.mttf = 1 / self.taxa_falha

        # FOR é o único que exige os dois
        if self.taxa_falha is not None and self.taxa_reparo is not None and self.for_ is None:
            self.for_ = self.taxa_falha / (self.taxa_falha + self.taxa_reparo)

        if verbose:
            print(f"[ReliabilityMixin] λ={self.taxa_falha}, μ={self.taxa_reparo}, "
                  f"MTTF={self.mttf}, MTTR={self.mttr}, FOR={self.for_}")
