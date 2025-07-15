"""
Módulo `power_system`

Contém a classe `PowerSystem`, que encapsula a topologia do sistema elétrico,
incluindo suas barras, linhas, transformadores, cargas, geradores e elementos shunt.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from electric_models.power import Bus, Line
    from electric_models.transformers import Transformer

@dataclass
class PowerSystem:
    """
    Representa um sistema elétrico de potência completo.

    Atributos:
        buses (List[Bus]): Lista de barras do sistema.
        lines (List[Line]): Lista de linhas de transmissão.
        transformers (List[Transformer]): Lista de transformadores.
        pb (float): Potência base do sistema em MVA (default = 100.0).
    """
    buses: List["Bus"] = field(default_factory=list)
    lines: List["Line"] = field(default_factory=list)
    transformers: List["Transformer"] = field(default_factory=list)
    pb: float = 100.0

    def get_bus(self, bus_id: str) -> Optional["Bus"]:
        """Retorna a barra com o ID especificado, ou None se não existir."""
        for bus in self.buses:
            if bus.id == bus_id:
                return bus
        return None

    def get_all_generators(self) -> List:
        """Retorna todos os geradores conectados às barras do sistema."""
        return [g for bus in self.buses for g in getattr(bus, 'generators', [])]

    def get_all_loads(self) -> List:
        """Retorna todas as cargas conectadas às barras do sistema."""
        return [l for bus in self.buses for l in getattr(bus, 'loads', [])]

    def get_all_shunts(self) -> List:
        """Retorna todos os elementos shunt conectados às barras do sistema."""
        return [s for bus in self.buses for s in getattr(bus, 'shunts', [])]

    def add_bus(self, bus: "Bus"):
        """Adiciona uma barra ao sistema, se ainda não estiver presente."""
        if bus not in self.buses:
            self.buses.append(bus)

    def add_line(self, line: "Line"):
        """Adiciona uma linha de transmissão ao sistema."""
        self.lines.append(line)

    def add_transformer(self, transformer: "Transformer"):
        """Adiciona um transformador ao sistema."""
        self.transformers.append(transformer)

    def filtrar_por_periodo(self, t: int):
        """
        Aplica filtros de período sobre todos os elementos (geradores, cargas etc.)
        das barras do sistema, conforme o período `t`.

        Args:
            t (int): Período a ser filtrado.
        """
        for bus in self.buses:
            # Filtrar cargas com perfil horário
            for load in bus.loads:
                if hasattr(load, "profile") and isinstance(load.profile, dict):
                    if t in load.profile:
                        load.demand_p = load.profile[t][0]  # (valor, peso)
                    else:
                        load.demand_p = 0.0

            # Filtrar geradores com perfil (se houver)
            for g in bus.generators:
                if hasattr(g, "profile") and isinstance(g.profile, dict):
                    if t in g.profile:
                        g.gmax = g.profile[t]
                    else:
                        g.gmax = 0.0
