"""
Módulo `nuclear_generator`

Define a classe `NuclearGenerator`, especializada para modelar usinas térmicas
movidas a combustível nuclear. Estende `ThermalGenerator` com restrições
operacionais características desse tipo de usina.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from electric_models.generation import ThermalGenerator

@dataclass(kw_only=True)
class NuclearGenerator(ThermalGenerator):
    """
    Representa um gerador térmico do tipo nuclear.

    Atributos herdados de `ThermalGenerator`.

    Comportamento adicional:
        - Define automaticamente `comb = "nuclear"`.
        - Se `mtu` (mínimo tempo ligado) não for fornecido, assume um valor alto padrão.
    
    Aplicações:
        - Despacho térmico com rigidez de operação.
        - Simulações de confiabilidade (alta disponibilidade).
        - Avaliações de planejamento de longo prazo com base base.
    """

    def __post_init__(self):
        """
        Inicializa o gerador nuclear com tipo de combustível e restrições típicas.

        - Define `comb` como "nuclear".
        - Define `mtu` como 720 horas (caso não informado), refletindo operação base-load.
        - Define `mtd` como 0, pois usinas nucleares raramente desligam.
        - Remove parâmetros de custo de partida e tempo quente, pois não se aplicam.
        - Registra o gerador na barra elétrica.
        """
        self.comb = "nuclear"
        if self.mtu is None:
            self.mtu = 720  # Ex: 30 dias
        if self.mtd is None:
            self.mtd = 0
        self.hot_cost = None
        self.cold_cost = None
        self.htc = None
        super().__post_init__()
