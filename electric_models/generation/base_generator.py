"""
Módulo `base_generator`

Define a classe abstrata `BaseGenerator`, que serve como interface comum para
modelos de diferentes tipos de geradores em sistemas elétricos de potência. Essa base é
projetada para aplicações que envolvem fluxo de potência, despacho, confiabilidade, e planejamento.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from electric_models import ReliabilityMixin

if TYPE_CHECKING:
    from power import Bus

@dataclass(kw_only=True)
class BaseGenerator(ReliabilityMixin, ABC):
    """
    Classe base abstrata para representar um gerador genérico.

    Esta classe serve de interface para diversos tipos de geradores (térmicos, hidráulicos,
    eólicos, etc.) e permite compatibilidade com múltiplas aplicações, incluindo fluxo de potência,
    despacho econômico, e estudos de confiabilidade.

    Atributos:
        id (str): Identificador do gerador.
        bus (Bus): Instância da barra elétrica associada.

        # Fluxo de Potência e Despacho
        pg (Optional[float]): Potência ativa gerada (MW).
        qg (Optional[float]): Potência reativa gerada (MVAr).
        gmin (Optional[float]): Limite inferior de geração ativa (MW).
        gmax (Optional[float]): Limite superior de geração ativa (MW).
        qmin (Optional[float]): Limite inferior de geração reativa (MVAr).
        qmax (Optional[float]): Limite superior de geração reativa (MVAr).

        # Classificação
        type (str): Tipo do gerador (ex.: "thermal", "hydro", "wind", "dummy").
        fictitious (bool): True se representa unidade fictícia para modelagem de déficit.
        status (bool): True se a unidade está disponível para operação.

        # Parâmetros de Confiabilidade
        taxa_falha (Optional[float]): Taxa de falha (1/MTTF) [1/h].
        taxa_reparo (Optional[float]): Taxa de reparo (1/MTTR) [1/h].
        mttr (Optional[float]): Tempo médio para reparo (h).
        mttf (Optional[float]): Tempo médio para falha (h).
        for_ (Optional[float]): FOR - Fator de Saída Forçada (probabilidade).
    """

    id: str                      # Identificador único do gerador
    bus: "Bus"                   # Referência à barra elétrica a que está conectado

    # Operação elétrica
    pg: Optional[float] = None
    qg: Optional[float] = None
    gmin: Optional[float] = 0.
    gmax: Optional[float] = 0.
    qmin: Optional[float] = 0.
    qmax: Optional[float] = 0.

    # Classificação
    type: str = "generic"
    fictitious: bool = False
    status: bool = True

    @abstractmethod
    def get_power_output(self, period: int) -> float:
        """
        Retorna a potência gerada no período especificado (MW).

        Args:
            period (int): Índice do período.

        Returns:
            float: Potência gerada (MW).
        """

    def is_operational(self) -> bool:
        """
        Verifica se o gerador está operacional no momento.

        Returns:
            bool: True se está operando.
        """
        return self.status and not self.fictitious

    def available_capacity(self) -> Optional[float]:
        """
        Retorna a capacidade de potência disponível se operacional.

        Returns:
            Optional[float]: gmax se operacional, senão None.
        """
        return self.gmax if self.is_operational() else None

    def __repr__(self):
        """
        Retorna uma representação resumida do gerador para fins de debug.

        Returns:
            str: Uma string no formato "<TipoGenerator id=ID bus=BUS>".
        """
        return f"<{self.type.capitalize()}Generator id={self.id} bus={self.bus.id}>"

    def validate(self):
        """
        Valida os atributos internos do gerador, garantindo coerência nos dados.

        Raises:
            ValueError: Se alguma inconsistência for encontrada nos parâmetros.
        """
        # Verifica ID e barra
        if not self.id:
            raise ValueError("O gerador deve ter um identificador válido (id).")

        if self.bus is None:
            raise ValueError(f"O gerador {self.id} deve estar conectado a uma barra (bus).")

        # Validação dos limites de potência ativa
        if self.gmin is not None and self.gmax is not None:
            if self.gmin > self.gmax:
                raise ValueError(f"gmin > gmax para o gerador {self.id}.")

        # Validação dos limites de potência reativa (se fornecidos)
        if self.qmin is not None and self.qmax is not None:
            if self.qmin > self.qmax:
                raise ValueError(f"qmin > qmax para o gerador {self.id}.")

        # Parâmetros de confiabilidade: todos positivos se definidos
        for nome, valor in {
            "taxa_falha": self.taxa_falha,
            "taxa_reparo": self.taxa_reparo,
            "mttr": self.mttr,
            "mttf": self.mttf,
            "for_": self.for_,
        }.items():
            if valor is not None and valor < 0:
                raise ValueError(f"{nome} deve ser não negativo no gerador {self.id}.")

        # Se tipo inválido
        if not isinstance(self.type, str) or not self.type:
            raise ValueError(f"O gerador {self.id} deve ter um tipo válido (type=str).")

    def __post_init__(self):
        """
        Executa validações internas automaticamente após a criação da instância.

        Garante que os parâmetros definidos na inicialização sejam coerentes,
        evitando erros silenciosos durante simulações ou otimizações.

        Raises:
            ValueError: Caso alguma inconsistência seja identificada nos atributos do gerador.
        """
        self.validate()
        self.compute_reliability()

    def to_dict(self) -> dict:
        """
        Converte os atributos do gerador em um dicionário.

        Returns:
            dict: Representação dos dados do gerador.
        """
        return self.__dict__.copy()
