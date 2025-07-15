"""
Módulo `symbolic`

Contém o construtor simbólico `SymbolicBuilder`, responsável por gerar
a formulação simbólica do modelo de fluxo de potência ótimo (FPO) DC,
incluindo variáveis, custo operacional, função objetivo e restrições.

Utiliza objetos do tipo `FullSystem`, com suporte a elementos como
geradores térmicos, linhas, cargas, barras e déficit de potência.

Autor: Giovani Santiago Junqueira
"""

from .model_builder import SymbolicModelBuilder
from .chute_inicial import chute_inicial
from .karush_kuhn_tucker import KKTChecker

__all__ = ["SymbolicModelBuilder", "chute_inicial", "KKTChecker"]
