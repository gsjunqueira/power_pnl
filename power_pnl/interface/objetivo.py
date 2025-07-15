"""
Módulo objetivo.py

Define as funções utilitárias para declarar o tipo de problema
(minimização ou maximização) de forma simbólica e intuitiva.

Estas funções retornam tuplas com o modo e a expressão objetivo, e
são utilizadas diretamente no SymbolicModel:

Exemplo:
    m.obj = minimizar(x1**2 + x2**2)
    m.obj = maximizar(log(x1) - x2**2)
    m.obj = objetivo(sin(x1) - x2**2)

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

def minimizar(expr):
    """
    Declara uma expressão simbólica como objetivo de minimização.

    Args:
        expr (Expr): Expressão simbólica do SymPy.

    Returns:
        tuple: ("min", expr)
    """
    return ("min", expr)

def maximizar(expr):
    """
    Declara uma expressão simbólica como objetivo de maximização.

    Args:
        expr (Expr): Expressão simbólica do SymPy.

    Returns:
        tuple: ("max", expr)
    """
    return ("max", expr)

def objetivo(expr):
    """
    Declara uma expressão simbólica com modo automático (min ou max).

    Args:
        expr (Expr): Expressão simbólica do SymPy.

    Returns:
        tuple: ("auto", expr)
    """
    return ("auto", expr)
