"""
Módulo `deficit`

Responsável por adicionar a variável de corte de carga (déficit) ao modelo de otimização,
bem como suas respectivas restrições e penalidades no custo total.

Essa modelagem permite capturar a insuficiência de geração em cenários onde a demanda
não pode ser totalmente atendida.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .bus import Bus

@dataclass
class Deficit:
    """
    Represents a load deficit (load shedding) at a given bus and time period.

    Attributes:
        id (str): Unique identifier of the deficit variable.
        bus (Bus): Bus to which the deficit is associated.
        period (int): Time index for the deficit.
        max_deficit (float): Upper bound for allowed load shedding [pu].
        cost (float): Penalty cost per unit of deficit [$ / pu].
    """
    id: str
    bus: "Bus"
    period: int
    max_deficit: float
    cost: float = 1e6

    def to_dict(self) -> dict:
        """
        Converte os atributos do déficit em um dicionário.

        Returns:
            dict: Representação dos atributos para exportação ou debug.
        """
        return {
            "id": self.id,
            "bus": self.bus,
            "period": self.period,
            "max_deficit": self.max_deficit,
            "cost": self.cost
        }

    def __post_init__(self):
        """
        Valida os atributos da variável de déficit.

        Raises:
            ValueError: Se valores inconsistentes forem fornecidos.
        """
        if self.max_deficit < 0:
            raise ValueError(f"[{self.id}] max_deficit deve ser não-negativo.")
        if self.cost < 0:
            raise ValueError(f"[{self.id}] custo de déficit deve ser não-negativo.")
        if not self.bus:
            raise ValueError(f"[{self.id}] referência de barra inválida.")
        self.bus.add_deficit(self)
