"""
Módulo `hydro_plant`

Define a classe `HydroPlant`, que representa uma usina hidrelétrica com reservatório.
Inclui suporte à simulação de operação por períodos, considerando afluências variáveis,
volume mínimo/máximo, vertimentos, volume morto e histórico de volume útil.

Compatível com diferentes portes (CGH, PCH, UHE) e tipos de operação
(com reservatório de acumulação ou a fio d’água).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass, field
from typing import Optional, List, Literal, Dict
from electric_models.generation import HydroGenerator


@dataclass
class HydroPlant:
    """
    Representa uma usina hidrelétrica com reservatório.

    Atributos:
        id (str): Identificador da usina.
        volume_min (float): Volume mínimo de operação (hm³).
        volume_max (float): Volume máximo do reservatório (hm³).
        volume_morto (Optional[float]): Volume abaixo do qual não há geração.
        limite_vazao_turbinada (Optional[float]): Vazão máxima que pode ser turbinada
        no período (hm³).
        afluencias (dict[int, float]): Afluência por período (hm³/período).
        vertimento (Optional[float]): Volume vertido no período (hm³).
        historico_volume (dict[int, float]): Histórico de volume útil por período.
        curva_cota_volume (Optional[dict[float, float]]): Curva cota-volume útil (m x hm³).
        porte (Literal): CGH, PCH, UHE.
        tipo_operacao (Literal): acumulacao ou fio_dagua.
        generators (List[HydroGenerator]): Lista de geradores associados.
    """

    id: str
    volume_min: float
    volume_max: float
    volume_inicial: Optional[float] = None

    volume_morto: Optional[float] = None
    limite_vazao_turbinada: Optional[float] = None

    afluencias: Dict[int, float] = field(default_factory=dict)
    vertimento: Optional[float] = None
    historico_volume: Dict[int, float] = field(default_factory=dict)
    curva_cota_volume: Optional[Dict[float, float]] = None

    porte: Literal["CGH", "PCH", "UHE"] = "UHE"
    tipo_operacao: Literal["acumulacao", "fio_dagua"] = "acumulacao"

    generators: List[HydroGenerator] = field(default_factory=list)

    def add_generator(self, generator: HydroGenerator):
        """Adiciona um gerador hidráulico à usina."""
        self.generators.append(generator)

    def get_total_generation(self, period: int) -> float:
        """Retorna a potência total gerada no período (MW)."""
        return sum(g.get_power_output(period) for g in self.generators)

    def get_total_vazao_turbinada(self, period: int) -> float:
        """
        Retorna a vazão total turbinada no período (hm³), respeitando o limite físico, se houver.
        """
        vazao_total = sum(
            g.get_power_output(period) / (
                self.curva_produtividade(self.get_last_volume()) or g.productivity or 1.0
            )
            for g in self.generators if g.productivity and g.productivity > 0
        )

        if self.limite_vazao_turbinada is not None:
            return min(vazao_total, self.limite_vazao_turbinada)
        return vazao_total

    def get_energy_generated(self, period: int) -> float:
        """
        Calcula a energia gerada no período (MWh).

        Returns:
            float: Soma de potência gerada por hora.
        """
        return self.get_total_generation(period)  # Se duração = 1h, MW = MWh

    def curva_produtividade(self, volume: float) -> Optional[float]:
        """
        Estima a produtividade hídrica com base na curva cota-volume.

        Realiza uma interpolação linear entre os pontos mais próximos da curva.

        Args:
            volume (float): Volume atual (hm³).

        Returns:
            Optional[float]: Produtividade estimada (MW/hm³), ou None se não aplicável.
        """
        if not self.curva_cota_volume or volume is None:
            return None

        # Ordena os volumes em ordem crescente
        volumes = sorted(self.curva_cota_volume.keys())

        # Fora do intervalo da curva
        if volume <= volumes[0]:
            return self.curva_cota_volume[volumes[0]]
        if volume >= volumes[-1]:
            return self.curva_cota_volume[volumes[-1]]

        # Interpolação linear entre dois pontos vizinhos
        for i in range(len(volumes) - 1):
            v1, v2 = volumes[i], volumes[i + 1]
            if v1 <= volume <= v2:
                p1 = self.curva_cota_volume[v1]
                p2 = self.curva_cota_volume[v2]
                # Interpolação
                return p1 + (p2 - p1) * (volume - v1) / (v2 - v1)

        return None  # não deveria ocorrer se a curva estiver bem definida

    def update_volume(self, period: int):
        """
        Atualiza o volume útil com base na afluência, geração e limites físicos.

        Args:
            period (int): Índice do período de simulação.
        """
        afluencia = self.afluencias.get(period, 0.0)
        vazao_turbinada = self.get_total_vazao_turbinada(period)
        volume_anterior = self.get_last_volume()
        novo_volume = volume_anterior + afluencia - vazao_turbinada

        if novo_volume > self.volume_max:
            self.vertimento = novo_volume - self.volume_max
        else:
            self.vertimento = 0.0

        self.historico_volume[period] = min(max(novo_volume, self.volume_min), self.volume_max)

    def reset(self):
        """Restaura o volume atual e histórico para o estado inicial."""
        volume_inicial = max(self.volume_min, self.volume_max / 2)
        self.historico_volume.clear()
        self.historico_volume[0] = volume_inicial
        self.vertimento = 0.0

    def __repr__(self):
        """Representação resumida para debug."""
        return f"<HydroPlant id={self.id} porte={self.porte} tipo={self.tipo_operacao}>"

    def __post_init__(self):
        """
        Valida os parâmetros e inicializa estruturas auxiliares.

        Raises:
            ValueError: Se volumes estiverem inconsistentes.
        """
        if self.volume_min > self.volume_max:
            raise ValueError(f"[{self.id}] volume_max deve ser maior ou igual a volume_min")

        if not self.historico_volume:
            # Inicializa com volume médio ou volume mínimo
            vi = self.volume_inicial if self.volume_inicial is not None else max(self.volume_min, self.volume_max / 2)
            self.historico_volume[0] = vi

        if self.volume_morto and self.volume_morto > self.volume_max:
            raise ValueError(
                f"[{self.id}] volume_morto ({self.volume_morto}) não pode ser maior que volume_max ({self.volume_max})"
            )

    def get_last_volume(self) -> float:
        """
        Retorna o último volume conhecido do reservatório.

        Returns:
            float: Último volume útil armazenado.
        """
        if not self.historico_volume:
            raise RuntimeError(f"[{self.id}] Nenhum volume registrado.")
        return self.historico_volume[max(self.historico_volume)]

    def get_volume(self, period: int) -> Optional[float]:
        """
        Retorna o volume registrado para um período específico.

        Returns:
            Optional[float]: Volume (hm³), ou None se não registrado.
        """
        return self.historico_volume.get(period)
