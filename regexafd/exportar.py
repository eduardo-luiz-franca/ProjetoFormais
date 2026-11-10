"""Exportação dos autômatos em JSON (formato do enunciado) e DOT (Graphviz).

AFD:  {"q0": {"a": "q1", "b": "q0"}, ..., "inicial": "q0", "finais": ["q4"]}
AFN:  {"q0": {"ε": ["q1", "q5"]}, ...}   (no AFN o destino é uma lista de estados)

O .dot pode ser aberto em https://dreampuf.github.io/GraphvizOnline ou
convertido em imagem com:  dot -Tpng arquivo.dot -o arquivo.png
"""

import json

from .afd import AFD


def nome(q):
    return f"q{q}"


def para_json(automato):
    dados = {}
    if isinstance(automato, AFD):
        for q, saidas in automato.transicoes.items():
            dados[nome(q)] = {s: nome(d) for s, d in saidas.items()}
        finais = automato.finais
    else:
        for q, arestas in automato.transicoes.items():
            saidas = {}
            for s, d in arestas:
                saidas.setdefault("ε" if s is None else s, []).append(nome(d))
            dados[nome(q)] = saidas
        finais = {automato.final}
    dados["inicial"] = nome(automato.inicial)
    dados["finais"] = [nome(q) for q in sorted(finais)]
    return json.dumps(dados, ensure_ascii=False, indent=2)


def para_dot(automato):
    if isinstance(automato, AFD):
        arestas = [(q, s, d) for q, saidas in automato.transicoes.items() for s, d in saidas.items()]
        finais = automato.finais
    else:
        arestas = [(q, "ε" if s is None else s, d) for q, lista in automato.transicoes.items() for s, d in lista]
        finais = {automato.final}

    # junta arestas paralelas num rótulo só: "a, b"
    rotulos = {}
    for q, s, d in arestas:
        rotulos.setdefault((q, d), []).append(s)

    linhas = ["digraph automato {", "  rankdir=LR;", '  inicio [shape=point];']
    for q in sorted(automato.transicoes):
        forma = "doublecircle" if q in finais else "circle"
        linhas.append(f"  {nome(q)} [shape={forma}];")
    linhas.append(f"  inicio -> {nome(automato.inicial)};")
    for (q, d), simbolos in rotulos.items():
        rotulo = ", ".join(simbolos).replace("\\", "\\\\").replace('"', '\\"')
        linhas.append(f'  {nome(q)} -> {nome(d)} [label="{rotulo}"];')
    linhas.append("}")
    return "\n".join(linhas) + "\n"
