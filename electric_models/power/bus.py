"""
Módulo `bus`

Define a classe `Bus`, que representa uma barra elétrica no sistema de potência.
Cada barra pode estar conectada a múltiplos geradores, cargas, shunts e déficits.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List
from electric_models import ReliabilityMixin

if TYPE_CHECKING:
    from electric_models.generation import BaseGenerator
    from electric_models.electric_elements import ShuntElement
    from electric_models.power import Load, Deficit

@dataclass(kw_only=True)
class Bus(ReliabilityMixin):
    """
    Representa uma barra do sistema de potência.

    Atributos:
        id (str): Identificador da barra.
        name (str): Nome descritivo da barra.
        v (float): Tensão em pu.
        theta (float): Ângulo de fase em rad.
        type (str): Tipo da barra (PQ, PV, Slack).
        generators (List): Lista de geradores conectados.
        loads (List): Lista de cargas conectadas.
        shunts (List): Lista de dispositivos shunt conectados.
        deficits (List[Deficit]): Lista de variáveis de déficit associadas.
    """
    id: str
    name: str = ""
    v: float = 1.0
    theta: float = 0.0
    type: str = "PQ"
    generators: List["BaseGenerator"] = field(default_factory=list)
    loads: List["Load"] = field(default_factory=list)
    shunts: List["ShuntElement"] = field(default_factory=list)
    deficits: List["Deficit"] = field(default_factory=list)
    status: bool = True

    def add_generator(self, generator: "BaseGenerator"):
        """Adiciona um gerador à barra."""
        self.generators.append(generator)

    def add_load(self, load: "Load"):
        """Adiciona uma carga à barra."""
        self.loads.append(load)

    def add_shunt(self, shunt: "ShuntElement"):
        """Adiciona um elemento shunt à barra."""
        self.shunts.append(shunt)

    def add_deficit(self, deficit: "Deficit"):
        """Adiciona uma variável de déficit (load shedding) à barra."""
        self.deficits.append(deficit)

    def __repr__(self):
        """Representação resumida da barra."""
        return f"<Bus id={self.id} type={self.type} V={self.v:.2f} ∠{self.theta:.2f} rad>"

    def __post_init__(self):
        """Valida os dados mínimos da barra após inicialização."""
        if not self.id:
            raise ValueError("Cada barra deve ter um identificador único (id).")
        if self.v <= 0:
            raise ValueError(f"[{self.id}] Tensão v deve ser positiva (atualmente {self.v}).")
        self.compute_reliability()

    def to_dict(self) -> dict:
        """
        Converte a barra para um dicionário de atributos básicos (exclui listas de elementos).

        Returns:
            dict: Representação simples da barra.
        """
        return {
            "id": self.id,
            "name": self.name,
            "v": self.v,
            "theta": self.theta,
            "type": self.type
        }
