"""
Módulo `hydro_system`

Define a classe `HydroSystem`, que representa um sistema composto por múltiplas
usinas hidrelétricas. Permite operações agregadas como despacho hídrico total
e atualização sincronizada dos volumes de reservatórios.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass, field
from typing import List, Callable
from .hydro_plant import HydroPlant

@dataclass
class HydroSystem:
    """
    Representa um sistema hídrico contendo múltiplas usinas hidrelétricas.

    Atributos:
        plants (List[HydroPlant]): Lista de usinas hidrelétricas no sistema.
    """
    plants: List[HydroPlant] = field(default_factory=list)

    def add_plant(self, plant: HydroPlant):
        """
        Adiciona uma usina ao sistema.

        Args:
            plant (HydroPlant): Instância de usina a ser adicionada.
        """
        self.plants.append(plant)

    def get_total_generation(self, period: int) -> float:
        """
        Soma da geração de todas as usinas no período.

        Args:
            period (int): Período de despacho.

        Returns:
            float: Geração total do sistema hídrico (MW).
        """
        return sum(p.get_total_generation(period) for p in self.plants)

    def update_all_volumes(self, period: int):
        """
        Atualiza o volume dos reservatórios de todas as usinas.

        Args:
            period (int): Período atual.
        """
        for plant in self.plants:
            plant.update_volume(period)

    def get_total_energy_generated(self, periods: List[int]) -> float:
        """
        Calcula a energia gerada no sistema ao longo de vários períodos.

        Args:
            periods (List[int]): Lista de períodos.

        Returns:
            float: Energia total gerada (MWh).
        """
        return sum(
            sum(plant.get_total_generation(p) for p in periods)
            for plant in self.plants
        )

    def get_total_volume(self) -> float:
        """
        Retorna o volume total somado de todos os reservatórios no estado atual.

        Returns:
            float: Volume total (hm³).
        """
        return sum(plant.volume_atual for plant in self.plants)

    def apply_policy(self, policy: Callable[[HydroPlant, int], None], period: int):
        """
        Aplica uma política de operação a cada usina no período informado.

        Args:
            policy (Callable): Função que recebe uma usina e o período.
            period (int): Período atual.
        """
        for plant in self.plants:
            policy(plant, period)

    def reset_all(self):
        """
        Restaura o volume e histórico de todas as usinas ao estado inicial.
        """
        for plant in self.plants:
            if hasattr(plant, "historico_volumes"):
                plant.historico_volumes.clear()
            plant.volume_atual = plant.volume_max
            plant.vertimento = 0.0

    def __repr__(self):
        """
        Representação textual resumida do sistema hídrico.

        Returns:
            str: Lista de identificadores de usinas.
        """
        ids = ", ".join(p.id for p in self.plants)
        return f"<HydroSystem: {ids}>"
