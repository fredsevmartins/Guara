# Guara — documentação em português

**Torne o conhecimento de IA verificável.**

Guara é o novo nome do produto OpenTruth. O pacote, o comando `opentruth`, a classe
`OpenTruth` e a pasta de dados `.opentruth/` continuam compatíveis. O repositório remoto
também foi renomeado para `fredsevmartins/Guara`.

O Guara é uma ferramenta local para registrar afirmações, fontes, relações de evidência,
revisões e possíveis conflitos numéricos em SQLite. Depois da instalação das dependências,
funciona offline, sem LLM, conta em nuvem ou chaves de API. A versão atual é **0.1.3**.

Uma afirmação registrada não é necessariamente verdadeira. Uma citação não é prova.
O sistema organiza evidências e seu histórico; a avaliação científica continua sendo necessária.

## Instalação

Requer Python 3.11 ou superior. No terminal:

```sh
git clone https://github.com/fredsevmartins/Guara.git
cd Guara
python -m venv .venv
```

Ative o ambiente no Linux/macOS com `. .venv/bin/activate` ou no PowerShell do Windows
com `.\.venv\Scripts\Activate.ps1`. Em seguida:

```sh
python -m pip install -e ".[dev]"
python -m examples.tutorial
```

O tutorial usa dados inteiramente sintéticos em um diretório temporário. Ele demonstra registro,
vínculo de evidência, revisão, histórico, backup e restauração, com verificações executáveis.
Para uso sem ferramentas de desenvolvimento, instale com `python -m pip install -e .`.
A ingestão segura de arquivos locais exige POSIX; os fluxos de metadados funcionam no Windows.
Não há publicação no PyPI confirmada.

## Seu primeiro registro

Escolha uma pasta autorizada para seus dados. Os comandos abaixo criam o armazenamento
`.opentruth/` na pasta atual e acrescentam uma afirmação sintética:

```sh
opentruth init
opentruth claim add "SYNTHETIC: beam Q is 1 m long." --subject "beam Q" --predicate length --value 1 --unit m
opentruth --format text claim list --query "beam Q"
opentruth export > evidence.json
opentruth backup snapshot.zip
```

A saída padrão é JSON. As opções globais, como `--workspace CAMINHO` e `--format text`,
ficam antes do comando. O arquivo `evidence.json` contém metadados e referências; o backup
inclui também os arquivos de fontes registrados.

## Como interpretar os resultados

| Conceito | Significado |
| --- | --- |
| Afirmação | Texto registrado, com versões e contexto opcional |
| Fonte | Referência bibliográfica e, opcionalmente, cópia de arquivo local |
| `SUPPORTS` / `CONTRADICTS` | Relações explicitamente registradas, sem validação independente |
| `NEEDS_REVIEW` | Estado de revisão que solicita avaliação |
| `SUPPORTED_BY_REGISTERED_EVIDENCE` | Há evidência de apoio registrada para a versão atual |
| Integridade de arquivo | Verificação dos bytes, sem avaliar a veracidade do conteúdo |

Diferenças numéricas só são comparadas segundo regras explícitas de sujeito, propriedade,
contexto, unidades e tolerâncias. Um possível conflito não é uma conclusão científica.
Ao revisar uma afirmação, os vínculos anteriores precisam de reavaliação explícita para
contribuir ao resumo da nova versão.

## Guias completos

Os guias técnicos abaixo estão em inglês:

- [Início rápido com vínculos de evidência](../quickstart.md) e [tutorial completo](../tutorial.md)
- [API Python](../python-api.md), [CLI](../cli-reference.md) e [integração MCP](../mcp-integration.md)
- [Modelo de evidências](../evidence-model.md) e [regras de comparação](../conflict-detection.md)
- [Backup e integridade](../backup-and-integrity.md), [limitações](../limitations.md) e [solução de problemas](../troubleshooting.md)
- [Índice de documentação](../README.md) e [como contribuir](../../CONTRIBUTING.md)

## Guará, nosso mascote

<img src="../../assets/mascot-guara.png" width="280" alt="Guará, um lobo-guará apoiado nas quatro patas, com óculos e lenço turquesa.">

Guará é um lobo-guará inspirado na fauna brasileira. As pernas longas, a pelagem alaranjada,
a crina escura e as orelhas grandes preservam a identidade do animal. Agora ele está apoiado nas
quatro patas, com óculos e lenço turquesa, representando curiosidade e evidências conectadas,
sem prometer certezas. Consulte o [guia do mascote](../mascot.md).

## Como citar

DOI: [10.5281/zenodo.23870405](https://doi.org/10.5281/zenodo.23870405).
Use os metadados de [CITATION.cff](../../CITATION.cff) e informe a versão utilizada.

## Fluxos completos no terminal

A versão 0.1.3 permite buscar com filtros, vincular evidências, revisar afirmações e reavaliar
vínculos sem um objeto JSON completo. Use `claim list --query`, `--subject`, `--predicate`
e `--review-status` para combinar filtros. Para corrigir, use `claim revise ID --statement`
com `--reason` e `--actor`. Os exemplos completos estão no [início rápido](../quickstart.md).
Uma correção preserva as versões anteriores e exige reavaliação explícita das evidências.

## Operação, resultados e suporte

Para usar com dados próprios, consulte o [guia de operação](../operations.md): localização dos
dados, testes de restauração, atualização e retenção. A [tabela de estados](../statuses.md)
separa revisão humana, relações de evidência, comparação numérica e integridade de arquivos.
O [glossário](../glossary.md) define os termos. Para problemas, siga a
[solução de problemas](../troubleshooting.md) e as [orientações de suporte](../support.md).
Esses guias técnicos estão em inglês. A documentação em `main` recebe correções após o lançamento;
os arquivos da release 0.1.3 mantêm a documentação da data de publicação.
