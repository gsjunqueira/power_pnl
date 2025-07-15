"""
Módulo `gas_generator`

Define a classe `GasGenerator`, que representa um gerador térmico a gás natural.
Herdeiro de `ThermalGenerator`, define o tipo de combustível como "gas".

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from electric_models.generation import ThermalGenerator

@dataclass(kw_only=True)
class GasGenerator(ThermalGenerator):
    """
    Gerador térmico movido a gás natural.

    Herda todos os atributos de `ThermalGenerator`. O campo `comb` é automaticamente
    definido como `"gas"` para indicar o tipo de combustível.

    Aplicações:
        - Despacho térmico com baixa emissão de CO₂.
        - Análise de confiabilidade em sistemas com geração distribuída.
        - Modelagem de transição energética com térmicas flexíveis.
    """

    def __post_init__(self):
        """
        Inicializa o gerador com tipo de combustível 'gas'
        e executa validações e associações padrão.

        - Define `comb = "gas"`.
        - Registra o gerador na barra elétrica.
        """
        self.comb = "gas"
        super().__post_init__()
