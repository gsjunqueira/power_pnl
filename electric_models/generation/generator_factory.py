"""
Módulo `generator_factory`

Fábrica de geradores que infere o tipo com base nos dados disponíveis.

Esta função permite importar dados genéricos e cria automaticamente
o tipo de gerador mais apropriado com base em seus atributos conhecidos.

Regras de inferência:
- Se possui qualquer um entre 'volume_min', 'volume_max', 'productivity' → HydroGenerator
- Se possui 'power_curve' → WindGenerator
- Se possui 'fictitious' ou custo muito alto → FictitiousGenerator
- Caso contrário → ThermalGenerator (padrão)

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from electric_models.generation.thermal import (
    BiomassGenerator, CoalGenerator, DieselGenerator, GasGenerator,
    NuclearGenerator, OilGenerator, CombinedGenerator)
from .hydro_generator import HydroGenerator
from .thermal_generator import ThermalGenerator
from .wind_generator import WindGenerator
# from .solar_generator import SolarGenerator
from .fictitious_generator import FictitiousGenerator
from .base_generator import BaseGenerator

def create_generator(data: dict) -> BaseGenerator:
    """
    Cria e retorna uma instância de gerador com base nos campos do dicionário.

    Regras de inferência:
    - Usa o campo 'comb' e 'ciclo' para selecionar subtipos de ThermalGenerator.
    - Fallback: ThermalGenerator se não especificado.

    Args:
        data (dict): Dicionário de parâmetros do gerador.

    Returns:
        BaseGenerator: Instância do tipo de gerador correspondente.
    """
    if not isinstance(data, dict):
        raise TypeError("Esperado um dicionário de parâmetros para o gerador.")

    comb = data.get("comb")
    ciclo = data.get("ciclo")

    # Regras de inferência por tipo
    if type=="hydro" or any(k in data for k in ("volume_min", "volume_max", "productivity",
                                                "plant")):
        instance = HydroGenerator(**data)
    elif type=="wind" or "power_curve" in data:
        instance = WindGenerator(**data)
    # elif "solar_curve" in data:
    #     generator = SolarGenerator(**data)
    elif data.get("fictitious", False) or data.get("cost", 0) > 1e5:
        instance = FictitiousGenerator(**data)
    elif comb:
        if ciclo == "combinado":
            return CombinedGenerator(**data)
        match comb.lower():
            case "coal":
                data = dict(data)
                comb = data.pop("comb", None)
                return CoalGenerator(**data)
            case "diesel":
                data = dict(data)
                comb = data.pop("comb", None)
                return DieselGenerator(**data)
            case "gas":
                data = dict(data)
                comb = data.pop("comb", None)
                return GasGenerator(**data)
            case "oil":
                data = dict(data)
                comb = data.pop("comb", None)
                return OilGenerator(**data)
            case "nuclear":
                data = dict(data)
                comb = data.pop("comb", None)
                return NuclearGenerator(**data)
            case "biomass":
                data = dict(data)
                comb = data.pop("comb", None)
                return BiomassGenerator(**data)
        return ThermalGenerator(**data)
    else:
        instance = ThermalGenerator(**data)

    # Verificação de robustez
    if not isinstance(instance, BaseGenerator):
        raise RuntimeError("Tipo de gerador não reconhecido ou instância inválida.")

    return instance
