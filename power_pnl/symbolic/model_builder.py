"""
Módulo `model_builder`

Contém a classe `SymbolicModelBuilder`, responsável pela construção simbólica
do modelo de otimização de sistemas elétricos, incluindo definição das
variáveis simbólicas, cálculo do custo operacional, função objetivo e
restrições do modelo.

Esta estrutura é compatível com formulações simbólicas para análise
de fluxo de potência ótimo (FPO) em corrente contínua com suporte a
déficit de carga, limites angulares, fluxo de potência e geração.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import sympy as sp
from sympy import Eq, Le, Ge
from electric_models.system import FullSystem
from power_pnl.models import ConstantSet

class SymbolicModelBuilder:
    """
    Classe responsável pela construção simbólica do modelo de otimização.

    Métodos públicos:
        - __init__: Inicializa a classe com o sistema elétrico e define as variáveis.
        - variaveis: Gera as variáveis simbólicas para geradores, linhas, barras e déficits.
        - custo_operacional: Retorna o custo marginal de operação como expressão simbólica.
        - funcao_objetivo: Retorna a FOB como a integral indefinida do custo marginal.
        - restricoes: Agrega todas as restrições do modelo em uma única lista.
    """

    def __init__(self, full_system: FullSystem, slack_id: str = None, barra_unica: bool = False,
                 tipo: str ="cubica", method: str = "newton"):
        """
        Inicializa o construtor simbólico do modelo, criando as variáveis.

        Args:
            full_system (FullSystem): Sistema elétrico completo.
        """
        self.full_system = full_system
        if slack_id is None:
            slack_id = self.full_system.power.buses[0].id
        self.slack_id = slack_id
        self.slack_var = f"theta_{self.slack_id}"
        self.variables = self.variaveis()
        self._modo_barra_unica = barra_unica
        self.tipo = tipo
        self.method = method
        self.constants = ConstantSet(include_mi = method == "interior-point")

    def variaveis(self) -> dict[str, sp.Symbol]:
        """
        Cria variáveis simbólicas para geradores, linhas, ângulos de fase e déficit.

        Returns:
            dict[str, sp.Symbol]: Dicionário com as variáveis simbólicas por nome.
        """
        self.variables = {}

        for bus in self.full_system.power.buses:
            # Variáveis de ângulo de fase por barra
            if bus.id != self.slack_id:
                self.variables[f"theta_{bus.id}"] = sp.Symbol(f"theta_{bus.id}")

            # Variáveis de geração por gerador
            for g in getattr(bus, "generators", []):
                self.variables[f"P_{g.id}"] = sp.Symbol(f"P_{g.id}")

        return self.variables

    def restricoes(self) -> list[sp.Expr]:
        """
        Retorna todas as restrições simbólicas do modelo, agregadas em uma única lista.

        Returns:
            list[sp.Expr]: Lista achatada de todas as restrições simbólicas.
        """
        restricoes = []
        restricoes += self._limite_geracao()
        if not self._modo_barra_unica:
            restricoes += self._limite_fluxo()
            restricoes += self._balanco_potencia()
            restricoes += self._limite_angulo()
        else:
            restricoes += self._balanco_barra_unica()
        return restricoes

    def custo_operacional(self, solucao: dict) -> float:
        """
        Calcula o custo marginal total de operação.

        Returns:
            sp.Expr: Soma dos custos marginais de todos os geradores.
        """
        custo = 0
        pb = self.full_system.power.pb

        for bus in self.full_system.power.buses:
            for g in getattr(bus, "generators", []):
                nome_var = f"P_{g.id}"
                # p_val = solucao[nome_var] * pb
                p_val = solucao[nome_var]
                custo += self._custo_gerador(g, p_val)
        return custo

    def custo_cubico(self, solucao: dict[sp.Symbol, float]) -> float:
        """
        Calcula o custo marginal total de operação.

        Returns:
            sp.Expr: Soma dos custos marginais de todos os geradores.
        """
        custo_expr = self._custo_cubico()
        subs = {}

        for var in self.variables.values():
            if var in solucao:
                subs[var] = solucao[var] 

        return float(custo_expr.subs(subs).evalf())

    def get_fob(self, solucao: dict[sp.Symbol, float]) -> float:
        """
        Avalia numericamente a função objetivo com base na solução em pu,
        convertendo as potências para MW antes da avaliação.

        Args:
            solucao (dict[sp.Symbol, float]): Dicionário com variáveis
            simbólicas e seus valores em pu.

        Returns:
            float: Valor da FOB com potências em MW.
        """
        pb = self.full_system.power.pb
        fob_expr = self.fob()
        subs = {}

        for var in self.variables.values():
            if var in solucao:
                nome = str(var)
                if nome.startswith("P_"):
                    # subs[var] = solucao[var] * pb
                    subs[var] = solucao[var]
                else:
                    subs[var] = solucao[var]

        return float(fob_expr.subs(subs).evalf())

    def fob(self) -> sp.Expr:
        """
        Calcula a função objetivo como a integral do custo marginal de cada gerador.

        FOB = ∑_g ∫(a_g P^2 + b_g P + c_g) dP = ∑_g (a_g/3 * P^3 + b_g/2 * P^2 + c_g * P)

        Returns:
            sp.Expr: Expressão simbólica da função objetivo (FOB).
        """
        fob = 0

        for bus in self.full_system.power.buses:
            for g in getattr(bus, "generators", []):
                p = self.variables.get(f"P_{g.id}")
                if p is None:
                    raise ValueError(f"Variável de geração P_{g.id} não encontrada.")

                custo_marginal = self._custo_gerador(g, p)
                fob += sp.integrate(custo_marginal, p) if self.tipo == "cubica" else custo_marginal

        return fob

    def _custo_gerador(self, g, p: sp.Symbol) -> sp.Expr:
        """
        Retorna a expressão simbólica do custo marginal de geração de um gerador térmico.

        Custo marginal = a * P² + b * P + c

        Args:
            g: Instância do gerador (deve possuir atributos a, b, c).
            p (sp.Symbol): Variável simbólica da potência ativa do gerador.

        Returns:
            sp.Expr: Expressão simbólica do custo marginal.
        """
        return g.c * p**2 + g.b * p + g.a

    def _custo_cubico(self) -> sp.Expr:
        """
        Gera a expressão simbólica do custo operacional cúbico de todos os geradores.
        Estilo idêntico ao método fob().
        """

        custo_total = 0

        for bus in self.full_system.power.buses:
            for g in getattr(bus, "generators", []):
                p = self.variables.get(f"P_{g.id}")
                if p is None:
                    raise ValueError(f"Variável de geração P_{g.id} não encontrada.")

                custo_marginal = self._custo_gerador(g, p)
                custo_total += sp.integrate(custo_marginal, p)

        return custo_total


    def _limite_geracao(self) -> list:
        """
        Gera as restrições simbólicas de limite mínimo e máximo de geração ativa
        para cada gerador do sistema, percorrendo as barras.

        Args:
            full_system (FullSystem): Instância do sistema completo com barras e geradores.
            variaveis (dict[str, sp.Symbol]): Dicionário de variáveis simbólicas.

        Returns:
            list: Lista de expressões simbólicas com restrições do tipo Pmin ≤ P ≤ Pmax.
        """
        restricoes = []

        for barra in self.full_system.power.buses:
            if hasattr(barra, "generators"):
                for g in barra.generators:
                    p = self.variables.get(f"P_{g.id}")
                    if p is None:
                        raise ValueError(f"Variável simbólica 'P_{g.id}' não encontrada.")
                    if g.gmin is not None:
                        restricoes.append(Ge(p, g.gmin)) # >=
                    if g.gmax is not None:
                        restricoes.append(Le(p, g.gmax)) # <=
        return restricoes

    def _limite_fluxo(self) -> list:
        """
        Gera as restrições de limite de fluxo para cada linha do sistema,
        substituindo F_linha por B * (theta_from - theta_to).

        Returns:
            list: Lista de desigualdades simbólicas (fluxo ≤ Fmax e fluxo ≥ -Fmax).
        """
        restricoes = []

        for linha in self.full_system.power.lines:
            if linha.x == 0:
                raise ValueError(
                    f"Linha {linha.id} possui reatância zero, não é possível calcular susceptância."
                )

            b = linha.suceptancia  # susceptância

            # Ângulo de from_bus
            if linha.from_bus.id == self.slack_id:
                theta_from = 0
            else:
                theta_from = self.variables[f"theta_{linha.from_bus.id}"]

            # Ângulo de to_bus
            if linha.to_bus.id == self.slack_id:
                theta_to = 0
            else:
                theta_to = self.variables[f"theta_{linha.to_bus.id}"]

            fluxo_expr = b * (theta_from - theta_to)
            fmax_pu = linha.pmax

            restricoes.append(Le(fluxo_expr, fmax_pu))    # fluxo ≤ fmax
            restricoes.append(Ge(fluxo_expr, -fmax_pu))   # fluxo ≥ -fmax

        return restricoes

    def _balanco_potencia(self) -> list[sp.Equality]:
        """
        Gera as equações de balanço de potência para cada barra e período no modelo DC.

        Convenções:
        - Injeções (geração e déficit) têm sinal positivo.
        - Fluxos são modelados como saindo da barra: B*(θ_barra - θ_vizinha).
        - Carga aparece do lado direito da equação.

        Returns:
            list[sp.Equality]: Lista de equações simbólicas do tipo Eq(geração líquida, carga).
        """
        restricoes = []
        periodos = sorted({l.period for b in self.full_system.power.buses
                           for l in getattr(b, "loads", [])})

        for barra in self.full_system.power.buses:
            for t in periodos:
                # Geração na barra (considera geradores sem período específico)
                geracao = sum(
                    self.variables[f"P_{g.id}"]
                    for g in getattr(barra, "generators", [])
                )

                # Carga no período t
                carga = sum(
                    l.demand_p
                    for l in getattr(barra, "loads", [])
                    if l.period == t
                )

                # Déficit no período t
                dvar = self.variables.get(f"D_{barra.id}_t{t}", 0)

                # Soma de fluxos saindo da barra (fluxo = B * (θ_barra - θ_vizinha))
                fluxo_total = 0

                for linha in self.full_system.power.lines:
                    if linha.x == 0:
                        raise ValueError(f"Linha {linha.id} com reatância zero.")

                    b = linha.suceptancia

                    # Ângulos
                    theta_from = (0 if linha.from_bus.id == self.slack_id
                                  else self.variables[f"theta_{linha.from_bus.id}"])
                    theta_to   = (0 if linha.to_bus.id == self.slack_id
                                  else self.variables[f"theta_{linha.to_bus.id}"])

                    if linha.from_bus.id == barra.id:
                        # fluxo saindo da barra: (θ_barra - θ_vizinha)
                        fluxo_total -= b * (theta_from - theta_to)

                    elif linha.to_bus.id == barra.id:
                        # fluxo entrando na barra: (θ_barra - θ_vizinha)
                        fluxo_total -= b * (theta_to - theta_from)

                # Balanço: geração + déficit + fluxo = carga
                restricoes.append(Eq(geracao + dvar + fluxo_total, carga))

        return restricoes

    def _limite_angulo(self) -> list:
        """
        Cria restrições de limite inferior e superior para os ângulos das barras (exceto slack).

        Returns:
            list[sp.Relational]: Lista de restrições do tipo θ_min ≤ θ ≤ θ_max.
        """
        restricoes = []

        for b in self.full_system.power.buses:
            if b.id == self.slack_id:
                continue  # ignora a barra slack

            theta = self.variables.get(f"theta_{b.id}")
            if theta is None:
                continue

            theta_min = -sp.pi / 2
            theta_max = sp.pi / 2

            restricoes.append(Ge(theta, theta_min))
            restricoes.append(Le(theta, theta_max))

        return restricoes

    def ativar_barra_unica(self):
        """
        Ativa o modo de modelagem como sistema de barra única (sem rede).

        Neste modo:
        - Todas as barras são tratadas como interligadas diretamente;
        - Variáveis de ângulo (theta) e restrições de fluxo de potência são ignoradas;
        - A topologia da rede é desconsiderada;
        - Apenas uma equação global de balanço de potência é utilizada.

        Útil para testes simplificados, análise sem rede ou quando se deseja
        isolar o efeito da geração e da carga sem a influência da malha elétrica.
        """
        self._modo_barra_unica = True

    def _balanco_barra_unica(self) -> list[sp.Equality]:
        """
        Cria uma única equação de balanço de potência ignorando a topologia da rede,
        assumindo todas as barras interligadas.

        Returns:
            list[sp.Equality]: [geração total + déficit total = carga total]
        """
        geracao_total = 0
        carga_total = 0
        deficit_total = 0

        periodos = sorted({l.period for b in self.full_system.power.buses
                        for l in getattr(b, "loads", [])})

        for barra in self.full_system.power.buses:
            for g in getattr(barra, "generators", []):
                geracao_total += self.variables[f"P_{g.id}"]

            for l in getattr(barra, "loads", []):
                carga_total += l.demand_p

            for t in periodos:
                dvar = self.variables.get(f"D_{barra.id}_t{t}", 0)
                deficit_total += dvar

        return [sp.Eq(geracao_total + deficit_total, carga_total)]
