"""
Módulo `biomass_generator`

Define a classe `BiomassGenerator`, que representa uma unidade térmica movida a biomassa.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from electric_models.generation import ThermalGenerator

@dataclass(kw_only=True)
class BiomassGenerator(ThermalGenerator):
    """
    Gerador térmico do tipo biomassa.

    Herda todos os atributos de `ThermalGenerator`. O campo `comb` é automaticamente
    definido como `"biomass"` para indicar o tipo de combustível utilizado.

    Aplicações:
        - Análises de emissões com biocombustíveis.
        - Modelagem de fontes renováveis despacháveis.
        - Estudos de confiabilidade com matriz diversificada.
    """

    def __post_init__(self):
        """
        Inicializa o gerador com tipo de combustível 'biomass'
        e executa validações e associações padrão.

        - Define `comb = "biomass"`.
        - Registra o gerador na barra elétrica.
        """
        self.comb = "biomass"
        super().__post_init__()
