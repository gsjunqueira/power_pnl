"""
Módulo `karush_kuhn_tucker`

Módulo para verificação das condições de otimalidade de Karush-Kuhn-Tucker (KKT)
em problemas de otimização simbólica modelados com SymPy.

Contém a classe KKTChecker, que permite checar estacionariedade, primalidade,
dualidade, não negatividade dos multiplicadores e complementaridade.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from typing import List, Tuple
from sympy import Symbol, diff, im, Mul, Expr, solve

class KKTChecker:
    """
    Classe para verificar as condições de otimalidade de Karush-Kuhn-Tucker (KKT)
    para problemas de otimização com restrições.

    As 6 condições teóricas verificadas são:

        1. Estacionariedade:
            ∂L/∂x_j = 0 (ou ≤ 0 / ≥ 0 no caso de fronteira)

        2. Complementaridade primal:
            x_j * ∂L/∂x_j = 0

        3. Satisfação das restrições:
            g_i(x*) - b_i {≤, ≥, =} 0

        4. Complementaridade dual:
            λ_i * (g_i(x*) - b_i) = 0

        5. Domínio das variáveis:
            x_j^{min} ≤ x_j^* ≤ x_j^{max}

        6. Validade dos multiplicadores:
            - Para **igualdade**: λ_i ∈ ℝ
            - Para **desigualdade**: λ_i ≥ 0 e ∈ ℝ

    A entrada esperada é a Lagrangeana simbólica já ajustada com os sinais corretos
    (i.e., sem necessidade de reidentificar os tipos das restrições), e um dicionário 
    com todas as variáveis (primal, dual e folgas).

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
        self.restricoes = self._extrair_restricoes()
        # Extração automática das variáveis por tipo
        self.variaveis = {k: v for k, v in solucao.items() if not any(p in str(k)
                                                for p in ["lambda", "pi_up", "pi_dn", "s"])}
        self.multipliers = {
            "lambda": self._extrair_lista("lambda"),
            "pi_up": self._extrair_lista("pi_up"),
            "pi_dn": self._extrair_lista("pi_dn"),
            "s": self._extrair_lista("s"),
        }
        self.resultado_kkt: List[str] = []

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


    def _extrair_restricoes(self) -> List[Tuple[Symbol, Expr]]:
        """
        Extrai as restrições da Lagrangeana no formato (multiplicador, expressão).
        Remove termos com variáveis de folga (ex: s**2), para recuperar a restrição original.
        
        Returns:
            List[Tuple[Symbol, Expr]]: Lista de pares (multiplicador, expressão sem s²).
        """
        restricoes = []

        for termo in self.lagrangeana.args:  # termo por termo do somatório da Lagrangeana
            if isinstance(termo, Mul) and len(termo.args) == 2:
                mult, expr = termo.args

                # Garante que mult é Symbol (ex: lambda1, pi_up1, etc.)
                if isinstance(mult, Symbol):
                    # Remove s_k**2, se houver
                    expr_sem_s = expr
                    for subtermo in expr.args:
                        if (subtermo.is_Pow and isinstance(subtermo.base, Symbol) and
                            str(subtermo.base).startswith('s')):
                            expr_sem_s -= subtermo
                    restricoes.append((mult, expr_sem_s))

        return restricoes

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
                mensagem = f"[KKT] Estacionariedade falhou para {var}: ∂L/∂{var} = {valor}"
                print(mensagem)
                self.resultado_kkt.append(mensagem)
                return False
        return True

    def verificar_complementaridade_primal(self) -> bool:
        """
        Verifica a Condição 2 de KKT: complementaridade primal.
        Para cada variável primal x_j, verifica se:
            x_j * ∂L/∂x_j ≈ 0

        Returns:
            bool: True se todas forem satisfeitas, False se alguma violar.
        """
        for var in self.variaveis:
            derivada = diff(self.lagrangeana, var)
            deriv_val = derivada.evalf(subs=self.solucao)
            var_val = self.solucao[var]

            produto = deriv_val * var_val
            if abs(produto) > self.tol:
                mensagem = (f"[KKT] Complementaridade primal violada: {var} * dL/d{var} "
                      "= {var_val} * {deriv_val} = {produto}")
                print(mensagem)
                self.resultado_kkt.append(mensagem)
                return False

        return True

    def verificar_satisfacao_restricoes(self) -> bool:
        """
        Verifica a Condição 3 de KKT: satisfação das restrições.
        Cada restrição deve estar satisfeita no ponto ótimo:
            - Igualdade: g(x*) == 0
            - Desigualdade ≥ (pi_dn): g(x*) ≥ 0
            - Desigualdade ≤ (pi_up): g(x*) ≤ 0

        Returns:
            bool: True se todas as restrições forem satisfeitas.
        """
        for mult, expr in self.restricoes:
            valor = expr.evalf(subs=self.solucao)

            if str(mult).startswith("lambda"):
                if abs(valor) > self.tol:
                    mensagem = f"[KKT] Igualdade não satisfeita: {mult} → {expr} = {valor} ≠ 0"
                    print(mensagem)
                    self.resultado_kkt.append(mensagem)
                    return False

            elif str(mult).startswith("pi_dn"):
                if valor < -self.tol:
                    mensagem = f"[KKT] Desigualdade (≥) violada: {mult} → {expr} = {valor} < 0"
                    print(mensagem)
                    self.resultado_kkt.append(mensagem)
                    return False

            elif str(mult).startswith("pi_up"):
                if valor > self.tol:
                    mensagem = f"[KKT] Desigualdade (≤) violada: {mult} → {expr} = {valor} > 0"
                    print(mensagem)
                    self.resultado_kkt.append(mensagem)
                    return False

        return True

    def verificar_complementaridade_dual(self) -> bool:
        """
        Verifica a Condição 4 de KKT: complementaridade dual.
        Para cada restrição (de desigualdade), verifica se:
            λ_i * (g_i(x*) - b_i) ≈ 0

        Returns:
            bool: True se todas forem satisfeitas, False se alguma violar.
        """

        for mult, expr in self.restricoes:

            val_mult = self.solucao[mult]
            val_expr = expr.evalf(subs=self.solucao)

            produto = val_mult * val_expr
            if abs(produto) > self.tol:
                mensagem = f"[KKT] Complementaridade dual violada: {mult} * ({expr}) = {produto}"
                print(mensagem)
                self.resultado_kkt.append(mensagem)
                return False

        return True

    def verificar_dominio_primal(self) -> bool:
        """
        Verifica a Condição 5 de KKT: domínio das variáveis.
        Considera apenas restrições simples (1 variável por vez), do tipo:
            - pi_dn: x >= xmin
            - pi_up: x <= xmax

        Returns:
            bool: True se todas as restrições de domínio forem satisfeitas.
        """

        for mult, expr in self.restricoes:
            var_set = expr.free_symbols

            if len(var_set) != 1:
                continue

            var = var_set.pop()
            expr_val = expr.evalf(subs=self.solucao)

            if str(mult).startswith("pi_up") and expr_val > self.tol:
                limite = solve(expr, var)[0]
                mensagem = f"[KKT] Domínio violado: {var} → {var} > {limite}"
                print(mensagem)
                self.resultado_kkt.append(mensagem)
                return False
            elif str(mult).startswith("pi_dn") and expr_val < -self.tol:
                limite = solve(expr, var)[0]
                mensagem = f"[KKT] Domínio violado: {var} → {var} < {limite}"
                print(mensagem)
                self.resultado_kkt.append(mensagem)
                return False

        return True

    def verificar_dominio_multiplicadores(self) -> bool:
        """
        Verifica a Condição 6 de KKT: validade dos multiplicadores.
        
        - lambda (igualdade): deve ser real (parte imaginária nula).
        - pi_up, pi_dn (desigualdades): devem ser reais e ≥ 0.

        Returns:
            bool: True se todos os multiplicadores forem válidos; False caso contrário.
        """
        # Verifica os λ (igualdade)
        for i, val in enumerate(self.multipliers["lambda"]):
            if abs(im(val)) > self.tol:
                mensagem = f"[KKT] Multiplicador λ{i+1} inválido: parte imaginária {val} ≠ 0"
                print(mensagem)
                self.resultado_kkt.append(mensagem)
                return False

        # Verifica os π (desigualdades)
        for nome in ["pi_up", "pi_dn"]:
            for i, val in enumerate(self.multipliers[nome]):
                if abs(im(val)) > self.tol:
                    mensagem = (f"[KKT] Multiplicador {nome}{i+1} inválido: parte imaginária"
                                " {val} ≠ 0")
                    print(mensagem)
                    self.resultado_kkt.append(mensagem)
                    return False
                if val < -self.tol:
                    mensagem = f"[KKT] Multiplicador {nome}{i+1} inválido: valor negativo {val} < 0"
                    print(mensagem)
                    self.resultado_kkt.append(mensagem)
                    return False

        return True

    def verificar_todas(self) -> tuple[bool, list[str]]:
        """
        Executa todas as verificações das condições de otimalidade de KKT.

        Returns:
            bool: True se todas as condições forem satisfeitas; False caso contrário.
        """
        checks = [
            self.verificar_estacionariedade(), # Condição 1
            self.verificar_complementaridade_primal(), # Condição 2
            self.verificar_satisfacao_restricoes(), # Condição 3
            self.verificar_complementaridade_dual(), # Condição 4
            self.verificar_dominio_primal(), # Condição 5
            self.verificar_dominio_multiplicadores(), # Condição 6

        ]
        if all(checks):
            mensagem = "✅ Todas as condições de KKT foram satisfeitas.\n"
            print(mensagem)
            self.resultado_kkt.append(mensagem)
            return True, self.resultado_kkt
        else:
            mensagem = "❌ Solução viola alguma condição de KKT.\n"
            print(mensagem)
            self.resultado_kkt.append(mensagem)
            return False, self.resultado_kkt
