"""
Módulo que define capacitores shunt e série para sistemas de potência.

- CapacitorShunt: conectado a uma barra (shunt), fornece potência reativa.
- CapacitorSeries: conectado em série com uma linha, compensa reatância.

Compatível com modelos de fluxo de potência AC e otimização (FPO).
Não aplicável para despacho ou confiabilidade.

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
class CapacitorShunt(ReliabilityMixin, ShuntElement):
    """
    Capacitor conectado à barra (shunt), representado por susceptância positiva.

    Atributos:
        id (str): Identificador único do capacitor.
        bus (Bus): Instância da barra onde está conectado.
        b (float): Susceptância (pu), valor positivo.
        status (bool): Indica se o capacitor está ativo.
    """
    id: str
    bus: "Bus"
    b: float
    status: bool = True

    def __post_init__(self):
        """Valida e associa automaticamente o capacitor à barra."""
        if self.b <= 0:
            raise ValueError(f"[{self.id}] Susceptância (b) deve ser positiva.")
        self.bus.add_shunt(self)

    def get_susceptance(self) -> float:
        """Retorna a susceptância (pu) do capacitor."""
        return self.b

    def is_operational(self) -> bool:
        """Indica se o capacitor está ativo no sistema."""
        return self.status

    def __repr__(self):
        """Representação resumida para debug."""
        return f"<CapacitorShunt id={self.id} bus={self.bus.id} b={self.b}>"


@dataclass(kw_only=True)
class CapacitorSeries(ReliabilityMixin, SeriesElement):
    """
    Capacitor conectado em série com uma linha, representado por reatância negativa.

    Atributos:
        id (str): Identificador único do capacitor.
        line (Line): Linha onde o capacitor está instalado.
        x (float): Reatância (pu ou ohms), valor negativo.
        status (bool): Indica se o capacitor está ativo.
    """
    id: str
    line: "Line"
    x: float
    status: bool = True

    def __post_init__(self):
        """Valida e associa automaticamente o capacitor à linha."""
        if self.x >= 0:
            raise ValueError(f"[{self.id}] Reatância (x) deve ser negativa.")
        self.line.add_series_element(self)

    def get_reactance(self) -> float:
        """Retorna a reatância (pu ou ohms) do capacitor série."""
        return self.x

    def is_operational(self) -> bool:
        """Indica se o capacitor está ativo no sistema."""
        return self.status

    def __repr__(self):
        """Representação resumida para debug."""
        return f"<CapacitorSeries id={self.id} line={self.line.id} x={self.x}>"
