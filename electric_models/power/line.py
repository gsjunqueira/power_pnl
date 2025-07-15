"""
Módulo `line`

Define a classe `Line`, que representa uma linha de transmissão entre duas barras no
sistema elétrico. Contém atributos elétricos como condutância, susceptância e capacidade
máxima de transporte, essenciais para o cálculo de perdas e fluxo de potência.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# pylint: disable=too-few-public-methods, too-many-arguments

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional
from electric_models import ReliabilityMixin
from electric_models.electric_elements import SeriesElement

if TYPE_CHECKING:
    from .bus import Bus

@dataclass(kw_only=True)
class Line(ReliabilityMixin):
    """
    Representa uma linha de transmissão no sistema elétrico.

    Atributos:
        id (str): Identificador único da linha.
        from_bus (Bus): Barra de origem.
        to_bus (Bus): Barra de destino.
        r (float): Resistência série (pu). Se não fornecida, será calculada a partir da condutância.
        x (float): Reatância série (pu). Se não fornecida, será calculada a partir da suceptância.
        b (float): Admitância shunt total (pu), usada para modelar carga distribuída. Default = 0.0.
        pmax (float): Capacidade máxima de fluxo ativo (MW ou pu). Default = 9999.
        condutancia (float): Condutância série (pu). Pode ser usada como alternativa a `r`.
        suceptancia (float): Suceptância série (pu). Pode ser usada como alternativa a `x`.
        status (bool): Indica se a linha está ativa (True) ou desligada (False).
        series_elements (List[SeriesElement]): Lista de elementos série adicionais como reatores ou
        capacitores.

    Notas:
        - Se `r` e `x` forem fornecidos, a condutância e suceptância são calculadas automaticamente.
        - Se `condutancia` e `suceptancia` forem fornecidas em vez de `r` e `x`, estes serão
        calculados internamente.
        - Pelo menos um par entre `(r, x)` ou `(condutancia, suceptancia)` deve ser definido.
    """
    id: str
    from_bus: "Bus"
    to_bus: "Bus"
    r: Optional[float] = None
    x: Optional[float] = None
    condutancia: Optional[float] = None
    suceptancia: Optional[float] = None
    b: float = 0.0
    pmax: float = 9999.
    status: bool = True
    series_elements: List[SeriesElement] = field(default_factory=list)

    def add_series_element(self, element: SeriesElement):
        """
        Adiciona um capacitor ou reator série à linha.

        Args:
            element (SeriesElement): Instância de capacitor ou reator.
        """
        self.series_elements.append(element)

    def is_operational(self) -> bool:
        """Indica se a linha está ativa no sistema."""
        return self.status

    def get_total_reactance(self) -> float:
        """
        Retorna a reatância total da linha considerando elementos série.

        Returns:
            float: Soma de x da linha e dos elementos série (pu).
        """
        return self.x + sum(e.get_reactance() for e in self.series_elements)

    def __post_init__(self):
        """
        Valida os atributos iniciais após a criação da instância.

        Raises:
            ValueError: Se a reatância ou resistência forem não positivas.
        """
        if self.r is None or self.x is None:
            if self.condutancia is not None and self.suceptancia is not None:
                denom = self.condutancia**2 + self.suceptancia**2
                self.r = self.condutancia / denom
                self.x = -self.suceptancia / denom
            else:
                raise ValueError(
                    f"[{self.id}] É necessário fornecer (r, x) ou (condutancia, suceptancia)."
                )
        else:
            if self.r < 0:
                raise ValueError(f"[{self.id}] A resistência da linha deve ser não negativa.")
            if self.x <= 0:
                raise ValueError(f"[{self.id}] A reatância da linha deve ser positiva.")
            # Converte r, x para condutância e suceptância
            denom = self.r**2 + self.x**2
            self.condutancia = self.r / denom
            self.suceptancia = -self.x / denom

        if self.from_bus == self.to_bus:
            raise ValueError(
                f"[{self.id}] A linha não pode conectar a mesma barra nas duas extremidades.")
        self.compute_reliability()

    def __repr__(self):
        """
        Representação resumida da linha para depuração.

        Returns:
            str: String no formato "<Line id=... buses=...→...>".
        """
        return f"<Line id={self.id} buses={self.from_bus.id}→{self.to_bus.id}>"

    def to_dict(self) -> dict:
        """
        Converte os principais atributos da linha em um dicionário.

        Returns:
            dict: Atributos exportáveis da linha.
        """
        return {
            "id": self.id,
            "from_bus": self.from_bus.id,
            "to_bus": self.to_bus.id,
            "r": self.r,
            "x": self.x,
            "b": self.b,
            "status": self.status,
            "condutancia": self.condutancia,
            "suceptancia": self.suceptancia
        }
