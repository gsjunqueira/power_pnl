"""
Módulo `dual_transformer`

Define a classe `DualTransformer`, que representa a decomposição de um transformador
com controle simultâneo de tap (tensão) e defasagem angular (fase) em dois
transformadores equivalentes separados.

Aplicações:
    - Fluxo de potência AC com análise de sensibilidade.
    - Modelos linearizados (PTDF, FPO).
    - Estudo de impacto individual de TAP e phase-shift.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .tap_transformer import TapTransformer
from .phase_transformer import PhaseTransformer


class DualTransformer:
    """
    Representa um transformador com controle simultâneo de tap e defasagem angular.

    A composição é feita por:
    - `tap_part`: transformador com apenas TAP.
    - `phase_part`: transformador com apenas defasagem angular (fase).

    Atributos:
        id (str): Identificador original do transformador composto.
        status (bool): Indica se o transformador está ativo.
        tap_part (TapTransformer): Parte com controle de tap (phase = 0).
        phase_part (PhaseTransformer): Parte com defasagem angular (tap = 1).
    """

    def __init__(self, data: dict):
        """
        Inicializa o `DualTransformer`, dividindo o controle de TAP e FASE.

        Args:
            data (dict): Dicionário com os campos típicos de transformador.
                         Deve conter 'id', 'tap', 'phase', 'r', 'x', 'from_bus', 'to_bus'.

        Raises:
            KeyError: Se algum campo essencial estiver ausente.
        """
        required_fields = {"id", "tap", "phase", "r", "x", "from_bus", "to_bus"}
        missing = required_fields - set(data)
        if missing:
            raise KeyError(f"Campos ausentes para DualTransformer: {missing}")

        self.id = data["id"]
        self.status = data.get("status", True)

        # Cria as partes, forçando apenas o parâmetro relevante em cada
        self.tap_part = TapTransformer(**{**data, "phase": 0.0, "status": self.status})
        self.phase_part = PhaseTransformer(**{**data, "tap": 1.0, "status": self.status})

    def get_parts(self):
        """Retorna as partes componentes do transformador dual."""
        return self.tap_part, self.phase_part

    def to_dict(self) -> dict:
        """
        Converte os atributos principais do DualTransformer em um dicionário.

        Útil para registro, exportação de parâmetros ou inspeção automática
        durante simulações.

        Returns:
            dict: Dicionário contendo os principais campos de identificação e
                configuração do transformador composto.
        """
        return {
            "id": self.id,
            "status": self.status,
            "tap": self.tap_part.tap,
            "phase": self.phase_part.phase,
            "r": self.tap_part.r,
            "x": self.tap_part.x,
            "from_bus": self.tap_part.from_bus.id,
            "to_bus": self.tap_part.to_bus.id,
        }

    def __repr__(self):
        """Representação compacta do DualTransformer."""
        return f"<DualTransformer id={self.id} tap={self.tap_part.tap} phase={self.phase_part.phase} status={self.status}>"
