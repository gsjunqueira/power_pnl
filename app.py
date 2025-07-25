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


def report(arquivo, kkt, solucao, iteracao, fob, custo_operacional, f_obj, t_hessiana, custo_cubico):
    """
    Gera um relatório da solução de um problema de otimização, salvando-o em um arquivo de texto
    e exibindo o mesmo conteúdo no terminal.

    O relatório inclui:
    - Verificação das condições KKT
    - Valores das variáveis da solução
    - Número de iterações do algoritmo
    - Valor da função objetivo (FOB) cúbica
    - Custo operacional total

    Parâmetros:
    ----------
    arquivo : str
        Caminho do arquivo de saída (.txt) onde o relatório será salvo.
    kkt : objeto
        Objeto que possui o método `verificar_todas()` para checar as condições KKT.
    solucao : dict
        Dicionário contendo as variáveis da solução como chaves e suas expressões como valores.
    iteracao : int
        Número de iterações realizadas pelo algoritmo de otimização.
    fob : float
        Valor da função objetivo cúbica ao final da otimização.
    custo_operacional : float
        Custo operacional total calculado com base na solução encontrada.
    """
    _, mensage = kkt.verificar_todas()
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write('\n#---------------------------------------------------------------------#\n')
        f.write("Solução:\n\n")
        f.write(f"Matriz Hessiana possui {t_hessiana}\n")
        for msg in mensage:
            f.write(msg + "\n" )
        for var, val in solucao.items():
            valor = val.evalf() if hasattr(val, "evalf") else val
            f.write(f"{var} = {valor}\n")
        f.write(f"Iterações = {iteracao}\n")
        f.write(f"\nFOB {f_obj}= {fob:.2f}\n")
        f.write(f"\nC.O.2 = {custo_operacional:.2f}\n")
        f.write(f"\nC.O.3 = {custo_cubico:.2f}\n")
        f.write('\n#=====================================================================#\n')

    print('\n#---------------------------------------------------------------------#\n')
    print("Solução:\n")
    print(mensage[-1])
    # for var, val in solucao.items():
    #     print(f"{var} = {val.evalf()}")
    print(f"Iterações = {iteracao}")
    print(f"\nFOB {f_obj}= {fob:.2f}")
    print(f"\nC.O.2 = {custo_operacional:.2f}")
    print(f"\nC.O.3 = {custo_cubico:.2f}")
    print('\n#=====================================================================#\n')

def resolucao(arquivo, sistema, passo, max_iter, f_obj = "cubica", single_bus = False):
    """
    Resolve um problema de otimização simbólica com base em um sistema fornecido,
    utilizando um solver iterativo, e gera um relatório da solução encontrada.

    A função realiza os seguintes passos:
    - Constrói o modelo simbólico a partir do sistema (função objetivo e restrições).
    - Define uma condição inicial apropriada.
    - Executa o solver com o passo e número máximo de iterações definidos.
    - Avalia a solução obtida e calcula métricas como a função objetivo e o custo operacional.
    - Verifica as condições KKT para garantir a otimalidade.
    - Gera um relatório da solução, salvando-o em arquivo e exibindo no terminal.

    Parâmetros:
    ----------
    sistema : objeto
        Objeto com estrutura de sistema de potência, contendo atributos como `.power.buses`, etc.
    arquivo : str
        Caminho para o arquivo onde o relatório final será salvo.
    passo : float
        Valor do passo (tamanho do incremento) utilizado pelo método iterativo do solver.
    max_iter : int
        Número máximo de iterações permitidas na resolução do problema.
    f_obj : str, opcional
        Tipo da função objetivo a ser usada no modelo ("cubica", "quadratica", etc.).
        O padrão é "cubica".

    Retorna:
    -------
    None
        O resultado é salvo no arquivo especificado e impresso no terminal;
        a função não retorna nenhum valor diretamente.
    """
    sm = SymbolicModelBuilder(sistema, tipo=f_obj, method="newton")
    modelo = SymbolicModel()
    if single_bus:
        sm.ativar_barra_unica()
    modelo.obj = minimizar(sm.fob())
    modelo.constraints = sm.restricoes()
    x0_1 = chute_inicial(variables=sm.variaveis(), sistema=sistema)

    solver = SymbolicSolver(modelo, x0=x0_1, passo=passo, max_iter=max_iter)
    resultado = solver.executar()

    solucao = resultado["solucao"]
    iters = resultado["iteracoes"]
    t_hessiana = resultado["hessiana"]
    solucao_dict = {str(var): val.evalf() if hasattr(val, "evalf") else float(val)
                    for var, val in resultado["solucao"].items()}
    fob = sm.get_fob(solucao)
    custo_operacional = sm.custo_operacional(solucao_dict)
    custo_cubico = sm.custo_cubico(solucao)

    kkt = KKTChecker(
        lagrangeana=solver.lagrangian,
        solucao=resultado["solucao"]
    )
    print()
    with open("restricoes_geradas.txt", "a", encoding="utf-8") as f:
        if 'oil' in arquivo:
            comb = 'oil'
        else:
            comb = 'gas'

        f.write(f"\n\nEquações de restrição geradas para função objetiva {f_obj}, "
                f"com barra única = {single_bus}:\n e geradores 1 e 3 com combustível = {comb}\n")
        for idx, restr in enumerate(sm.restricoes(), 1):
            f.write(f"Restrição {idx}: {restr}\n\n")

    report(arquivo, kkt, solucao, iters, fob, custo_operacional, f_obj, t_hessiana, custo_cubico)

def main():
    """
    Ponto de entrada principal do script.

    Executa o carregamento do sistema com base em parâmetros definidos
    diretamente no código (sem depender da linha de comando).
    """

    caminho_json = "data/base_dados.json"
    caso_1 = "DGER_1"
    caso_2 = "DGER_2"

    loader_1 = DataLoader(caminho_json, case=caso_1)
    sistema_1 = loader_1.carregar()
    loader_2 = DataLoader(caminho_json, case=caso_2)
    sistema_2 = loader_2.carregar()

    arquivo1 = "reports/cubico_rede_dc.txt"
    arquivo2 = "reports/quadratica_rede_dc.txt"
    arquivo3 = "reports/cubico_rede_dc_oil.txt"
    arquivo4 = "reports/quadratica_rede_dc_oil.txt"
    arquivo5 = "reports/cubico.txt"
    arquivo6 = "reports/quadratica.txt"
    arquivo7 = "reports/cubico_oil.txt"
    arquivo8 = "reports/quadratica_oil.txt"

    resolucao(arquivo1, sistema_1, passo=1, max_iter=100, f_obj="cubica")
    resolucao(arquivo2, sistema_1, passo=0.2, max_iter=2000, f_obj="quadratica")
    resolucao(arquivo3, sistema_2, passo=0.2, max_iter=2000, f_obj="cubica")
    resolucao(arquivo4, sistema_2, passo=0.8, max_iter=2000, f_obj="quadratica")

    resolucao(arquivo5, sistema_1, passo=0.8, max_iter=2000, f_obj="cubica", single_bus=True)
    resolucao(arquivo6, sistema_1, passo=0.2, max_iter=2000, f_obj="quadratica", single_bus=True)
    resolucao(arquivo7, sistema_2, passo=0.2, max_iter=2000, f_obj="cubica", single_bus=True)
    resolucao(arquivo8, sistema_2, passo=0.8, max_iter=2000, f_obj="quadratica", single_bus=True)

if __name__ == "__main__":
    main()
