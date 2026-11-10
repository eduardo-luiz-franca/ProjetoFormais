"""Simulação: decide se uma cadeia pertence à linguagem do autômato."""


def simular_afn(afn, cadeia):
    """Mantém o conjunto de estados ativos e avança todos juntos (sem backtracking)."""
    ativos = afn.fecho_epsilon({afn.inicial})
    for c in cadeia:
        ativos = afn.fecho_epsilon(afn.mover(ativos, c))
    return afn.final in ativos


def simular_afd(afd, cadeia):
    """Um estado por vez; cada símbolo é uma consulta à tabela.

    Devolve (aceita, caminho), onde caminho é a lista de estados visitados.
    Símbolo fora do alfabeto da ER: rejeita na hora.
    """
    q = afd.inicial
    caminho = [q]
    for c in cadeia:
        if c not in afd.alfabeto:
            return False, caminho
        q = afd.transicoes[q][c]
        caminho.append(q)
    return q in afd.finais, caminho
