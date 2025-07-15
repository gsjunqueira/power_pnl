"""
Módulo `load`

Define a classe `Load`, que representa uma carga elétrica conectada a uma barra.
Suporta modelagem para diferentes aplicações: fluxo AC/DC, FPO, reserva e confiabilidade.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .bus import Bus

@dataclass(kw_only=True)
class Load:
    """
    Representa uma carga elétrica conectada a uma barra.

    Atributos:
        id (str): Identificador da carga.
        bus (Bus): Instância da barra à qual a carga está conectada.
        demand_p (Optional[float]): Demanda ativa (MW). Obrigatório em DC e confiabilidade.
        demand_q (Optional[float]): Demanda reativa (MVAr). Usado apenas em AC.
        reserva (Optional[float]): Requisito de reserva (MW). Usado em FPO.
        period (int): Índice do período (ex: hora do dia).
    """
    id: str
    bus: "Bus"
    demand_p: Optional[float] = None
    demand_q: Optional[float] = None
    reserva: Optional[float] = None
    period: int = 0
    status: bool = True

    def __post_init__(self):
        """
        Valida os campos (se definidos) e associa a carga à barra correspondente.
        """
        if self.demand_p is not None and self.demand_p < 0:
            raise ValueError(f"[{self.id}] Demanda ativa (demand_p) não pode ser negativa.")
        if self.demand_q is not None and self.demand_q < 0:
            raise ValueError(f"[{self.id}] Demanda reativa (demand_q) não pode ser negativa.")
        if self.reserva is not None and self.reserva < 0:
            raise ValueError(f"[{self.id}] Reserva (reserva) não pode ser negativa.")

        self.bus.add_load(self)

    def __repr__(self):
        """
        Representação compacta da carga para fins de debug.
        """
        return (
            f"<Load id={self.id} bus={self.bus.id} P={self.demand_p or 0.0} "
            f"Q={self.demand_q or 0.0} R={self.reserva or 0.0} t={self.period}>"
        )

    def to_dict(self) -> dict:
        """
        Converte os dados da carga para dicionário.

        Returns:
            dict: Dicionário com os campos principais da carga.
        """
        return {
            "id": self.id,
            "bus": self.bus.id,
            "demand_p": self.demand_p,
            "demand_q": self.demand_q,
            "reserva": self.reserva,
            "period": self.period,
        }
