"""
Módulo: initial_guess.py

Gera um dicionário com valores iniciais para as variáveis simbólicas
de otimização baseando-se nos limites dos geradores, fluxo e ângulo.

Autor: Giovani Santiago Junqueira
"""


__author__ = "Giovani Santiago Junqueira"

import sympy as sp
from electric_models.system import FullSystem

# def chute_inicial(variables: dict[str, sp.Symbol], sistema: FullSystem) -> dict:
#     """
#     Gera valores iniciais (chute) para as variáveis simbólicas do modelo de otimização.

#     Esta função percorre o dicionário de variáveis simbólicas e atribui valores iniciais
#     coerentes com os limites físicos e operacionais do sistema elétrico representado por
#     um objeto `FullSystem`.

#     As heurísticas de inicialização adotadas são:
#         - Potência ativa de geradores (P_): média entre pmax e pmin, ou metade de pmax
#         se pmin ausente.
#         - Déficit de carga (D_): inicializado com 0.0.
#         - Fluxo nas linhas (F_): inicializado com 0.0.
#         - Ângulo de fase (θ_): inicializado com 0.0.
#         - Outras variáveis: inicializadas com 0.1 por padrão.

#     Args:
#         variables (dict[str, sp.Symbol]): Dicionário de variáveis simbólicas do modelo.
#         sistema (FullSystem): Objeto contendo a estrutura completa do sistema elétrico.

#     Returns:
#         dict: Dicionário associando cada variável simbólica a um valor numérico inicial.
#     """
#     chute = {}
#     for nome, var in variables.items():
#         if nome.startswith("P_"):
#             for barra in sistema.power.buses:
#                 for g in getattr(barra, "generators", []):
#                     if nome == f"P_{g.id}":
#                         chute[var] = (g.gmax + g.gmin) / 2 if hasattr(g, "gmin") else g.gmax / 2
#                         break
#         elif nome.startswith("D_"):
#             chute[var] = 0.0
#         elif nome.startswith("F_"):
#             chute[var] = 0.0
#         elif nome.startswith("θ_"):
#             chute[var] = 0.0
#         else:
#             chute[var] = 0.1
#     return chute

def chute_inicial(variables: dict[str, sp.Symbol], sistema: FullSystem) -> dict:
    """
    Gera um chute inicial com base na alocação da geração nas barras com carga e
    balanceamento na barra slack (fechamento de balanço de potência).
    """
    chute = {}
    geracoes_alocadas = {}  # armazena geração alocada por gerador
    total_carga = 0.0
    barra_slack = None

    # Primeiro passo: alocar nas barras com carga
    for barra in sistema.power.buses:
        carga_barra = sum(l.demand_p for l in getattr(barra, "loads", []))
        total_carga += carga_barra

        if not getattr(barra, "loads", []):
            barra_slack = barra  # sem carga => é a slack
            continue

        geradores = getattr(barra, "generators", [])
        total_gmax = sum(g.gmax for g in geradores)
        if total_gmax == 0:
            continue

        for g in geradores:
            var = variables.get(f"P_{g.id}")
            if var is None:
                continue
            # Aloca proporcional ao gmax, limitado por gmax
            alocacao = min(g.gmax, carga_barra * (g.gmax / total_gmax))
            chute[var] = alocacao
            geracoes_alocadas[g.id] = alocacao

    # Segundo passo: fechar balanço na slack
    if barra_slack:
        geradores_slack = getattr(barra_slack, "generators", [])
        soma_geracoes = sum(geracoes_alocadas.values())
        restante = total_carga - soma_geracoes

        for g in geradores_slack:
            var = variables.get(f"P_{g.id}")
            if var is None:
                continue
            chute[var] = restante

    # Demais variáveis
    for nome, var in variables.items():
        if var in chute:
            continue  # já atribuído

        if nome.startswith("D_"):
            chute[var] = 0.0
        elif nome.startswith("theta_"):
            chute[var] = 0.0
        else:
            chute[var] = 0.1

    return chute
