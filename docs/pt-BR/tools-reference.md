# Referencia de Tools

Listagem completa de todas as 87 tools MCP, organizadas por categoria. A disponibilidade de cada tool depende do [modo de filtragem](../../README.pt-BR.md#modos-de-filtragem-de-tools) selecionado.

**Legenda**: E = essential, W = write, A = all-only

## Database (13 tools)

| Tool | Modo | Descricao |
|---|---|---|
| `list_databases` | E | Recuperar todas as conexoes de banco de dados no Metabase |
| `get_database` | E | Recuperar informacoes detalhadas sobre um banco de dados especifico |
| `execute_query` | E | Executar uma query SQL nativa em um banco de dados |
| `create_database` | W | Adicionar uma nova conexao de banco de dados ao Metabase |
| `update_database` | W | Atualizar configuracao do banco (nome, conexao, sincronizacao) |
| `delete_database` | W | Remover permanentemente um banco de dados do Metabase |
| `validate_database` | A | Testar parametros de conexao antes de criar |
| `add_sample_database` | W | Adicionar o banco de dados de exemplo embutido do Metabase |
| `check_database_health` | A | Verificar a saude de uma conexao de banco de dados |
| `get_database_metadata` | A | Recuperar metadados abrangentes (tabelas, campos, relacionamentos) |
| `list_database_schemas` | A | Recuperar todos os nomes de schema em um banco de dados |
| `get_database_schema` | A | Recuperar informacoes detalhadas sobre um schema especifico |
| `sync_database_schema` | W | Iniciar sincronizacao de schema para atualizar o cache de metadados |

## Table (17 tools)

| Tool | Modo | Descricao |
|---|---|---|
| `list_tables` | E | Recuperar todas as tabelas com filtragem opcional por ID |
| `get_table` | E | Recuperar informacoes completas da tabela incluindo schema e campos |
| `get_field_id` | E | Buscar o ID e metadados de um campo por tabela e nome da coluna |
| `get_table_data` | E | Recuperar dados de amostra de uma tabela para preview |
| `update_tables` | W | Atualizar multiplas tabelas em lote com a mesma configuracao |
| `update_table` | W | Atualizar nome de exibicao, descricao e configuracoes de uma tabela |
| `get_table_fks` | A | Recuperar relacionamentos de chave estrangeira de uma tabela |
| `get_table_query_metadata` | A | Recuperar metadados de tabela otimizados para queries |
| `get_table_related` | A | Encontrar tabelas e entidades relacionadas |
| `get_card_table_fks` | A | Recuperar chaves estrangeiras da tabela virtual de um card |
| `get_card_table_query_metadata` | A | Recuperar metadados de query da tabela virtual de um card |
| `append_csv_to_table` | W | Adicionar novas linhas de conteudo CSV a uma tabela existente |
| `discard_table_field_values` | W | Limpar valores de campo em cache para forcar recarregamento |
| `reorder_table_fields` | W | Alterar a ordem de exibicao dos campos da tabela |
| `replace_table_csv` | W | Substituir completamente os dados da tabela com novo conteudo CSV |
| `rescan_table_field_values` | W | Disparar re-escaneamento para atualizar cache de valores de campo |
| `sync_table_schema` | W | Iniciar sincronizacao de schema para uma tabela especifica |

## Card (21 tools)

| Tool | Modo | Descricao |
|---|---|---|
| `list_cards` | E | Recuperar todos os cards com filtragem opcional por tipo de fonte |
| `get_card` | E | Obter metadados e configuracao completos de um card especifico |
| `execute_card` | E | Executar a query de um card e retornar os dados resultantes |
| `get_card_dashboards` | E | Encontrar todos os dashboards que incluem um card especifico |
| `create_card` | W | Criar um novo card com query e visualizacao customizadas |
| `update_card` | W | Modificar nome, query, visualizacao ou configuracoes de um card |
| `delete_card` | W | Remover um card (arquivar ou exclusao permanente) |
| `copy_card` | W | Criar uma copia duplicada de um card existente |
| `move_cards` | W | Realocar multiplos cards para uma collection ou dashboard diferente |
| `move_cards_to_collection` | W | Transferir multiplos cards em lote para uma collection especifica |
| `create_card_public_link` | W | Gerar uma URL publicamente acessivel para um card |
| `delete_card_public_link` | W | Remover acesso publico a um card |
| `export_card_result` | A | Executar um card e exportar resultados em formato especifico (CSV, XLSX, JSON) |
| `list_embeddable_cards` | A | Recuperar todos os cards configurados para embedding |
| `list_public_cards` | A | Recuperar todos os cards com URLs publicas habilitadas |
| `execute_pivot_card_query` | A | Executar um card com formatacao de tabela pivot |
| `get_card_param_values` | A | Recuperar valores disponiveis para um parametro de card |
| `search_card_param_values` | A | Pesquisar e filtrar valores de parametros disponiveis |
| `get_card_param_remapping` | A | Recuperar como valores de parametro sao remapeados para exibicao |
| `get_card_query_metadata` | A | Recuperar metadados estruturais sobre a query de um card |
| `get_card_series` | A | Recuperar dados de series temporais ou sugestoes de cards relacionados |

## Dashboard (27 tools)

| Tool | Modo | Descricao |
|---|---|---|
| `list_dashboards` | E | Recuperar todos os dashboards |
| `get_dashboard` | E | Recuperar informacoes detalhadas sobre um dashboard especifico |
| `get_dashboard_cards` | E | Recuperar todos os cards dentro de um dashboard especifico |
| `create_dashboard` | E/W | Criar um novo dashboard |
| `create_public_link` | W | Gerar uma URL publicamente acessivel para um dashboard |
| `copy_dashboard` | W | Criar uma copia de um dashboard existente com todos os cards |
| `add_card_to_dashboard` | W | Adicionar um card existente a um dashboard |
| `add_text_block` | W | Adicionar um bloco de texto ou titulo a um dashboard |
| `update_dashboard` | W | Atualizar propriedades do dashboard (nome, descricao, parametros) |
| `update_dashboard_cards` | W | Substituir todos os cards do dashboard (destrutivo) |
| `update_dashcard` | W | Atualizar propriedades de um dashcard especifico |
| `delete_dashboard` | W | Excluir ou arquivar um dashboard |
| `delete_public_link` | W | Remover acesso por URL publica de um dashboard |
| `remove_cards_from_dashboard` | W | Remover dashcards especificos de um dashboard |
| `favorite_dashboard` | W | Marcar um dashboard como favorito |
| `unfavorite_dashboard` | W | Remover um dashboard dos favoritos |
| `revert_dashboard` | W | Restaurar um dashboard para uma revisao anterior |
| `save_dashboard` | W | Salvar um objeto de dashboard completo |
| `save_dashboard_to_collection` | W | Salvar um dashboard em uma collection especifica |
| `get_dashboard_related` | A | Recuperar entidades relacionadas a um dashboard |
| `get_dashboard_revisions` | A | Recuperar historico de revisoes de um dashboard |
| `list_embeddable_dashboards` | A | Recuperar todos os dashboards configurados para embedding |
| `list_public_dashboards` | A | Recuperar todos os dashboards com URLs publicas habilitadas |
| `search_dashboards` | A | Pesquisar dashboards por nome ou descricao |
| `execute_dashboard_card` | A | Executar um card especifico de um dashboard |
| `get_dashboard_queries` | A | Extrair todas as queries de um dashboard com nomes resolvidos |
| `audit_dashboard_filters` | A | Analisar conexoes de filtros para encontrar configuracoes incorretas |

## Additional (9 tools)

| Tool | Modo | Descricao |
|---|---|---|
| `list_collections` | E | Recuperar todas as collections |
| `get_collection_items` | E | Recuperar todos os itens dentro de uma collection |
| `search_content` | E | Pesquisar em todo o conteudo do Metabase |
| `get_metabase_playground_link` | E | Gerar um link de playground do Metabase para exploracao interativa |
| `create_collection` | W | Criar uma nova collection |
| `update_collection` | W | Atualizar propriedades de uma collection |
| `delete_collection` | W | Excluir permanentemente uma collection |
| `move_to_collection` | W | Mover um card ou dashboard para uma collection diferente |
| `list_users` | A | Recuperar todos os usuarios do Metabase com funcoes e permissoes |
