"""RegexAFD: ER → AFN-ε (Thompson) → AFD (subconjuntos) → AFD mínimo.

Uso:
    python main.py              (pede a ER)
    python main.py "(a|b)*abb"
"""

import sys
from pathlib import Path

from regexafd.afd import construir_afd, minimizar
from regexafd.exportar import nome, para_dot, para_json
from regexafd.parser import ErroDeSintaxe, parse
from regexafd.simulacao import simular_afd, simular_afn
from regexafd.thompson import construir_afn


def mostrar_tabela(afd):
    """Tabela de transições do AFD (→ inicial, * final)."""
    print("estado  " + "  ".join(f"{s:>3}" for s in afd.alfabeto))
    for q in sorted(afd.transicoes):
        marca = ("→" if q == afd.inicial else " ") + ("*" if q in afd.finais else " ")
        destinos = "  ".join(f"{nome(afd.transicoes[q][s]):>3}" for s in afd.alfabeto)
        print(f"{marca}{nome(q):<5} {destinos}")


def salvar(pasta, automatos):
    pasta.mkdir(exist_ok=True)
    for etapa, automato in automatos.items():
        (pasta / f"{etapa}.json").write_text(para_json(automato), encoding="utf-8")
        (pasta / f"{etapa}.dot").write_text(para_dot(automato), encoding="utf-8")
    print(f"\nAutômatos salvos em {pasta}/ (.json e .dot)")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # o console do Windows não mostra ε e → sem isso
    er = sys.argv[1] if len(sys.argv) > 1 else input("Expressão regular: ")

    try:
        arvore = parse(er)
    except ErroDeSintaxe as erro:
        print(f"Erro de sintaxe na {erro}\n  {er}\n  {' ' * erro.posicao}^")
        return

    afn = construir_afn(arvore)
    afd = construir_afd(afn)
    afd_min = minimizar(afd)

    print(f"\nAFN: {afn.n_estados} estados | AFD: {afd.n_estados} | AFD mínimo: {afd_min.n_estados}")
    print("\nAFD mínimo:")
    mostrar_tabela(afd_min)
    salvar(Path("saida"), {"afn": afn, "afd": afd, "afd_min": afd_min})

    print("\nDigite cadeias para testar (linha vazia para sair).")
    while True:
        try:
            cadeia = input("> ")
        except EOFError:
            break
        if cadeia == "":
            break
        aceita, caminho = simular_afd(afd_min, cadeia)
        assert aceita == simular_afn(afn, cadeia)  # AFN e AFD mínimo têm de concordar
        print(f"  {'ACEITA' if aceita else 'REJEITA'}   caminho: {' → '.join(nome(q) for q in caminho)}")


if __name__ == "__main__":
    main()
