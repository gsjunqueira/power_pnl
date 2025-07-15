"""
Módulo `oil_generator`

Define a classe `OilGenerator`, especializada em representar usinas térmicas a óleo
combustível pesado (BPF). Estende `ThermalGenerator` fixando `comb = "oil"` para
diferenciar o tipo de combustível utilizado.

Observação:
    O termo "oil" refere-se aqui ao óleo combustível pesado (BPF), amplamente
    utilizado em grandes termelétricas a vapor ou motores estacionários. Não
    se trata de óleo Diesel automotivo, que seria tratado em outra classe específica.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from electric_models.generation import ThermalGenerator


@dataclass(kw_only=True)
class OilGenerator(ThermalGenerator):
    """
    Gerador térmico movido a óleo combustível pesado (BPF).

    Herda todos os atributos de `ThermalGenerator`, fixando `comb = "oil"`.

    Aplicações:
        - Modelagem de despacho térmico com diferentes combustíveis.
        - Cálculo de emissões, desempenho e custos por tipo de combustível.
    """

    def __post_init__(self):
        """
        Inicializa o gerador com o tipo de combustível 'oil' e registra na barra.

        - Define `comb` como "oil".
        - Realiza a validação padrão da classe base.
        """
        self.comb = "oil"
        super().__post_init__()
