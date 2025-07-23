"""
Módulo `loader`

Responsável por carregar um sistema elétrico completo a partir de um
arquivo JSON, construindo um objeto `FullSystem` com todos os
componentes (barras, linhas, cargas, geradores) devidamente alocados
em suas estruturas.

Todas as leituras, conversões para pu e alocações internas ocorrem
em um único ponto de entrada: `carregar_sistema()`.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# import re
import json
from pathlib import Path
from typing import Optional
from collections import defaultdict
from electric_models.system import FullSystem
from electric_models.power import PowerSystem, Bus, Line, Load, Deficit
from electric_models.hydro import HydroPlant, HydroSystem
from electric_models.generation import create_generator
from electric_models.transformers import create_transformer

class DataLoader:
    """
    Classe para carregar os dados de um sistema elétrico e hidráulico a partir de um arquivo JSON.

    Responsável por instanciar todos os elementos da malha elétrica, geração e hidráulica,
    e montar o objeto `FullSystem` com base no cenário escolhido.
    """

    def __init__(self, json_path: str, case: str = "DGER_1"):
        """
        Inicializa o carregador com o caminho do arquivo JSON e o nome do cenário.

        Args:
            json_path (str): Caminho absoluto ou relativo para o arquivo `.json`.
            case (str): Nome da chave correspondente ao conjunto de geradores. Default: "DGER_1".
        """
        self.path = Path(json_path)
        self.system: Optional[FullSystem] = None
        self.case = case
        self.data = self._load_json()
        self.pb = 100.
        self.barras = []
        self.mapa_barras = {}
        self.hydro_plants = {}
        self.geradores = []
        self.linhas = []
        self.transformadores = []
        self.cargas = []

    def _load_json(self) -> dict:
        """Lê e retorna o conteúdo do arquivo JSON como dicionário."""
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _potencia_base(self):
        """
        Extrai a potência base (PB) a partir da chave 'PB' no JSON, ou define como 100.0 se ausente.

        Atribui o valor extraído ao atributo `self.pb`.
        """
        self.pb = self.data.get("PB", 100.)

    def _carregar_barras(self):
        """Instancia e armazena os objetos `Bus` com base nos dados."""
        self.barras = [Bus(**b) for b in self.data.get("DBAR", [])]
        self.mapa_barras = {b.id: b for b in self.barras}

    def _carregar_usinas_hidraulicas(self):
        """Instancia os objetos `HydroPlant` e armazena no dicionário por ID."""
        self.hydro_plants = {
            p["id"]: HydroPlant(**{**p, "generators": []})
            for p in self.data.get("DHIDR", [])
        }

    def _carregar_geradores(self):
        """Instancia os geradores e associa às barras e plantas (quando hidráulicos)."""
        for g in self.data.get(self.case, []):
            g_data = {**g, "bus": self.mapa_barras[g["bus"]],
                      "gmin": self._pu(g.get("gmin")), "gmax": self._pu(g.get("gmax")),
                      "b": g.get("b")*self.pb, "c": g.get("c")*self.pb**2}
            if g.get("type") == "hydro":
                g_data["plant"] = self.hydro_plants[g["plant"]]
            self.geradores.append(create_generator(g_data))

    def _carregar_transformadores(self):
        """Instancia e armazena os objetos `Transformer` com base nos dados."""
        self.transformadores = [
            create_transformer({
                **t,
                "from_bus": self.mapa_barras[t["from_bus"]],
                "to_bus": self.mapa_barras[t["to_bus"]]
            })
            for t in self.data.get("DTRA", [])
        ]

    def _carregar_linhas(self):
        """Instancia e armazena os objetos `Line` com base nos dados."""
        self.linhas = [
            Line(
                **{
                    **l,
                    "from_bus": self.mapa_barras[l["from_bus"]],
                    "to_bus": self.mapa_barras[l["to_bus"]],
                    "condutancia": self._pu(l.get("condutancia")),
                    "suceptancia": self._pu(l.get("suceptancia")),
                    "pmax": self._pu(l.get("pmax"))
                }
            )
            for l in self.data.get("DLIN", [])
        ]

    def _carregar_cargas(self):
        """
        Instancia e armazena os objetos `Load` com base na chave `DLOAD`.

        Aplica a mesma carga para todos os períodos definidos (atualmente fixado em 1).
        As cargas são associadas às barras correspondentes via `self.mapa_barras`.
        """
        num_periodos = 1
        self.cargas = [
            Load(
                **{
                    **carga,
                    "bus": self.mapa_barras[carga["bus"]],
                    "period": h,
                    "demand_p": self._pu(carga.get("demand_p"))
                }
            )
            for carga in self.data.get("DLOAD", [])
            for h in range(num_periodos)
        ]

    def _carregar_deficits(self, data: dict):
        """
        Carrega os objetos `Deficit` a partir da chave `deficits` no JSON, se presente.

        Caso contrário, cria déficits automaticamente com base na carga total por barra
        e por período, associando o custo padrão de corte.

        Os déficits são adicionados nas respectivas barras, dentro de `barra.deficits`.
        """
        if "deficits" in data:
            for d in data["deficits"]:
                deficit = Deficit(
                    id=d["id"],
                    bus=self.mapa_barras[d["bus"]],
                    period=d["period"],
                    max_deficit=d["limite"],
                    cost=d["custo"]
                )
                self.mapa_barras[d["bus"]].deficits.append(deficit)
        else:
            demanda_por_barra_tempo = defaultdict(float)

            for bus in self.system.power.buses:
                for carga in getattr(bus, "loads", []):
                    demanda_por_barra_tempo[(bus.id, carga.period)] += carga.demand_p

            for (bus_id, t), demanda_total in demanda_por_barra_tempo.items():
                deficit = Deficit(
                    id=f"CUT_{bus_id}_t{t}",
                    bus=self.mapa_barras[bus_id],
                    period=t,
                    max_deficit=demanda_total,
                    cost=1e4 + (abs(hash(f"{bus_id}_{t}")) % 100) # custo fixo padrão
                )

    def _pu(self, valor: Optional[float]) -> Optional[float]:
        """
        Converte um valor absoluto (em MW ou MVAr) para unidade por unidade (pu).

        A conversão utiliza a potência base do sistema (`self.pb`). Caso o valor
        seja None, retorna None sem realizar conversão, permitindo uso seguro em
        campos opcionais.

        Fórmula: valor_pu = valor / potência_base

        Args:
            valor (Optional[float]): Valor numérico em MW/MVAr ou None.

        Returns:
            Optional[float]: Valor convertido para pu ou None se entrada for None.
        """
        return valor / self.pb if valor is not None else None

    def carregar(self) -> FullSystem:
        """
        Constrói e retorna um objeto `FullSystem` com base nos dados lidos.

        Returns:
            FullSystem: Sistema elétrico e hidráulico completo.
        """
        self._potencia_base()
        self._carregar_barras()
        self._carregar_usinas_hidraulicas()
        self._carregar_transformadores()
        self._carregar_linhas()


        power = PowerSystem(
            buses=self.barras,
            lines=self.linhas,
            transformers=self.transformadores,
            pb = self.pb
        )
        hydro = HydroSystem(plants=self.hydro_plants)

        self._carregar_geradores()
        self._carregar_cargas()
        self.system = FullSystem(power=power, hydro=hydro)
        self._carregar_deficits(self.data)

        return self.system
