"""
Classe SymbolicSolver

Executa a resolução de um problema de otimização simbólico, construído com SymbolicModel.
Possui detecção automática de sistema linear ou não linear, e aplica o método apropriado:
- sistema linear: resolvido via inversão matricial
- sistema não linear: resolvido via método de Newton iterativo

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import sympy as sp
from sympy.polys.polyerrors import PolynomialError
from power_pnl.engine import LagrangianBuilder, DerivativesCalculator, ConvexityAnalyzer


class SymbolicSolver:
    """
    Solver simbólico que integra todas as etapas: montagem, derivadas e resolução.
    """

    def __init__(self, model, passo=0.1, tol=1e-6, max_iter=20,
                 x0=None, intervalo_convexidade=None):
        """
        Inicializa o solver com o modelo e parâmetros de controle.

        Args:
            model (SymbolicModel): Modelo simbólico criado pelo usuário.
            tol (float): Tolerância para parada no método iterativo.
            max_iter (int): Máximo de iterações permitidas.
        """
        self.model = model.build()
        self.passo = passo
        self.tol = tol
        self.max_iter = max_iter
        self.x0 = x0
        self.intervalo_convexidade = intervalo_convexidade
        self._classificar_localmente = False

        self.lagrangian = None
        self.gradiente = None
        self.hessiana = None
        self.variaveis = None
        self.historico = None

    def executar(self):
        """
        Executa o processo completo: montagem, derivadas e resolução.

        Returns:
            list[dict]: Lista de soluções encontradas.
        """
        self._construir_lagrangeana()

        variaveis_ativas = self.lagrangian.free_symbols
        print("\n[Debug] Variáveis simbólicas na Lagrangeana:")
        for v in sorted(variaveis_ativas, key=str):
            print(f"  - {v}")
        print(self.lagrangian)

        self._calcular_derivadas()
        self._diagnostico_convexidade()

        if self._sistema_linear():
            return self._resolver_linear()
        else:
            return self._resolver_nonlinear_newton()

    def _construir_lagrangeana(self):
        """Monta a Lagrangeana simbólica."""
        builder = LagrangianBuilder(
            objective=self.model.objective,
            variables=self.model.variables,
            constraints=self.model.constraints,
            mode=self.model.mode
        )
        self.lagrangian = builder.get_expression()

    def _calcular_derivadas(self):
        """Calcula o gradiente e a hessiana da Lagrangeana."""
        deriv = DerivativesCalculator(self.lagrangian, self.model.variables)
        self.gradiente = deriv.gradient("all")
        self.hessiana = deriv.hessian("all")
        self.variaveis = self.model.variables.all_symbols()

    def _diagnostico_convexidade(self):
        """
        Executa o diagnóstico de convexidade simbólico ou numérico, com mensagens informativas.
        """
        if self.intervalo_convexidade is None:
            print("[Aviso] Análise de convexidade não realizada (intervalo não fornecido).")
            return

        tipo = ConvexityAnalyzer(self.hessiana, self.model.variables.all_symbols(),
                                 self.intervalo_convexidade).classificar()

        print("\n\n#=====================================================================#\n")
        print(f"\033[1mFunção objetivo:\033[0m {self.model.objective.expr}\n")

        if (self.model.constraints.equalities or
            self.model.constraints.inequalities_up or
            self.model.constraints.inequalities_dn):
            print("Sujeito a:\n")
            for eq in self.model.constraints.equalities:
                print(eq)
            for ineq in self.model.constraints.inequalities_up:
                print(f"\n{ineq[0]} <= {ineq[1]}")
            for ineq in self.model.constraints.inequalities_dn:
                print(f"\n{ineq[0]} >= {ineq[1]}")

        print(f"[Diagnóstico] Lagrangeana classificada como:\033[1;91m {tipo.upper()} \033[0m")
        if tipo in ("côncava", "estritamente côncava"):
            print(f"[Diagnóstico] Função {tipo.upper()} ⇒ ponto de \033[1;91m MÁXIMO \033[0m")
        elif tipo in ("convexa", "estritamente convexa"):
            print(f"[Diagnóstico] Função {tipo.upper()} ⇒ ponto de \033[1;91m MÍNIMO \033[0m")
        elif tipo == "nem convexa nem côncava":
            self._classificar_localmente = True

    def _preparar_chute(self) -> dict[sp.Symbol, float]:
        """
        Prepara o dicionário de valores iniciais (chute) no formato {Symbol: valor},
        garantindo que todas as variáveis simbólicas tenham valor atribuído.

        Aceita diferentes formas de entrada em self.x0:
            - dict com Symbol ou str como chave (pode estar incompleto)
            - float ou int (valor fixo para todas as variáveis)
            - list de floats (na mesma ordem de self.variaveis)

        Retorna:
            dict[sp.Symbol, float]: Chute inicial completo.
        """
        chute = {}

        if isinstance(self.x0, dict):
            if all(isinstance(k, sp.Symbol) for k in self.x0):
                chute = self.x0.copy()
            elif all(isinstance(k, str) for k in self.x0):
                chute = {var: self.x0.get(str(var), None) for var in self.variaveis}

        elif isinstance(self.x0, (int, float)):
            chute = {v: float(self.x0) for v in self.variaveis}

        elif isinstance(self.x0, list) and len(self.x0) == len(self.variaveis):
            chute = {v: float(val) for v, val in zip(self.variaveis, self.x0)}

        # Preencher variáveis faltantes com heurística
        for var in self.variaveis:
            if var not in chute or chute[var] is None:
                nome = str(var)
                if nome.startswith("s"):
                    chute[var] = 0.1
                elif nome.startswith(("pi_up", "pi_dn")):
                    chute[var] = 0.1
                elif nome.startswith("lambda"):
                    chute[var] = 0.1
                else:
                    chute[var] = 0.1

        return chute

    def _sistema_linear(self):
        """
        Verifica se o sistema gerado é linear em todas as variáveis.

        Returns:
            bool: True se todas as equações forem lineares.
        """
        try:
            for expr in self.gradiente:
                poly = expr.as_poly(*self.variaveis)
                if poly is None or poly.total_degree() > 1:
                    return False
            return True
        except PolynomialError:
            return False

    def _resolver_linear(self):
        """
        Resolve o sistema linear Ax = b via inversão simbólica.

        Returns:
            dict: Dicionário com a solução simbólica exata.
        """
        matrix_a, b = sp.linear_eq_to_matrix(self.gradiente, self.variaveis)
        solucao = matrix_a.inv() * b
        return {
            "solucao": dict(zip(self.variaveis, solucao)),
            "fob": self.model.objective.expr.evalf(subs=dict(zip(self.variaveis, solucao))),
            "iteracoes": 1
        }

    def _resolver_nonlinear_newton(self):
        """
        Resolve o sistema não linear via método de Newton-Raphson simbólico.

        Returns:
            dict: Solução numérica aproximada.
        """
        xk = self._preparar_chute()

        print(self.historico)
        for it in range(self.max_iter):
            grad_eval = sp.Matrix([g.evalf(subs=xk) for g in self.gradiente])
            hess_eval = self.hessiana.evalf(subs=xk)

            if grad_eval.norm() < self.tol:

                # Classificação local apenas se necessário
                if self.model.mode == "auto" and getattr(self, "_classificar_localmente", False):
                    hess_local = self.hessiana.evalf(subs=xk)
                    autovalores = hess_local.eigenvals()
                    autovalores_numericos = []
                    for v in autovalores:
                        v_num = v.evalf()
                        if sp.im(v_num) == 0:  # somente autovalores reais
                            autovalores_numericos.append(float(v_num))

                    if not autovalores_numericos:
                        print("\033[1;91m[Diagnóstico] Não foi possível classificar: autovalores complexos\033[0m")
                    elif all(v > 0 for v in autovalores_numericos):
                        print("\033[1;91m[Diagnóstico] Ponto ótimo classificado como: MÍNIMO LOCAL\033[0m")
                    elif all(v < 0 for v in autovalores_numericos):
                        print("\033[1;91m[Diagnóstico] Ponto ótimo classificado como: MÁXIMO LOCAL\033[0m")
                    else:
                        print("\033[1;91m[Diagnóstico] Ponto ótimo classificado como: PONTO DE SELA (INDETERMINADO)\033[0m")

                return {
                    "solucao": xk,
                    "iteracoes": it + 1
                }

            try:
                rank = hess_eval.rank()
                nvars = len(self.variaveis)

                if rank < nvars:
                    raise ValueError(
                        f"Hessiana singular ou mal condicionada: rank = {rank}, esperado = {nvars}")
                delta = -hess_eval.inv() * grad_eval
            except Exception as exc:
                raise ValueError("Hessiana singular ou mal condicionada") from exc

            for i, v in enumerate(self.variaveis):
                xk[v] += delta[i]

        raise ValueError(f"Método de Newton não convergiu em {it+1} iterações")

    def _resolver_gradiente(self, passo: float | None = None, tol: float | None = None):
        """
        Resolve o problema de otimização usando o método do gradiente (descida/subida).

        Returns:
            dict: Dicionário com os valores ótimos das variáveis.
        """

        xk = self._preparar_chute()
        print("\n[Debug] Variáveis armazenadas em self.variaveis:")
        for v in sorted(self.variaveis, key=str):
            print(f"  - {v}")

        alpha = passo if passo is not None else self.passo
        beta = tol if tol is not None else self.tol

        iteracao = 0
        historico = []

        while iteracao < self.max_iter:
            grad = [g.evalf(subs=xk) for g in self.gradiente]
            erro = max(abs(val) for val in grad)
            print(erro)
            historico.append((iteracao, dict(xk), erro))
            if erro <= beta:
                break
            # Atualiza as variáveis (subida ou descida)
            for i, var in enumerate(self.variaveis):
                direcao = alpha * grad[i]
                xk[var] = xk[var] - direcao if self.model.mode == "min" else xk[var] + direcao
            iteracao += 1
        self.historico = historico
        return xk

    # Ponto de extensão futura para outros métodos
    def _resolver_nonlinear_custom(self):
        """Placeholder para outros métodos não lineares (barreira, penalidade, etc)."""
        raise NotImplementedError("Resolver não linear customizado ainda não implementado")
