"""
Módulo: convexity_analyzer

Define a classe `ConvexityAnalyzer` para avaliar a convexidade de uma função simbólica
com base em sua matriz Hessiana pré-calculada, domínio de avaliação e variáveis envolvidas.

Suporta:
- Avaliação simbólica ou numérica
- Análise univariada, bivariada e multivariada
- Geração robusta de pontos de avaliação
- Padrões compatíveis com Pylint

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from itertools import product
import numpy as np
import sympy as sp
from sympy.core.sympify import SympifyError


class ConvexityAnalyzer:
    """
    Classe para avaliação da convexidade de uma função simbólica com base na Hessiana.

    Permite análise simbólica ou numérica (via domínio de pontos) para funções com 1 ou
    mais variáveis.
    """

    def __init__(self, hessian: sp.Matrix, variaveis: list, dominio=None):
        """
        Inicializa o analisador de convexidade.

        Args:
            hessian (sp.Matrix): Matriz Hessiana da função.
            variaveis (list): Lista de variáveis simbólicas.
            dominio (list | tuple | dict, optional): Domínio para avaliação numérica.
        """
        self.hessian = hessian
        self.vars = variaveis
        self.dominio = dominio
        self._pontos = self._gerar_pontos() if dominio else []

    def classificar(self) -> str:
        """
        Classifica a convexidade da função de acordo com o número de variáveis.

        Returns:
            str: Tipo de convexidade detectada.
        """
        n = len(self.vars)
        if n == 1:
            return self._convexidade_1d()
        if n == 2:
            return self._convexidade_2d()
        return self._convexidade_nd()

    def _convexidade_1d(self) -> str:
        """
        Avalia a convexidade univariada com base na segunda derivada.

        Returns:
            str: Classificação da função.
        """
        deriv2 = self.hessian[0, 0]
        var = self.vars[0]

        if self._pontos:
            pontos = [p if isinstance(p, (int, float)) else p[0] for p in self._pontos]
            valores = []
            for p in pontos:
                try:
                    val = float(deriv2.evalf(subs={var: p}))
                    valores.append(val)
                except (TypeError, ValueError, ZeroDivisionError, FloatingPointError, SympifyError):
                    continue
            return self._classificar_valores_1d(valores)

        if deriv2.is_number:
            return self._classificar_valores_1d([float(deriv2)])
        return "nem convexa nem côncava"

    def _classificar_valores_1d(self, valores):
        """
        Classifica com base em valores numéricos da segunda derivada.

        Args:
            valores (list[float]): Lista de valores avaliados.

        Returns:
            str: Tipo de convexidade.
        """
        if not valores:
            return "indeterminado"
        if all(v > 0 for v in valores):
            return "estritamente convexa"
        if all(v >= 0 for v in valores):
            return "convexa"
        if all(v < 0 for v in valores):
            return "estritamente côncava"
        if all(v <= 0 for v in valores):
            return "côncava"
        if all(abs(v) < 1e-10 for v in valores):
            return "linear"
        return "nem convexa nem côncava"

    def _convexidade_2d(self) -> str:
        """
        Avalia convexidade para funções bivariadas via determinantes da Hessiana.

        Returns:
            str: Classificação da função.
        """
        x1, x2 = self.vars
        resultados = []

        for p1, p2 in self._pontos:
            try:
                h_eval = self.hessian.evalf(subs={x1: p1, x2: p2})
                h11 = float(h_eval[0, 0])
                h22 = float(h_eval[1, 1])
                det = float(h_eval.det())
                resultados.append((h11, h22, det))
            except (TypeError, ValueError, ZeroDivisionError, FloatingPointError, SympifyError):
                continue

        if not resultados:
            return "indeterminado"

        h11s, h22s, dets = zip(*resultados)
        if self._all_zero(h11s) and self._all_zero(h22s) and self._all_zero(dets):
            return "linear"
        if self._any_negative(dets):
            return "nem convexa nem côncava"
        if self._all_pos(h11s) and self._all_pos(h22s) and self._all_nonneg(dets):
            return "estritamente convexa"
        if self._all_nonneg(h11s) and self._all_nonneg(h22s) and self._all_nonneg(dets):
            return "convexa"
        if self._all_neg(h11s) and self._all_neg(h22s) and all(d > 0 for d in dets):
            return "estritamente côncava"
        if self._all_nonpos(h11s) and self._all_nonpos(h22s) and self._all_nonneg(dets):
            return "côncava"
        return "nem convexa nem côncava"

    def _convexidade_nd(self) -> str:
        """
        Avalia a convexidade multivariada com base nos menores principais da Hessiana.

        Returns:
            str: Classificação da função.
        """
        n = len(self.vars)
        resultados = []

        for ponto in self._pontos:
            try:
                h_eval = self.hessian.evalf(subs=dict(zip(self.vars, ponto)))
                menores = [float(h_eval[:k, :k].det()) for k in range(1, n + 1)]
                resultados.append(menores)
            except (TypeError, ValueError, ZeroDivisionError, FloatingPointError, SympifyError):
                continue

        if not resultados:
            return "indeterminado"

        colunas = list(zip(*resultados))

        if all(self._all_zero(col) for col in colunas):
            return "linear"
        if all(self._all_pos(col) for col in colunas):
            return "estritamente convexa"
        if all(self._all_nonneg(col) for col in colunas):
            return "convexa"
        if all(self._alternancia_estr_concava(col) for col in colunas):
            return "estritamente côncava"
        if all(self._alternancia_concava(col) for col in colunas):
            return "côncava"
        return "nem convexa nem côncava"

    # --- Auxiliares de análise numérica ---

    def _all_pos(self, lst):
        """Verifica se todos os valores são > 0."""
        return all(v > 0 for v in lst)

    def _all_nonneg(self, lst):
        """Verifica se todos os valores são ≥ 0."""
        return all(v >= 0 for v in lst)

    def _all_neg(self, lst):
        """Verifica se todos os valores são < 0."""
        return all(v < 0 for v in lst)

    def _all_nonpos(self, lst):
        """Verifica se todos os valores são ≤ 0."""
        return all(v <= 0 for v in lst)

    def _all_zero(self, lst):
        """Verifica se todos os valores são ≈ 0."""
        return all(abs(v) < 1e-10 for v in lst)

    def _any_negative(self, lst):
        """Verifica se existe algum valor negativo."""
        return any(v < 0 for v in lst)

    def _alternancia_concava(self, lst):
        """Alternância para concavidade: (-1)^k * det_k ≥ 0."""
        return all((v <= 0 if i % 2 == 0 else v >= 0) for i, v in enumerate(lst))

    def _alternancia_estr_concava(self, lst):
        """Alternância estrita: (-1)^k * det_k > 0."""
        return all((v < 0 if i % 2 == 0 else v > 0) for i, v in enumerate(lst))

    def _gerar_pontos(self):
        """
        Gera pontos a partir do domínio definido para avaliação numérica.

        Suporta:
        - Lista de tuplas [(x1, x2, ...)]
        - Tupla global (min, max) ou (min, max, passo)
        - Dicionário {var: (min, max) ou (min, max, passo)}

        Returns:
            list[tuple]: Lista de pontos para avaliação.
        """
        nvars = len(self.vars)

        if isinstance(self.dominio, list):
            if all(isinstance(p, tuple) and len(p) == nvars for p in self.dominio):
                return self.dominio
            raise ValueError("Pontos mal formatados.")

        if isinstance(self.dominio, tuple):
            if len(self.dominio) == 2:
                grid = np.linspace(self.dominio[0], self.dominio[1], 5)
            elif len(self.dominio) == 3:
                grid = np.arange(self.dominio[0], self.dominio[1] + self.dominio[2], self.dominio[2]
                                 )
            else:
                raise ValueError("Tupla deve ter 2 ou 3 elementos.")
            return list(product(*[grid] * nvars))

        if isinstance(self.dominio, dict):
            grades = []
            for var in self.vars:
                intervalo = self.dominio[var]
                if len(intervalo) == 2:
                    grades.append(np.linspace(intervalo[0], intervalo[1], 5))
                elif len(intervalo) == 3:
                    grades.append(np.arange(intervalo[0], intervalo[1] + intervalo[2], intervalo[2])
                                  )
                else:
                    raise ValueError(f"Domínio mal definido para variável {var}.")
            return list(product(*grades))

        raise ValueError("Formato de domínio não reconhecido.")
