# Guara 0.1.3 — comece aqui

Guara organiza afirmações, fontes e histórico de evidências localmente. É uma ferramenta de
terminal, API Python e servidor MCP stdio. A marca era OpenTruth; o pacote, o comando e a
classe continuam sendo `opentruth` e `OpenTruth`, para compatibilidade.

## Instalar o produto

Baixe o ZIP ou o wheel em [GitHub Releases](https://github.com/fredsevmartins/Guara/releases).
Requer Python 3.11 ou superior. Extraia o arquivo `Guara-0.1.3.zip`, abra um terminal dentro
da pasta `Guara` e execute:

```sh
python -m venv .venv
```

Ative o ambiente:

- Linux/macOS: `. .venv/bin/activate`
- PowerShell no Windows: `.\.venv\Scripts\Activate.ps1`
- Prompt de Comando no Windows: `.venv\Scripts\activate.bat`

Instale o pacote que acompanha a entrega:

```sh
python -m pip install dist/opentruth-0.1.3-py3-none-any.whl
opentruth --version
python -m pip check
```

A saída da versão deve ser `Guara 0.1.3`. A instalação inicial baixa dependências Python;
depois dela, as operações locais funcionam offline. Não são necessárias chaves de API.
Se você baixou somente o wheel, use o caminho desse arquivo no comando de instalação.

## Experimentar sem alterar seus dados

Ainda na pasta extraída, rode o tutorial sintético:

```sh
python -m examples.tutorial
```

Ele usa e remove uma pasta temporária. A saída deve mostrar `synthetic: true`,
`history_events: 5`, `backup_restored: true` e
`evidence_status: CONTRADICTED_BY_REGISTERED_EVIDENCE`. Os valores não são observações reais.

## Criar seu armazenamento

Crie uma pasta para seu trabalho. Os comandos abaixo usam uma pasta nova chamada `meus-dados`:

```sh
mkdir meus-dados
opentruth --workspace meus-dados init
opentruth --workspace meus-dados claim add "SYNTHETIC: beam Q is 1 m long." --subject "beam Q" --predicate length --value 1 --unit m
opentruth --workspace meus-dados --format text claim list
opentruth --workspace meus-dados export > evidence.json
opentruth --workspace meus-dados backup snapshot.zip
```

Use o mesmo workspace para cada operação. Os dados ficam em `meus-dados/.opentruth/`,
o backup em `meus-dados/snapshot.zip` e a exportação em `evidence.json` na pasta do terminal.
O backup inclui arquivos de fontes registrados; a exportação JSON contém metadados e referências.

Para vincular uma fonte, revisar evidências e entender os estados, consulte o
[início rápido](docs/quickstart.md), o [guia em português](docs/pt-BR/README.md) e o
[índice da documentação](docs/README.md).

## Assistentes de IA e Python

A integração exige um cliente que inicie servidores MCP locais por stdio. Consulte
[configuração MCP](docs/mcp-integration.md); não há servidor HTTP remoto implementado.
Para Python, use `from opentruth import OpenTruth` e consulte a [API](docs/python-api.md).

## Estado da entrega

- Versão 0.1.3: 106 testes aprovados em Linux/Python 3.12, incluindo sessão MCP real.
- Tutorial, cenários sintéticos, Ruff, links locais e instalação isolada do wheel aprovados.
- Mascote Guará corrigido: dois braços e duas pernas; arte em `assets/mascot-guara.png`.
- DOI informado: https://doi.org/10.5281/zenodo.23870405.
- O repositório remoto foi renomeado pelo proprietário para `fredsevmartins/Guara` e confirmado
  pela API do GitHub. Veja os [detalhes de compatibilidade](docs/repository-name.md).
- Os arquivos públicos da versão ficam em [GitHub Releases](https://github.com/fredsevmartins/Guara/releases),
  com ZIP completo, wheel, código-fonte, mascote, arte de divulgação e checksums SHA-256.
- O pacote e o comando continuam sendo `opentruth`; publicação no PyPI não faz parte desta entrega.

Fontes registradas e bytes íntegros não estabelecem verdade científica. A ingestão segura de
arquivos locais exige POSIX; no Windows, use os fluxos de metadados. Consulte as
[limitações](docs/limitations.md) antes de adotar fluxos com dados reais.
