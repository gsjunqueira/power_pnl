"""
Módulo `hydro_generator`

Implementa a classe `HydroGenerator`, uma especialização de `BaseGenerator` voltada para
geradores hidrelétricos. Permite a futura integração de restrições de volume, afluência,
rampa hidráulica e produção de energia associada.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from .base_generator import BaseGenerator

if TYPE_CHECKING:
    from power import Bus
    from hydro import HydroPlant

@dataclass(kw_only=True)
class HydroGenerator(BaseGenerator):
    """
    Representa um gerador hidráulico individual.

    Atributos:
        productivity (float): Produtividade hídrica (MW/hm³).
        status (bool): Indica se o gerador está ativo.
        plant (HydroPlant): Referência à usina hidráulica à qual pertence.
    """

    productivity: Optional[float] = None
    plant: Optional["HydroPlant"] = None
    type: str = "hydro"

    def __post_init__(self):
        super().__post_init__()  # Validação do BaseGenerator
        self.bus.add_generator(self)
        if self.plant:
            self.plant.add_generator(self)
        if self.productivity is not None and self.productivity < 0:
            raise ValueError(f"[{self.id}] 'productivity' deve ser ≥ 0.")

    def get_power_output(self, period: int) -> float:
        """
        Retorna a potência gerada pela unidade hidráulica no período, considerando
        o volume turbinado da planta e a produtividade hídrica da unidade.

        A potência gerada é limitada pelos valores de gmax e gmin (se definidos).

        Args:
            period (int): Índice do período de simulação.

        Returns:
            float: Potência gerada (MW).
        """
        if not self.plant:
            return 0.0

        volume = self.plant.get_turbined_volume(period)
        potencia = self.productivity * volume

        if self.gmax is not None:
            potencia = min(potencia, self.gmax)
        if self.gmin is not None:
            potencia = max(potencia, self.gmin)

        return potencia

    def __repr__(self):
        """
        Representação textual resumida para debug.

        Returns:
            str: String no formato "<HydroGenerator id=... bus=...>".
        """
        return f"<HydroGenerator id={self.id} bus={self.bus.id}>"

def get_energy(self, period: int) -> Optional[float]:
    """
    Retorna a energia gerada no período, considerando produtividade e volume.

    Args:
        period (int): Índice do período.

    Returns:
        Optional[float]: Energia gerada (MWh), ou None se sem planta.
    """
    if not self.plant or self.productivity is None:
        return None
    return self.productivity * self.plant.get_turbined_volume(period)
