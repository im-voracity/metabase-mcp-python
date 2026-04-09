> **Idioma**: [English](README.md) | Portugues (BR)

# metabase-mcp-python

Um servidor [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) em Python para o [Metabase](https://www.metabase.com/), permitindo que assistentes de IA consultem bancos de dados, gerenciem dashboards e interajam com sua instancia do Metabase.

Inspirado no [CognitionAI/metabase-mcp-server](https://github.com/CognitionAI/metabase-mcp-server) (TypeScript). Veja [CREDITS.md](CREDITS.md) para atribuicao.

## Instalacao

### Com uv (recomendado)

```bash
uv tool install metabase-mcp-python
```

### Com pip

```bash
pip install metabase-mcp-python
```

### A partir do codigo fonte

```bash
git clone https://github.com/im-voracity/metabase-mcp-python.git
cd metabase-mcp-python
uv sync
```

## Configuracao

Defina as seguintes variaveis de ambiente (ou use um arquivo `.env`):

| Variavel | Obrigatoria | Descricao |
|---|---|---|
| `METABASE_URL` | Sim | URL da sua instancia Metabase (ex: `http://localhost:3000`) |
| `METABASE_API_KEY` | Uma das | Chave de API do Metabase para autenticacao |
| `METABASE_USERNAME` | Uma das | Usuario para autenticacao via sessao |
| `METABASE_PASSWORD` | Uma das | Senha para autenticacao via sessao |

Voce deve fornecer `METABASE_API_KEY` ou ambos `METABASE_USERNAME` e `METABASE_PASSWORD`.

## Uso

### Claude Desktop

Adicione ao seu `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["tool", "run", "metabase-mcp-python"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_API_KEY": "sua-chave-api"
      }
    }
  }
}
```

Com autenticacao via sessao:

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["tool", "run", "metabase-mcp-python"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_USERNAME": "usuario@exemplo.com",
        "METABASE_PASSWORD": "sua-senha"
      }
    }
  }
}
```

### Claude CLI

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["tool", "run", "metabase-mcp-python", "--write"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_API_KEY": "sua-chave-api"
      }
    }
  }
}
```

### Executando a partir do codigo fonte

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["run", "--directory", "/caminho/para/metabase-mcp-python", "metabase-mcp"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_API_KEY": "sua-chave-api"
      }
    }
  }
}
```

## Modos de Filtragem de Tools

O servidor suporta tres modos para controlar quais tools sao expostas ao assistente de IA:

| Modo | Flag | Tools | Descricao |
|---|---|---|---|
| Essential | `--essential` (padrao) | ~19 | Operacoes de leitura basicas para consulta e exploracao |
| Write | `--write` | ~59 | Essential + operacoes de criacao, atualizacao e exclusao |
| All | `--all` | ~87 | Todas as tools disponiveis, incluindo operacoes avancadas |

Exemplos:

```bash
metabase-mcp                # Modo essential (padrao)
metabase-mcp --write        # Essential + tools de escrita
metabase-mcp --all          # Todas as tools
```

O modo essential e o padrao para manter a lista de tools gerenciavel e reduzir o risco de modificacoes nao intencionais. Use `--write` ou `--all` quando precisar criar ou modificar recursos no Metabase.

## Tools Disponiveis

As tools sao organizadas em cinco categorias:

- **Database** (13 tools) -- Listar, inspecionar, criar e gerenciar conexoes de banco de dados; executar queries SQL
- **Table** (17 tools) -- Navegar tabelas, inspecionar schemas, gerenciar metadados de campos, importar/exportar CSV
- **Card** (21 tools) -- CRUD de perguntas salvas, executar queries, gerenciar links publicos, mover cards
- **Dashboard** (27 tools) -- CRUD de dashboards, gerenciar cards/layout, auditoria de filtros, links publicos
- **Additional** (9 tools) -- Collections, busca, usuarios, links de playground

Veja [docs/pt-BR/tools-reference.md](docs/pt-BR/tools-reference.md) para a listagem completa de tools.

## Desenvolvimento

### Setup

```bash
git clone https://github.com/im-voracity/metabase-mcp-python.git
cd metabase-mcp-python
uv sync --group dev
```

### Testes

```bash
uv run pytest
uv run pytest -m "not integration"    # Pular testes de integracao
```

### Linting e verificacao de tipos

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

## Arquitetura

Veja [docs/pt-BR/architecture.md](docs/pt-BR/architecture.md) para uma visao detalhada da estrutura do codigo, fluxo de requisicoes e sistema de autenticacao.

## Licenca

[MIT](LICENSE)
