"""
Módulo `interfaces`

Define interfaces abstratas para elementos shunt e série no sistema elétrico.

Estas interfaces são utilizadas por dispositivos como reatores e capacitores
para garantir consistência na API de elementos passivos.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from electric_models.power import Bus, Line

# pylint: disable=too-few-public-methods

@dataclass(kw_only=True)
class ShuntElement(ABC):
    """
    Interface abstrata para elementos conectados em shunt a uma barra elétrica.

    Requer a implementação de:
        - get_susceptance(): retorna a susceptância total em pu.
    """
    id: str
    bus: "Bus"
    b: float
    status: bool = True

    @abstractmethod
    def get_susceptance(self) -> float:
        """Retorna a susceptância do elemento shunt (pu)."""

@dataclass(kw_only=True)
class SeriesElement(ABC):
    """
    Interface abstrata para elementos conectados em série a uma linha elétrica.

    Requer a implementação de:
        - get_reactance(): retorna a reatância total em pu ou ohms.
    """
    id: str
    line: "Line"
    x: float
    status: bool = True

    @abstractmethod
    def get_reactance(self) -> float:
        """Retorna a reatância do elemento série (pu ou ohms)."""
