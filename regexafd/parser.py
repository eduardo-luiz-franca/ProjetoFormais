"""Parser: transforma o texto da expressão regular numa árvore (AST).

Gramática (precedência crescente: | < concatenação < * + ?):

    uniao    → concat ( '|' concat )*
    concat   → postfixo*                (vazio = ε)
    postfixo → atomo ( '*' | '+' | '?' )*
    atomo    → símbolo | '\\' escape | '(' uniao ')' | '[' classe ']' | 'ε'

Cada regra vira um método (descida recursiva). Só três operadores ficam na
árvore — união, concatenação e estrela —, como na definição formal de ER.
Os outros são reescritos:

    r+    = r r*
    r?    = r | ε
    [a-c] = a | b | c
    \\d    = 0 | 1 | ... | 9
"""

from dataclasses import dataclass


@dataclass
class Vazio:
    """ε (a cadeia vazia)."""


@dataclass
class Simbolo:
    caractere: str


@dataclass
class Concat:
    esquerda: object
    direita: object


@dataclass
class Uniao:
    esquerda: object
    direita: object


@dataclass
class Estrela:
    filho: object


class ErroDeSintaxe(Exception):
    def __init__(self, mensagem, posicao):
        super().__init__(f"posição {posicao}: {mensagem}")
        self.posicao = posicao


ESPECIAIS = set("|*+?()[]\\")
DIGITOS = "0123456789"


def parse(er):
    return Parser(er).analisar()


def uniao_de(caracteres):
    """[abc] → a | b | c"""
    arvore = Simbolo(caracteres[0])
    for c in caracteres[1:]:
        arvore = Uniao(arvore, Simbolo(c))
    return arvore


class Parser:
    def __init__(self, er):
        self.er = er
        self.pos = 0

    def atual(self):
        return self.er[self.pos] if self.pos < len(self.er) else None

    def avancar(self):
        c = self.er[self.pos]
        self.pos += 1
        return c

    def analisar(self):
        arvore = self.uniao()
        if self.atual() is not None:
            raise ErroDeSintaxe("')' sem '(' correspondente", self.pos)
        return arvore

    def uniao(self):
        arvore = self.concat()
        while self.atual() == "|":
            self.avancar()
            arvore = Uniao(arvore, self.concat())
        return arvore

    def concat(self):
        arvore = None
        while self.atual() is not None and self.atual() not in "|)":
            parte = self.postfixo()
            arvore = parte if arvore is None else Concat(arvore, parte)
        return Vazio() if arvore is None else arvore

    def postfixo(self):
        arvore = self.atomo()
        while self.atual() in ("*", "+", "?"):
            op = self.avancar()
            if op == "*":
                arvore = Estrela(arvore)
            elif op == "+":
                arvore = Concat(arvore, Estrela(arvore))  # r+ = r r*
            else:
                arvore = Uniao(arvore, Vazio())  # r? = r | ε
        return arvore

    def atomo(self):
        c = self.atual()
        if c in ("*", "+", "?"):
            raise ErroDeSintaxe(f"'{c}' sem nada antes", self.pos)
        if c == "]":
            raise ErroDeSintaxe("']' sem '['", self.pos)
        if c == "(":
            inicio = self.pos
            self.avancar()
            arvore = self.uniao()
            if self.atual() != ")":
                raise ErroDeSintaxe("falta fechar o '('", inicio)
            self.avancar()
            return arvore
        if c == "[":
            return uniao_de(self.classe())
        if c == "\\":
            return uniao_de(self.escape())
        if c == "ε":
            self.avancar()
            return Vazio()
        return Simbolo(self.avancar())

    def escape(self):
        """\\d são os dígitos; \\ seguido de caractere especial é o próprio caractere."""
        inicio = self.pos
        self.avancar()
        c = self.atual()
        if c is None:
            raise ErroDeSintaxe("'\\' no fim da expressão", inicio)
        self.avancar()
        if c == "d":
            return DIGITOS
        if c in ESPECIAIS or c in "-ε":
            return c
        raise ErroDeSintaxe(f"escape desconhecido: \\{c}", inicio)

    def classe(self):
        """[abc], [a-z0-9]: devolve os caracteres da classe, sem repetição."""
        inicio = self.pos
        self.avancar()  # '['
        caracteres = []
        while self.atual() != "]":
            if self.atual() is None:
                raise ErroDeSintaxe("falta fechar o '['", inicio)
            if self.atual() == "\\":
                caracteres += self.escape()
                continue
            c = self.avancar()
            if self.atual() == "-" and self.pos + 1 < len(self.er) and self.er[self.pos + 1] != "]":
                self.avancar()  # '-'
                fim = self.avancar()
                if ord(fim) < ord(c):
                    raise ErroDeSintaxe(f"faixa invertida {c}-{fim}", self.pos - 3)
                caracteres += [chr(x) for x in range(ord(c), ord(fim) + 1)]
            else:
                caracteres.append(c)
        self.avancar()  # ']'
        if not caracteres:
            raise ErroDeSintaxe("classe vazia []", inicio)
        return list(dict.fromkeys(caracteres))
