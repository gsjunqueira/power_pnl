"""
Módulo `full_system`

Módulo que define a classe `FullSystem`, responsável por integrar o sistema elétrico
(`PowerSystem`) com o sistema hidráulico (`HydroSystem`), possibilitando simulações
conjuntas com atualização de estados ao longo do tempo.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from electric_models.power import PowerSystem
from electric_models.hydro import HydroSystem

@dataclass
class FullSystem:
    """
    Sistema completo que une a modelagem elétrica (PowerSystem) e hidráulica (HydroSystem).

    Atributos:
        power (PowerSystem): Sistema elétrico completo.
        hydro (HydroSystem): Sistema hidráulico completo.
    """

    power: PowerSystem
    hydro: HydroSystem
    config: Optional[Dict] = field(default_factory=dict)

    def update(self, period: int):
        """
        Atualiza os volumes hidráulicos e outros estados internos do sistema.

        Args:
            period (int): Índice do período atual da simulação.
        """
        self.hydro.update_all_volumes(period)

    def get_total_generation(self, period: int) -> float:
        """
        Retorna a soma da geração total do sistema (geradores + hidrelétricas).

        Args:
            period (int): Índice do período de simulação.

        Returns:
            float: Geração total no sistema (MW).
        """
        termo_hidro = sum(g.pg or 0.0 for g in self.power.get_all_generators())
        hidro = self.hydro.get_total_generation(period)
        return termo_hidro + hidro

    def __repr__(self):
        """
        Representação compacta do sistema completo para debug.

        Returns:
            str: Descrição resumida dos subsistemas.
        """
        return f"<FullSystem power={len(self.power.buses)} buses, hydro={len(self.hydro.plants)} plants>"

    def set_config(self, config: Dict[str, Any]):
        """
        Atualiza o dicionário de configurações do sistema completo (FullSystem).

        Este método permite registrar parâmetros de configuração que serão utilizados
        em etapas posteriores, como construção de modelos, escolha de solver, ativação
        de funcionalidades (perdas, fluxo, emissão, etc.) e definição de parâmetros como `delta`.

        Args:
            config (Dict[str, Any]): Dicionário contendo as configurações do sistema.
                Exemplo:
                    {
                        "delta": [1],
                        "solver_name": "glpk",
                        "deficit": True,
                        "transporte": False,
                        "fluxo_dc": True,
                        "perdas": False,
                        "rampa": False,
                        "emissao": False
                    }
        """
        self.config.update(config)
