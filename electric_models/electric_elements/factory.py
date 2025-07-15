"""
Módulo `factory`

Funções de fábrica para criação automática de dispositivos reativos (shunt ou série)
com base no valor da susceptância ou reatância informada.

- CapacitorShunt ou ReactorShunt são instanciados com base no sinal de `b`.
- CapacitorSeries ou ReactorSeries são instanciados com base no sinal de `x`.

Compatível com modelagem de fluxo de potência, planejamento e estabilidade.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from typing import TYPE_CHECKING
from .capacitor import CapacitorShunt, CapacitorSeries
from .reactor import ReactorShunt, ReactorSeries
from .interfaces import ShuntElement, SeriesElement

if TYPE_CHECKING:
    from electric_models.power import Bus, Line

def create_shunt(id_: str, bus: "Bus", b: float, status: bool = True) -> ShuntElement:
    """
    Cria dinamicamente um dispositivo shunt (reativo) com base no sinal de b.

    Args:
        id_ (str): Identificador único do elemento.
        bus (Bus): Barra elétrica associada.
        b (float): Susceptância em pu (positiva = capacitor, negativa = reator).
        status (bool): True se o elemento está ativo.

    Returns:
        ShuntElement: Instância de CapacitorShunt ou ReactorShunt.

    Raises:
        ValueError: Se b == 0 (sem significado físico).
    """
    if b > 0:
        return CapacitorShunt(id=id_, bus=bus, b=b, status=status)
    elif b < 0:
        return ReactorShunt(id=id_, bus=bus, b=b, status=status)
    else:
        raise ValueError(f"[{id_}] Susceptância nula não define capacitor nem reator.")


def create_series(id_: str, line: "Line", x: float, status: bool = True) -> SeriesElement:
    """
    Cria dinamicamente um dispositivo série (reatância) com base no sinal de x.

    Args:
        id_ (str): Identificador único do elemento.
        line (Line): Linha de transmissão onde está conectado.
        x (float): Reatância em pu ou ohms (negativa = capacitor, positiva = reator).
        status (bool): True se o elemento está ativo.

    Returns:
        SeriesElement: Instância de CapacitorSeries ou ReactorSeries.

    Raises:
        ValueError: Se x == 0 (sem significado físico).
    """
    if x < 0:
        return CapacitorSeries(id=id_, line=line, x=x, status=status)
    elif x > 0:
        return ReactorSeries(id=id_, line=line, x=x, status=status)
    else:
        raise ValueError(f"[{id_}] Reatância nula não define capacitor nem reator.")
