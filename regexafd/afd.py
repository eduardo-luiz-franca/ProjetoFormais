"""AFD: construção dos subconjuntos (AFN → AFD) e minimização (AFD → AFD mínimo)."""

from dataclasses import dataclass


@dataclass
class AFD:
    alfabeto: list
    transicoes: dict  # transicoes[q][simbolo] = destino (função total: há sumidouro)
    inicial: int
    finais: set

    @property
    def n_estados(self):
        return len(self.transicoes)


def construir_afd(afn):
    """Construção dos subconjuntos.

    Cada estado do AFD é um conjunto de estados do AFN:
      - inicial = fecho-ε({inicial do AFN})
      - δ(T, a) = fecho-ε(mover(T, a))
      - T é final se contém o final do AFN
    O conjunto vazio vira o estado de erro (sumidouro).
    """
    alfabeto = afn.alfabeto()
    inicial = afn.fecho_epsilon({afn.inicial})
    numero = {inicial: 0}  # conjunto de estados do AFN → número do estado no AFD
    pendentes = [inicial]
    transicoes = {}

    while pendentes:
        conjunto = pendentes.pop(0)
        q = numero[conjunto]
        transicoes[q] = {}
        for simbolo in alfabeto:
            destino = afn.fecho_epsilon(afn.mover(conjunto, simbolo))
            if destino not in numero:
                numero[destino] = len(numero)
                pendentes.append(destino)
            transicoes[q][simbolo] = numero[destino]

    finais = {q for conjunto, q in numero.items() if afn.final in conjunto}
    return AFD(alfabeto, transicoes, 0, finais)


def minimizar(afd):
    """Minimização por refinamento de partições.

    1. Remove os estados inalcançáveis.
    2. Começa com dois grupos: finais e não finais.
    3. Separa os estados de um grupo que vão para grupos diferentes com algum
       símbolo. Repete até nenhum grupo mudar.
    4. Cada grupo final vira um estado do AFD mínimo.
    """
    # 1. estados alcançáveis a partir do inicial
    alcancaveis = {afd.inicial}
    pilha = [afd.inicial]
    while pilha:
        q = pilha.pop()
        for d in afd.transicoes[q].values():
            if d not in alcancaveis:
                alcancaveis.add(d)
                pilha.append(d)

    # 2. partição inicial: grupo[q] = número do grupo do estado q
    grupo = {q: (1 if q in afd.finais else 0) for q in alcancaveis}

    # 3. refina até estabilizar
    while True:
        assinaturas = {
            q: (grupo[q],) + tuple(grupo[afd.transicoes[q][s]] for s in afd.alfabeto)
            for q in alcancaveis
        }
        numeros = {}
        novo = {q: numeros.setdefault(a, len(numeros)) for q, a in sorted(assinaturas.items())}
        if len(numeros) == len(set(grupo.values())):
            break
        grupo = novo

    # 4. monta o AFD mínimo, numerando os grupos a partir do grupo do inicial
    ordem = {}
    pilha = [afd.inicial]
    while pilha:
        q = pilha.pop(0)
        if grupo[q] in ordem:
            continue
        ordem[grupo[q]] = len(ordem)
        pilha += [afd.transicoes[q][s] for s in afd.alfabeto]

    transicoes = {}
    for q in alcancaveis:
        transicoes[ordem[grupo[q]]] = {s: ordem[grupo[afd.transicoes[q][s]]] for s in afd.alfabeto}
    finais = {ordem[grupo[q]] for q in afd.finais if q in alcancaveis}
    return AFD(afd.alfabeto, transicoes, 0, finais)
