"""
Pacote `generation.thermal`

Subclasses específicas de `ThermalGenerator`, organizadas por tipo de combustível:

- `GasGenerator`
- `DieselGenerator`
- `CoalGenerator`
- `OilGenerator`
- `BiomassGenerator`
- `NuclearGenerator`
- `CombinedCycleGenerator`

Estas classes estendem `ThermalGenerator` com atributos especializados.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .gas_generator import GasGenerator
from .diesel_generator import DieselGenerator
from .coal_generator import CoalGenerator
from .oil_generator import OilGenerator
from .biomass_generator import BiomassGenerator
from .nuclear_generator import NuclearGenerator
from .combined_generator import CombinedGenerator

__all__ = [
    "GasGenerator",
    "DieselGenerator",
    "CoalGenerator",
    "OilGenerator",
    "BiomassGenerator",
    "NuclearGenerator",
    "CombinedGenerator",
]