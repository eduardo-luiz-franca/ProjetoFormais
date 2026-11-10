"""Construção de Thompson: AST → AFN-ε.

Cada pedaço da ER vira um fragmento de autômato com um estado inicial e um
final. Os fragmentos são ligados com transições ε (representadas por None).
"""

from dataclasses import dataclass, field

from .parser import Concat, Estrela, Simbolo, Uniao, Vazio

EPSILON = None


@dataclass
class AFN:
    n_estados: int = 0
    inicial: int = 0
    final: int = 0
    # transicoes[q] = lista de (símbolo, destino); símbolo None = ε
    transicoes: dict = field(default_factory=dict)

    def novo_estado(self):
        q = self.n_estados
        self.n_estados += 1
        self.transicoes[q] = []
        return q

    def ligar(self, origem, simbolo, destino):
        self.transicoes[origem].append((simbolo, destino))

    def alfabeto(self):
        return sorted({s for arestas in self.transicoes.values() for s, _ in arestas if s is not EPSILON})

    def fecho_epsilon(self, estados):
        """Estados alcançáveis a partir de `estados` usando só transições ε."""
        fecho = set(estados)
        pilha = list(estados)
        while pilha:
            q = pilha.pop()
            for simbolo, destino in self.transicoes[q]:
                if simbolo is EPSILON and destino not in fecho:
                    fecho.add(destino)
                    pilha.append(destino)
        return frozenset(fecho)

    def mover(self, estados, simbolo):
        """Estados alcançáveis a partir de `estados` lendo `simbolo` uma vez."""
        return {d for q in estados for s, d in self.transicoes[q] if s == simbolo}


def construir_afn(arvore):
    afn = AFN()

    def fragmento(no):
        """Cria o fragmento de `no` e devolve (inicial, final)."""
        if isinstance(no, (Vazio, Simbolo)):
            # (i) --a--> (f)   ou   (i) --ε--> (f)
            i, f = afn.novo_estado(), afn.novo_estado()
            afn.ligar(i, no.caractere if isinstance(no, Simbolo) else EPSILON, f)
            return i, f
        if isinstance(no, Concat):
            # final do primeiro --ε--> inicial do segundo
            i1, f1 = fragmento(no.esquerda)
            i2, f2 = fragmento(no.direita)
            afn.ligar(f1, EPSILON, i2)
            return i1, f2
        if isinstance(no, Uniao):
            # novo inicial com ε para os dois; os dois com ε para o novo final
            i, f = afn.novo_estado(), afn.novo_estado()
            for lado in (no.esquerda, no.direita):
                il, fl = fragmento(lado)
                afn.ligar(i, EPSILON, il)
                afn.ligar(fl, EPSILON, f)
            return i, f
        if isinstance(no, Estrela):
            # pode pular (i → f) ou repetir (final do filho → inicial do filho)
            i, f = afn.novo_estado(), afn.novo_estado()
            i1, f1 = fragmento(no.filho)
            afn.ligar(i, EPSILON, i1)
            afn.ligar(i, EPSILON, f)
            afn.ligar(f1, EPSILON, i1)
            afn.ligar(f1, EPSILON, f)
            return i, f
        raise TypeError(no)

    afn.inicial, afn.final = fragmento(arvore)
    return afn
