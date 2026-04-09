# Arquitetura

## Visao Geral dos Componentes

```
+------------------+     +------------------+     +----------------+     +------------------+
|                  |     |                  |     |                |     |                  |
|  MetabaseConfig  +---->+  MetabaseClient  +---->+  Tool modules  +---->+  FastMCP Server  |
|  (config.py)     |     |  (client.py)     |     |  (tools/*.py)  |     |  (server.py)     |
|                  |     |                  |     |                |     |                  |
+------------------+     +------------------+     +----------------+     +------------------+
       |                        |                        |                        |
  Env vars / .env         httpx.AsyncClient        @mcp.tool()              stdio transport
  pydantic-settings       MetabaseAuth             Tool filtering           MCP protocol
```

### MetabaseConfig (`src/metabase_mcp/config.py`)

Carrega a configuracao a partir de variaveis de ambiente usando `pydantic-settings`. Valida que `METABASE_URL` e uma URL bem formada e que uma chave de API ou credenciais de usuario/senha foram fornecidas.

### MetabaseClient (`src/metabase_mcp/client.py`)

Client HTTP assincrono que encapsula a API REST do Metabase. Usa `httpx.AsyncClient` com um handler customizado `MetabaseAuth`. Fornece metodos tipados para cada endpoint suportado da API (dashboards, cards, databases, tables, collections, users, permissions, activity).

### Tool Modules (`src/metabase_mcp/tools/`)

Cada modulo registra um grupo de tools MCP via decoradores `@mcp.tool()`:

- `database.py` -- Conexoes de banco de dados, queries, inspecao de schema
- `table.py` -- Metadados de tabelas, operacoes de campos, importacao/exportacao CSV
- `card.py` -- CRUD de perguntas salvas, execucao, links publicos
- `dashboard.py` -- CRUD de dashboards, layout de cards, auditoria de filtros
- `additional.py` -- Collections, busca, usuarios, links de playground

### FastMCP Server (`src/metabase_mcp/server.py`)

Cria a instancia `FastMCP`, inicializa o client e registra todas as tools. A filtragem de tools e aplicada apos o registro, removendo as tools que nao correspondem ao modo selecionado.

### Entry Point (`src/metabase_mcp/__main__.py`)

Faz o parsing dos argumentos CLI (`--essential`, `--write`, `--all`), cria o server e o inicia com transporte stdio.

## Fluxo de Requisicao

```
MCP Client (Claude, etc.)
    |
    |  MCP protocol (stdio)
    v
FastMCP Server
    |
    |  Roteia para a funcao de tool registrada
    v
Funcao de tool (ex: list_dashboards)
    |
    |  Chama metodo do client
    v
MetabaseClient._request()
    |
    |  httpx.AsyncClient com MetabaseAuth
    v
Metabase REST API
```

1. O client MCP envia uma requisicao de chamada de tool via stdio.
2. O FastMCP despacha a chamada para a funcao de tool correspondente.
3. A funcao de tool chama o metodo apropriado do `MetabaseClient`.
4. `MetabaseClient._request()` envia a requisicao HTTP via `httpx.AsyncClient`.
5. `MetabaseAuth` injeta o header de autenticacao (chave de API ou token de sessao).
6. A resposta e parseada, verificada quanto a erros e retornada como JSON.

## Autenticacao

A autenticacao e gerenciada pelo `MetabaseAuth`, uma subclasse de `httpx.Auth` que implementa o generator `auth_flow()`:

- **Chave de API**: Define o header `X-API-Key` em cada requisicao. Sem round-trips adicionais.
- **Token de sessao**: Na primeira requisicao, faz yield de uma sub-requisicao para `POST /api/session` com usuario/senha. O token de sessao retornado e armazenado em cache e definido como `X-Metabase-Session` nas requisicoes subsequentes.

Isso substitui o padrao de request interceptor do axios da implementacao original em TypeScript. A abordagem `httpx.Auth` e idiomatica em Python e permite que o httpx gerencie o fluxo de autenticacao de forma transparente.

### Tratamento de Redirecionamentos

`MetabaseClient._request()` trata redirecionamentos HTTP-para-HTTPS manualmente (ate 3 saltos) para preservar o metodo HTTP original. O comportamento padrao `follow_redirects` do httpx converte POST/PUT em GET em redirecionamentos 301/302, o que quebra chamadas de API.

## Filtragem de Tools

O registro de tools (`src/metabase_mcp/tools/__init__.py`) define tres conjuntos:

- **ESSENTIAL_TOOLS**: ~19 tools core somente leitura para consulta e exploracao.
- **WRITE_TOOLS**: ~40 tools adicionais que criam, atualizam ou excluem recursos.
- **Todas as tools**: O conjunto completo de ~87 tools em todos os modulos.

A filtragem funciona registrando todas as tools primeiro e depois removendo aquelas que nao correspondem ao modo selecionado. Essa abordagem evita logica condicional dentro de cada modulo de tools.

| Modo | Inclui |
|---|---|
| `essential` | Apenas tools em `ESSENTIAL_TOOLS` |
| `write` | Tools em `ESSENTIAL_TOOLS` + `WRITE_TOOLS` |
| `all` | Todas as tools registradas |

## Adicionando Novas Tools

1. Identifique o endpoint da API do Metabase e adicione um metodo ao `MetabaseClient` em `client.py`.
2. Crie a funcao de tool no modulo apropriado em `tools/` usando `@mcp.tool()`.
3. Se a tool deve estar disponivel no modo essential ou write, adicione seu nome ao conjunto correspondente em `tools/__init__.py`.
4. Adicione testes em `tests/tools/`.

### Convencoes para funcoes de tool

- Use `Annotated[type, Field(description="...")]` para todos os parametros.
- Defina `annotations=ToolAnnotations(readOnlyHint=True)` para operacoes de leitura, `readOnlyHint=False` para escritas, e adicione `destructiveHint=True` para exclusoes.
- Retorne `json.dumps(result, indent=2)` como string.
- Use validadores de `validators.py` (`JsonParsed`, `JsonParsedList`, `parse_if_string`) para parametros que podem chegar como JSON strings.
