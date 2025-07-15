"""
Módulo que define reatores shunt e série para sistemas de potência.

- ReactorShunt: conectado à barra, absorve potência reativa (susceptância negativa).
- ReactorSeries: conectado em série à linha, representa reatância positiva.

Aplicável a fluxo de potência AC, FPO e análise de estabilidade reativa.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from typing import TYPE_CHECKING
from electric_models import ReliabilityMixin
from .interfaces import ShuntElement, SeriesElement

if TYPE_CHECKING:
    from electric_models.power import Bus, Line


@dataclass(kw_only=True)
class ReactorShunt(ReliabilityMixin, ShuntElement):
    """
    Reator conectado à barra (shunt), representado por susceptância negativa.

    Atributos:
        id (str): Identificador do reator.
        bus (Bus): Instância da barra conectada.
        b (float): Susceptância (pu), valor negativo.
        status (bool): Indica se o reator está ativo.
    """
    id: str
    bus: "Bus"
    b: float
    status: bool = True

    def __post_init__(self):
        """Valida e associa automaticamente o reator à barra."""
        if self.b >= 0:
            raise ValueError(f"[{self.id}] Susceptância (b) de reator deve ser negativa.")
        self.bus.add_shunt(self)

    def get_susceptance(self) -> float:
        """Retorna a susceptância (pu) do reator."""
        return self.b

    def is_operational(self) -> bool:
        """Indica se o reator está ativo no sistema."""
        return self.status

    def __repr__(self):
        """Representação resumida para debug."""
        return f"<ReactorShunt id={self.id} bus={self.bus.id} b={self.b}>"

@dataclass(kw_only=True)
class ReactorSeries(ReliabilityMixin, SeriesElement):
    """
    Reator conectado em série com a linha, modelado por reatância positiva.

    Atributos:
        id (str): Identificador do reator.
        line (Line): Linha onde o reator está conectado.
        x (float): Reatância (pu ou ohms), valor positivo.
        status (bool): Indica se o reator está ativo.
    """
    id: str
    line: "Line"
    x: float
    status: bool = True

    def __post_init__(self):
        """Valida e associa automaticamente o reator à linha."""
        if self.x <= 0:
            raise ValueError(f"[{self.id}] Reatância (x) de reator série deve ser positiva.")
        self.line.add_series_element(self)

    def get_reactance(self) -> float:
        """Retorna a reatância (pu ou ohms) do reator série."""
        return self.x

    def is_operational(self) -> bool:
        """Indica se o reator está ativo no sistema."""
        return self.status

    def __repr__(self):
        """Representação resumida para debug."""
        return f"<ReactorSeries id={self.id} line={self.line.id} x={self.x}>"
