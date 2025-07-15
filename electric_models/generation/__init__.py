"""
Pacote `generation` — Modelos de unidades geradoras do sistema elétrico.

Este pacote reúne as classes que representam diferentes tipos de geradores, com suporte
a despacho, fluxo de potência, restrições operacionais, emissões e confiabilidade.

Submódulos incluídos:
- BaseGenerator: Classe abstrata comum a todos os geradores.
- ThermalGenerator: Gerador térmico genérico.
- WindGenerator: Gerador eólico baseado em curva de potência.
- HydroGenerator: Gerador hidráulico acoplado a usina.
- FictitiousGenerator: Gerador fictício para modelagem de déficit.


Subclasses térmicas específicas (gas, diesel, nuclear etc.)
estão organizadas separadamente.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .base_generator import BaseGenerator
from .thermal_generator import ThermalGenerator
from .wind_generator import WindGenerator
from .fictitious_generator import FictitiousGenerator
from .hydro_generator import HydroGenerator
from .generator_factory import create_generator

__all__ = [
    "BaseGenerator", "ThermalGenerator", "WindGenerator",
    "FictitiousGenerator", "HydroGenerator", "create_generator"
]
