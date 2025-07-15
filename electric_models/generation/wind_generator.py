"""
Módulo `wind_generator`.

Este módulo define a classe `WindGenerator`, responsável por modelar unidades de geração eólica
em estudos de operação, planejamento e confiabilidade. O modelo representa a relação entre a
velocidade do vento e a potência elétrica gerada, por meio de uma curva de potência específica.

A classe herda de `BaseGenerator` e associa automaticamente o gerador à barra do sistema ao ser
instanciada.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from typing import Optional
from .base_generator import BaseGenerator

@dataclass(kw_only=True)
class WindGenerator(BaseGenerator):
    """
    Representa um gerador eólico com base em uma curva de potência.

    Atributos:
        power_curve (dict[float, float]): Mapeamento entre velocidade do vento (m/s) e
        potência gerada (MW).
    """
    power_curve: Optional[dict[float, float]] = None
    type: str = "wind"

    def __post_init__(self):
        """
        Executa ações após a criação do objeto, como vincular o gerador à barra.

        Também valida a consistência interna do gerador.
        """
        self.bus.add_generator(self)
        self.validate()

    def get_power_output(self, period: float) -> float:
        """
        Retorna a potência gerada com base na velocidade do vento.

        Args:
            period (float): Velocidade do vento (m/s), usada como índice da curva de potência.

        Returns:
            float: Potência gerada (MW).
        """
        if not self.power_curve:
            return 0.0
        return self.power_curve.get(period, 0.0)

    def validate(self):
        """
        Valida os atributos específicos do gerador eólico, além dos genéricos.

        Raises:
            ValueError: Se a curva de potência não for válida.
        """
        super().validate()

        if self.power_curve is not None:
            if not isinstance(self.power_curve, dict):
                raise ValueError(
                    f"A curva de potência do gerador {self.id} deve ser um dicionário.")
            for v, p in self.power_curve.items():
                if v < 0 or p < 0:
                    raise ValueError(
                        f"Valores inválidos na curva de potência do gerador {self.id}.")

    def __repr__(self):
        """
        Retorna uma representação resumida do gerador eólico.

        Returns:
            str: String no formato "<WindGenerator id=... bus=...>".
        """
        return f"<WindGenerator id={self.id} bus={self.bus.id}>"
