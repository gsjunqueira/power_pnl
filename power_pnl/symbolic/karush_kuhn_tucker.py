"""
Módulo `karush_kuhn_tucker`

Módulo para verificação das condições de otimalidade de Karush-Kuhn-Tucker (KKT)
em problemas de otimização simbólica modelados com SymPy.

Contém a classe KKTChecker, que permite checar estacionariedade, primalidade,
dualidade, não negatividade dos multiplicadores e complementaridade.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from sympy import Symbol, diff, im

class KKTChecker:
    """
    Classe para verificar as condições de otimalidade de Karush-Kuhn-Tucker (KKT)
    para problemas de otimização com restrições.

    As condições verificadas são:
        1. Estacionariedade
        2. Primalidade das folgas
        3. Dualidade (multiplicadores reais)
        4. Positividade dos multiplicadores de desigualdade
        5. Positividade das variáveis de folga (opcional, caso seja modelado com s²)
        6. Complementaridade entre multiplicadores e folgas

    A entrada esperada é a Lagrangeana simbólica completa e a solução contendo
    todas as variáveis (primal, dual, e folgas) em um único dicionário.

    A classe foi projetada para uso simbólico com SymPy.
    """

    def __init__(self, lagrangeana, solucao, tol=1e-8):
        """
        Inicializa o verificador de condições de otimalidade de Karush-Kuhn-Tucker (KKT).

        Args:
            lagrangeana (sympy.Expr): Expressão simbólica da Lagrangeana.
            solucao (dict): Dicionário contendo TODAS as variáveis da solução (primal, dual e
            folgas), como: {"P_GT01": ..., "lambda1": ..., "pi_up1": ..., "s1": ..., ...}.
            tol (float): Tolerância para comparações numéricas.
        """
        self.lagrangeana = lagrangeana
        self.solucao = solucao
        self.tol = tol

        # Extração automática das variáveis por tipo
        self.variaveis = {k: v for k, v in solucao.items() if not any(p in str(k)
                                                for p in ["lambda", "pi_up", "pi_dn", "s"])}
        self.multipliers = {
            "lambda": self._extrair_lista("lambda"),
            "pi_up": self._extrair_lista("pi_up"),
            "pi_dn": self._extrair_lista("pi_dn"),
            "s": self._extrair_lista("s"),
        }

    def _extrair_lista(self, prefixo):
        """
        Extrai uma lista ordenada de valores da solução para os multiplicadores ou folgas
        com base em um prefixo (ex: "lambda", "pi_up", "s").

        Args:
            prefixo (str): Prefixo a ser buscado nas chaves da solução.

        Returns:
            list: Lista de valores ordenada por índice extraído do nome da variável.
        """
        itens = [(int(str(k)[len(prefixo):]), v) for k, v in self.solucao.items()
                 if str(k).startswith(prefixo)]
        return [v for _, v in sorted(itens)]

    def _subs_mults(self):
        """
        Cria um dicionário de substituições para os multiplicadores e folgas, útil para
        avaliar expressões.

        Returns:
            dict: Dicionário {Symbol: valor} com todos os multiplicadores substituídos.
        """
        subs = {}
        for nome, lista in self.multipliers.items():
            for i, val in enumerate(lista):
                subs[Symbol(f"{nome}{i+1}")] = val
        return subs

    def verificar_estacionariedade(self):
        """
        Verifica a condição de estacionariedade: o gradiente da Lagrangeana deve ser zero 
        em relação a todas as variáveis de decisão.

        Returns:
            bool: True se todas as derivadas forem menores que a tolerância; False caso contrário.
        """
        for var in self.variaveis:
            derivada = diff(self.lagrangeana, var)
            valor = derivada.evalf(subs=self.solucao)
            if abs(valor) > self.tol:
                print(f"[KKT] Estacionariedade falhou para {var}: ∂L/∂{var} = {valor}")
                return False
        return True

    def verificar_primalidade_folgas(self):
        """
        Verifica se os valores das variáveis de folga são reais (sem parte imaginária
        significativa).

        Returns:
            bool: True se todas as folgas forem reais dentro da tolerância; False caso contrário.
        """
        for i, s in enumerate(self.multipliers["s"]):
            if abs(im(s).evalf()) > self.tol:
                print(f"[KKT] Primalidade (folga s{i+1}) tem parte imaginária não nula: {s}")
                return False
        return True

    def verificar_dualidade(self):
        """
        Verifica se os multiplicadores de Lagrange são reais (sem parte imaginária significativa).

        Returns:
            bool: True se todos os multiplicadores forem reais; False caso contrário.
        """
        for nome in ["lambda", "pi_up", "pi_dn"]:
            for i, val in enumerate(self.multipliers[nome]):
                if abs(im(val).evalf()) > self.tol:
                    print(f"[KKT] Dualidade (multiplicador {nome}{i+1}) tem parte imaginária não nula: {val}")
                    return False
        return True

    def verificar_positividade_duais(self):
        """
        Verifica a condição de não negatividade dos multiplicadores associados às restrições de
        desigualdade.

        Returns:
            bool: True se todos os multiplicadores forem ≥ 0 (dentro da tolerância); False caso
            contrário.
        """
        for nome in ["pi_up", "pi_dn"]:
            for i, val in enumerate(self.multipliers[nome]):
                if val < -self.tol:
                    print(f"[KKT] Violação de positividade: {nome}{i+1} = {val} < 0")
                    return False
        return True

    def verificar_positividade_folgas(self):
        """
        [Ignorada se folgas modeladas com s²] 
        Verifica se as variáveis de folga são não-negativas.

        Returns:
            bool: True sempre, pois a verificação foi desativada.
        """
        # for i, s in enumerate(self.multipliers["s"]):
        #     if abs(im(s).evalf()) > self.tol:
        #         continue
        #     if re(s).evalf() < -self.tol:
        #         print(f"[KKT] Violação de positividade (s{i+1}): {s} < 0")
        #         return False
        return True

    def verificar_complementaridade(self):
        """
        Verifica a condição de complementaridade: para cada par (pi, s), o produto deve ser zero.

        Returns:
            bool: True se todos os produtos pi * s forem menores que a tolerância; False caso
            contrário.
        """
        total_up = len(self.multipliers["pi_up"])
        for i in range(total_up):
            prod = self.multipliers["pi_up"][i] * self.multipliers["s"][i]
            if abs(prod) > self.tol:
                print(f"[KKT] Complementaridade falhou: pi_up{i+1} * s{i+1} = {prod}")
                return False
        for i in range(len(self.multipliers["pi_dn"])):
            j = i + total_up
            prod = self.multipliers["pi_dn"][i] * self.multipliers["s"][j]
            if abs(prod) > self.tol:
                print(f"[KKT] Complementaridade falhou: pi_dn{i+1} * s{j+1} = {prod}")
                return False
        return True

    def verificar_todas(self):
        """
        Executa todas as verificações das condições de otimalidade de KKT.

        Returns:
            bool: True se todas as condições forem satisfeitas; False caso contrário.
        """
        checks = [
            self.verificar_estacionariedade(),
            self.verificar_primalidade_folgas(),
            self.verificar_dualidade(),
            self.verificar_positividade_duais(),
            self.verificar_positividade_folgas(),
            self.verificar_complementaridade()
        ]
        if all(checks):
            print("✅ Todas as condições de KKT foram satisfeitas.\n")
            return True
        else:
            print("❌ Solução viola alguma condição de KKT.\n")
            return False
