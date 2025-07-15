"""
Módulo `coal_generator`

Define a classe `CoalGenerator`, representando uma unidade termoelétrica movida a carvão mineral.
Herdada de `ThermalGenerator`, esta classe diferencia o tipo de combustível por meio do campo
`comb`.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from electric_models.generation import ThermalGenerator


@dataclass(kw_only=True)
class CoalGenerator(ThermalGenerator):
    """
    Representa um gerador térmico movido a carvão mineral.

    Herda todos os atributos de `ThermalGenerator`. O campo `comb` é automaticamente
    definido como `"coal"` para indicar o tipo de combustível utilizado.

    Aplicações:
        - Despacho térmico com discriminação por tipo de combustível.
        - Estudo de emissões atmosféricas e confiabilidade operacional.
    """

    def __post_init__(self):
        """
        Inicializa o gerador com tipo de combustível fixado como 'coal'
        e executa os procedimentos padrão de validação e associação.

        - Define `comb = "coal"`.
        - Registra o gerador na barra elétrica associada.
        """
        self.comb = "coal"
        super().__post_init__()
