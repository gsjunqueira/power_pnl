"""
Módulo principal

Executa o carregamento do sistema elétrico e hidráulico a partir de um
arquivo JSON, utilizando a classe `DataLoader` definida no módulo `loader.py`.

Permite a escolha do caso de estudo (ex: "DGER_1", "DGER_2") via argumento.

Autor: Giovani Santiago Junqueira
"""

__authot__ = "Giovani Santiago Juqnueira"

from reader import DataLoader
from power_pnl.symbolic import SymbolicModelBuilder, chute_inicial, KKTChecker
from power_pnl.interface import SymbolicModel, minimizar
from power_pnl.solver import SymbolicSolver


def main():
    """
    Ponto de entrada principal do script.

    Executa o carregamento do sistema com base em parâmetros definidos
    diretamente no código (sem depender da linha de comando).
    """

    caminho_json = "data/base_dados.json"
    caso_1 = "DGER_1"
    # caso_2 = "DGER_2"

    loader_1 = DataLoader(caminho_json, case=caso_1)
    sistema_1 = loader_1.carregar()

    m1 = SymbolicModel()
    s1 = SymbolicModelBuilder(sistema_1)
    m1.obj = minimizar(s1.funcao_objetivo())
    m1.constraints = s1.restricoes()
    x0_1 = chute_inicial(variables=s1.variaveis(), sistema=sistema_1)

    solver1 = SymbolicSolver(m1, x0=x0_1, max_iter=2000)
    resultado1 = solver1.executar()

    solucao1 = resultado1["solucao"]
    iters1 = resultado1["iteracoes"]
    solucao_dict1 = {str(var): val.evalf() if hasattr(val, "evalf") else float(val)
                    for var, val in resultado1["solucao"].items()}
    fob1 = s1.get_fob(solucao1)
    custo_operacional1 = s1.custo_operacional(solucao_dict1)

    kkt = KKTChecker(
        lagrangeana=solver1.lagrangian,
        solucao=resultado1["solucao"]
    )

    print('\n#---------------------------------------------------------------------#\n')
    print("Solução:\n")
    kkt.verificar_todas()

    for var, val in solucao1.items():
        print(f"{var} = {val.evalf()}")
    print(f"Iterações = {iters1}")

    print(f"\nFOB = {fob1:.2f}")
    print(f"\nC.O. = {custo_operacional1:.2f}")

    print('\n#=====================================================================#\n')

    # loader_2 = DataLoader(caminho_json, case=caso_2)
    # sistema_2 = loader_2.carregar()

    # m2 = SymbolicModel()
    # s2 = SymbolicModelBuilder(sistema_2)
    # m2.obj = minimizar(s2.funcao_objetivo())
    # m2.constraints = s2.restricoes()
    # x0_2 = chute_inicial(variables=s2.variaveis(), sistema=sistema_2)

    # solver2 = SymbolicSolver(m2, x0=x0_2, max_iter=2000)
    # resultado2 = solver2.executar()
    # solucao2 = resultado2["solucao"]
    # iters2 = resultado2["iteracoes"]
    # solucao_dict2 = {str(var): val.evalf() if hasattr(val, "evalf") else float(val)
    #                 for var, val in resultado2["solucao"].items()}
    # fob2 = s2.get_fob(solucao2)
    # custo_operacional2 = s2.custo_operacional(solucao_dict2)

    # print('\n#---------------------------------------------------------------------#\n')
    # print("Solução ótima:\n")
    # for var, val in solucao2.items():
    #     print(f"{var} = {val.evalf():.4f}")
    # print(f"Iterações = {iters2}")

    # print(f"\nFOB = {fob2:.2f}")
    # print(f"\nC.O. = {custo_operacional2:.2f}")

    # print('\n#=====================================================================#\n')

if __name__ == "__main__":
    main()
