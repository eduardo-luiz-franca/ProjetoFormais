# RegexAFD

Motor de expressões regulares feito do zero, sem o módulo `re`, para a disciplina
Linguagens Formais e Computabilidade (UFPB):

```text
ER ──parser──▶ árvore ──Thompson──▶ AFN-ε ──subconjuntos──▶ AFD ──minimização──▶ AFD mínimo
```

## Como rodar

Precisa só do Python 3.10 ou superior, sem nenhuma biblioteca externa.

```bash
python main.py "(a|b)*abb"
```

O programa mostra o número de estados de cada etapa e a tabela do AFD mínimo.
Os três autômatos são salvos em `saida/` como `.json` e `.dot`. Depois, ele lê
cadeias e responde se cada uma é aceita, mostrando o caminho de estados.

Para ver um `.dot` como imagem, cole o conteúdo em
<https://dreampuf.github.io/GraphvizOnline> ou, com o Graphviz instalado, rode
`dot -Tpng saida/afd_min.dot -o afd_min.png`.

## Sintaxe

| ER | significado |
| --- | --- |
| `ab` | concatenação |
| `a\|b` | união |
| `a*` | zero ou mais |
| `a+` | um ou mais (vira `aa*`) |
| `a?` | opcional (vira `a\|ε`) |
| `( )` | agrupamento; `()` sozinho é ε |
| `ε` | cadeia vazia |
| `[abc]`, `[a-z0-9]` | classe (vira `a\|b\|c`) |
| `\d` | dígito (`[0-9]`) |
| `\*`, `\(`, `\\` … | o próprio caractere especial |

A cadeia inteira precisa casar com a ER, como em `re.fullmatch`.

## Arquivos

| arquivo | conteúdo |
| --- | --- |
| `regexafd/parser.py` | ER → árvore (descida recursiva) |
| `regexafd/thompson.py` | árvore → AFN-ε, com fecho-ε e mover |
| `regexafd/afd.py` | AFN → AFD (subconjuntos) e minimização |
| `regexafd/simulacao.py` | simulação do AFN e do AFD |
| `regexafd/exportar.py` | JSON e DOT |
| `main.py` | programa principal |

## Decisões

- A árvore só tem união, concatenação e estrela, como na definição formal de
  ER. O parser reescreve `+`, `?`, as classes e `\d` usando esses três
  operadores.
- O alfabeto é o conjunto de caracteres que aparecem na ER. Um caractere fora
  dele é rejeitado direto.
- O AFD é completo: o conjunto vazio da construção dos subconjuntos vira um
  estado de erro (sumidouro).
- A minimização remove os estados inalcançáveis e refina a partição
  {finais, não finais} até ela não mudar mais.

## Limitações

Não há `.`, classes negadas `[^...]`, repetição `{n,m}`, âncoras nem grupos de
captura.
