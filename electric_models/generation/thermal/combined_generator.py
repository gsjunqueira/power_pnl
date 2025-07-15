"""
Módulo `combined_generator`

Define a classe `CombinedGenerator`, que representa uma unidade térmica em ciclo combinado.
Este tipo de usina opera com múltiplos estágios (geração a gás + recuperação de calor).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from electric_models.generation import ThermalGenerator

@dataclass(kw_only=True)
class CombinedGenerator(ThermalGenerator):
    """
    Representa uma usina térmica em ciclo combinado.

    Atributos herdados:
        - Todos de ThermalGenerator (pg, custos, rampas, emissões, etc).

    Comportamento:
        - O atributo `ciclo` é automaticamente definido como "combinado".
        - O tipo de combustível (`comb`) continua indicando gás, óleo, etc.

    Aplicações:
        - Modelagem de térmicas mais eficientes.
        - Despacho com separação por tecnologia.
    """

    def __post_init__(self):
        """
        Inicializa o gerador em ciclo combinado.

        - Define `ciclo` como "combinado".
        - Executa a inicialização da superclasse.
        """
        self.ciclo = "combinado"
        super().__post_init__()
