"""
Módulo `thermal_generator`

Define a classe `ThermalGenerator`, derivada de `BaseGenerator`, para representar usinas
termoelétricas. Inclui parâmetros técnicos e econômicos para estudos de despacho
com rampas, custos de partida e restrições temporais.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from typing import Optional
from .base_generator import BaseGenerator

@dataclass(kw_only=True)
class ThermalGenerator(BaseGenerator):
    """
    Representa um gerador térmico com suporte a múltiplas aplicações:
    - Fluxo de potência AC/DC
    - Despacho econômico
    - Restrições operacionais (rampas, tempo mínimo)
    - Emissões e confiabilidade

    Atributos adicionais:
        a (Optional[float]): Coeficiente constante da função de custo.
        b (Optional[float]): Coeficiente linear da função de custo.
        c (Optional[float]): Coeficiente quadrático da função de custo.
        ramp_up (Optional[float]): Rampa de subida (MW/h).
        ramp_down (Optional[float]): Rampa de descida (MW/h).
        emission (Optional[float]): Emissão de CO₂ (tCO₂/MWh gerado).
        mtu (Optional[int]): Tempo mínimo ligado (h).
        mtd (Optional[int]): Tempo mínimo desligado (h).
        hot_cost (Optional[float]): Custo de partida a quente (R$).
        cold_cost (Optional[float]): Custo de partida a frio (R$).
        htc (Optional[int]): Tempo para considerar a máquina "quente" (h).
    """

    type: str = "thermal"

    # Função de custo (para despacho)
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None

    # Restrições dinâmicas
    ramp_up: Optional[float] = None
    ramp_down: Optional[float] = None

    # Emissões ambientais
    emission: Optional[float] = None

    # Regras operacionais
    mtu: Optional[int] = None
    mtd: Optional[int] = None
    hot_cost: Optional[float] = None
    cold_cost: Optional[float] = None
    htc: Optional[int] = None

    # Ciclo térmico
    ciclo: Optional[str] = "simple"

    def get_power_output(self, period: int) -> float:
        """
        Retorna a potência ativa gerada no período informado.

        Args:
            period (int): Índice do período (inteiro).

        Returns:
            float: Valor de `pg` se definido, senão 0.0.
        """
        return self.pg if self.pg is not None else 0.0

    def get_cost(self) -> Optional[float]:
        """
        Calcula o custo instantâneo de geração baseado na função quadrática.

        Returns:
            Optional[float]: Valor do custo total (R$), ou None se parâmetros ausentes.
        """
        if self.a is None or self.b is None or self.c is None:
            return None
        pg = self.pg or 0.0
        return self.c * pg**2 + self.b * pg + self.a

    def get_emission(self) -> Optional[float]:
        """
        Calcula a emissão instantânea de CO₂ em tCO₂/hora.

        Returns:
            Optional[float]: Emissão total no instante atual.
        """
        return (self.pg or 0.0) * self.emission if self.emission is not None else None

    def __post_init__(self):
        """
        Realiza a validação automática do gerador térmico após a criação
        e registra o gerador na barra associada.

        Raises:
            ValueError: Se qualquer parâmetro contínuo for negativo.
        """
        super().__post_init__()
        self.bus.add_generator(self)

        # Verificação contínua
        for campo, valor in {
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "ramp_up": self.ramp_up,
            "ramp_down": self.ramp_down,
            "emission": self.emission,
            "hot_cost": self.hot_cost,
            "cold_cost": self.cold_cost,
        }.items():
            if valor is not None and valor < 0:
                raise ValueError(f"[{self.id}] '{campo}' deve ser ≥ 0.")

        for campo, valor in {
            "mtu": self.mtu,
            "mtd": self.mtd,
            "htc": self.htc,
        }.items():
            if valor is not None and valor < 0:
                raise ValueError(f"[{self.id}] '{campo}' deve ser um inteiro ≥ 0.")

        if self.ciclo not in (None, "simple", "combined"):
            raise ValueError(f"[{self.id}] ciclo deve ser 'simple' ou 'combined'.")


    def __repr__(self):
        """
        Retorna uma representação resumida do gerador térmico.

        Returns:
            str: String no formato "<ThermalGenerator id=... bus=... ciclo=...>".
        """
        return f"<ThermalGenerator id={self.id} bus={self.bus.id} ciclo={self.ciclo}>"
