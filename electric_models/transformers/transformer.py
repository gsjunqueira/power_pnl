"""
Módulo `transformer`

Define a classe `Transformer`, representando um transformador genérico entre duas barras
elétricas, com suporte a impedância, tap e defasagem angular.

Compatível com fluxo de potência AC, fluxo ótimo (FPO), e análise de estabilidade.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from typing import TYPE_CHECKING
import math
from electric_models import ReliabilityMixin

if TYPE_CHECKING:
    from electric_models.power import Bus

@dataclass(kw_only=True)
class Transformer(ReliabilityMixin):
    """
    Representa um transformador entre duas barras.

    Atributos:
        id (str): Identificador único do transformador.
        from_bus (Bus): Barra de origem (lado primário).
        to_bus (Bus): Barra de destino (lado secundário).
        r (float): Resistência série (pu).
        x (float): Reatância série (pu).
        b (float): Admitância shunt total (pu). Default = 0.0.
        tap (float): Relação de transformação (tap ratio). Default = 1.0.
        phase (float): Defasagem angular (graus). Default = 0.0.
        status (bool): Indica se o transformador está em operação.
    """

    id: str
    from_bus: "Bus"
    to_bus: "Bus"
    r: float
    x: float
    b: float = 0.0
    tap: float = 1.0
    phase: float = 0.0
    pmax: float = 0.0
    status: bool = True

    def is_operational(self) -> bool:
        """
        Indica se o transformador está em operação.

        Returns:
            bool: True se o transformador está ativo.
        """
        return self.status

    def get_series_impedance(self) -> complex:
        """
        Retorna a impedância série do transformador (pu).

        Returns:
            complex: Impedância Z = R + jX.
        """
        return complex(self.r, self.x)

    def get_tap_ratio(self) -> complex:
        """
        Retorna o tap como um número complexo, considerando ângulo de fase.

        Returns:
            complex: Tap complexo a∠θ (tap * exp(jθ)).
        """
        theta_rad = math.radians(self.phase)
        return self.tap * complex(math.cos(theta_rad), math.sin(theta_rad))

    def __post_init__(self):
        """
        Valida os atributos e verifica consistência física.

        Raises:
            ValueError: Se valores forem inconsistentes ou fisicamente inválidos.
        """
        if self.r < 0 or self.x <= 0:
            raise ValueError(f"[{self.id}] Impedância inválida: r ≥ 0, x > 0.")

        if self.tap <= 0:
            raise ValueError(f"[{self.id}] Tap deve ser positivo.")

        if not 0.0 <= self.phase <= 360.0:
            raise ValueError(f"[{self.id}] Phase deve estar entre 0 e 360 graus.")

        if self.from_bus == self.to_bus:
            raise ValueError(f"[{self.id}] As barras de origem e destino não podem ser iguais.")
        self.compute_reliability()

    def __repr__(self):
        """
        Representação textual resumida do transformador.

        Returns:
            str: String no formato "<Transformer id=... from=... to=...>".
        """
        return f"<Transformer id={self.id} from={self.from_bus.id} to={self.to_bus.id}>"
