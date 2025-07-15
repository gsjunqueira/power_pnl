"""
Módulo `diesel_generator`

Define a classe `DieselGenerator`, que representa uma usina termoelétrica a óleo diesel.
Essa classe estende `ThermalGenerator` e fixa o campo `comb` como `"diesel"` para
identificar explicitamente o tipo de combustível utilizado.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from electric_models.generation import ThermalGenerator

@dataclass(kw_only=True)
class DieselGenerator(ThermalGenerator):
    """
    Representa um gerador térmico movido a óleo diesel.

    Herda todos os atributos da classe base `ThermalGenerator`,
    fixando o campo `comb = "diesel"` para permitir diferenciação
    por combustível em modelagens de despacho e emissões.

    Aplicações:
        - Sistemas isolados ou de backup
        - Despacho térmico emergencial
        - Análise de emissões e custo por tipo de combustível
    """

    def __post_init__(self):
        """
        Inicializa o gerador como sendo do tipo diesel, e registra a instância na barra.

        - Define `comb` como 'diesel'.
        - Executa validações e associação à barra via super().__post_init__().
        """
        self.comb = "diesel"
        super().__post_init__()
