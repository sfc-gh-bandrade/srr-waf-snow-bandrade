# ❄️ Revisão do Snowflake Well-Architected Framework

Uma aplicação Streamlit abrangente para analisar contas Snowflake baseada nas melhores práticas do [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/).

## Visão Geral

Esta aplicação fornece insights acionáveis nos cinco pilares do Well-Architected Framework:

### 🚀 Eficiência de Performance

- Análise de utilização e eficiência de warehouses
- Tendências de performance de queries e oportunidades de otimização
- Monitoramento da saúde do clustering de tabelas
- Análise de taxa de acerto do cache de resultados
- Configuração de timeouts de warehouse
- Detecção de spillage de queries
- Monitoramento de SLO de latência (P50, P99)

**Referência de Melhores Práticas**: [Guia de Performance](https://www.snowflake.com/en/developers/guides/well-architected-framework-performance/)

### 🛡️ Confiabilidade e Resiliência

- Monitoramento do status de replicação de bancos de dados
- Análise de falhas e erros de queries
- Confiabilidade de pipelines de dados (Snowpipe)
- Monitoramento de execução de tasks

**Referência de Melhores Práticas**: [Guia de Confiabilidade](https://www.snowflake.com/en/developers/guides/well-architected-framework-reliability/)

### ⚙️ Excelência Operacional

- Configuração de monitores de recursos
- Configurações de auto-suspend/resume de warehouses
- Detecção de queries de longa duração
- Análise de padrões de execução de queries

**Referência de Melhores Práticas**: [Guia de Excelência Operacional](https://www.snowflake.com/en/developers/guides/well-architected-framework-operational-excellence/)

### 🔒 Segurança e Governança

- Rastreamento de adoção de autenticação multi-fator (MFA)
- Revisão de configuração de políticas de rede
- Monitoramento de acesso a roles privilegiados
- Políticas de mascaramento de dados e acesso a linhas
- Rastreamento de tentativas de autenticação falhadas

**Referência de Melhores Práticas**: [Guia de Segurança e Governança](https://www.snowflake.com/en/developers/guides/well-architected-framework-security-and-governance/)

### 💰 Otimização de Custos e FinOps

- Consumo de créditos por tipo de serviço
- Análise detalhada de custos de warehouses
- Tendências de custos de armazenamento e otimização
- Detecção de warehouses ociosos
- Oportunidades de otimização de armazenamento (tabelas grandes não utilizadas)
- Uso de armazenamento com Time Travel
- Uso de tabelas Iceberg (Gen2)

**Referência de Melhores Práticas**: [Guia de Otimização de Custos](https://www.snowflake.com/en/developers/guides/well-architected-framework-cost-optimization-and-finops/)

## Funcionalidades

- **Análises Visuais**: Gráficos e visualizações interativas usando Plotly
- **Recomendações Acionáveis**: Detecção automatizada de oportunidades de melhoria
- **Período de Análise Configurável**: Ajuste o intervalo de tempo (7-90 dias) para análise
- **Dados em Tempo Real**: Consulta as views `ACCOUNT_USAGE` do Snowflake para métricas atualizadas
- **Alertas Codificados por Cores**: Alertas de sucesso, aviso e críticos para fácil identificação

## Pré-requisitos

- Conta Snowflake com permissões apropriadas
- Acesso ao schema `SNOWFLAKE.ACCOUNT_USAGE` (requer `ACCOUNTADMIN` ou privilégios concedidos)
- Ambiente Snowflake Streamlit ou conexão Snowflake local

## Instalação

### Opção 1: Implantar no Snowflake (Recomendado)

1. **Criar um app Streamlit no Snowflake:**

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE <SEU_BANCO_DE_DADOS>;
USE SCHEMA <SEU_SCHEMA>;

CREATE STREAMLIT snowflake_waf_review
  ROOT_LOCATION = '@<SEU_STAGE>'
  MAIN_FILE = 'app.py'
  QUERY_WAREHOUSE = <SEU_WAREHOUSE>;
```

2. **Fazer upload dos arquivos:**

```sql
PUT file:///caminho/para/app.py @<SEU_STAGE>/app.py AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

3. **Conceder privilégios necessários:**

```sql
-- Conceder acesso ao ACCOUNT_USAGE
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <SUA_ROLE>;
```

### Opção 2: Executar Localmente

1. **Clonar o repositório:**

```bash
git clone <url-do-seu-repo>
cd snowflake-readiness-review
```

2. **Instalar dependências:**

```bash
pip install -r requirements-local.txt
```

3. **Configurar conexão Snowflake:**

Criar um arquivo `.streamlit/secrets.toml`:

```toml
[snowflake]
account = "sua_conta"
token = "seu_token_oauth"
role = "ACCOUNTADMIN"
warehouse = "seu_warehouse"
```

4. **Executar a aplicação:**

```bash
streamlit run app_local.py
```

## Permissões Necessárias

A aplicação requer acesso às seguintes views do Snowflake:

- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE`
- `SNOWFLAKE.ACCOUNT_USAGE.DATABASES`
- `SNOWFLAKE.ACCOUNT_USAGE.USERS`
- `SNOWFLAKE.ACCOUNT_USAGE.NETWORK_POLICIES`
- `SNOWFLAKE.ACCOUNT_USAGE.SESSIONS`
- `SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.RESOURCE_MONITORS`
- `SNOWFLAKE.ACCOUNT_USAGE.PIPES`
- `SNOWFLAKE.ACCOUNT_USAGE.TASKS`
- `SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES`
- `SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS`
- `SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.TABLES`

**Nota**: As views `ACCOUNT_USAGE` têm latência (45 minutos a 3 horas). Para dados em tempo real, considere usar views `INFORMATION_SCHEMA` quando aplicável.

## Uso

1. **Iniciar a aplicação** em seu ambiente Snowflake ou localmente
2. **Configurar o período de análise** usando o controle deslizante da barra lateral (7-90 dias)
3. **Navegar pelas abas** para explorar cada pilar do Well-Architected Framework
4. **Revisar recomendações** destacadas em caixas de alerta de aviso e críticos
5. **Exportar insights** tirando capturas de tela ou copiando tabelas de dados

## Métricas e Recomendações Principais

### Performance

- ✅ Tempo de fila deve ser <20% do tempo de execução
- ✅ Taxa de acerto de cache deve ser >50%
- ✅ Profundidade de clustering deve ser <3 para performance ótima
- ✅ Spillage local deve ser <5% das queries
- ✅ Spillage remoto deve ser <1% das queries
- ✅ P99 de latência deve estar dentro dos SLOs definidos

### Confiabilidade

- ✅ Habilitar replicação para bancos de dados críticos
- ✅ Monitorar e resolver erros de pipelines
- ✅ Configurar notificações de erro para tasks

### Excelência Operacional

- ✅ Configurar monitores de recursos
- ✅ Definir auto-suspend para 60-300 segundos
- ✅ Habilitar auto-resume para todos os warehouses

### Segurança e Governança

- ✅ Impor MFA para todos os usuários
- ✅ Implementar políticas de rede
- ✅ Aplicar políticas de mascaramento a dados sensíveis
- ✅ Monitorar uso de roles privilegiados

### Otimização de Custos

- ✅ Identificar e suspender warehouses ociosos
- ✅ Monitorar uso de créditos de serviços em nuvem (<10%)
- ✅ Arquivar ou excluir tabelas grandes não utilizadas
- ✅ Revisar políticas de retenção de dados
- ✅ Otimizar configurações de Time Travel
- ✅ Considerar tabelas Iceberg para grandes volumes

## Solução de Problemas

### "Não foi possível conectar ao Snowflake"

- Certifique-se de que está executando em um ambiente Snowflake Streamlit, ou
- Verifique sua configuração de conexão em `.streamlit/secrets.toml`

### "Erro ao buscar dados"

- Verifique se sua role tem `IMPORTED PRIVILEGES` no banco de dados `SNOWFLAKE`
- Verifique se a role tem acesso ao schema `ACCOUNT_USAGE`
- Algumas views podem requerer a role `ACCOUNTADMIN`

### "Nenhum dado disponível"

- Views `ACCOUNT_USAGE` têm latência (45 min - 3 horas)
- Certifique-se de que a conta esteve ativa durante o período de análise
- Tente aumentar o período de análise usando o controle deslizante da barra lateral

## Personalização

Você pode personalizar a aplicação:

1. **Ajustando limites**: Modificar limites de aviso no código (ex: % de tempo de fila, taxa de acerto de cache)
2. **Adicionando queries personalizadas**: Estender cada aba com análises adicionais específicas ao seu caso de uso
3. **Estilização**: Modificar o CSS na seção `st.markdown()` para personalização de marca
4. **Adicionando abas**: Criar novas abas para análises personalizadas ou tipos específicos de workload

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para enviar issues ou pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT.

## Suporte

Para questões ou problemas:

- Revise a [documentação do Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)
- Consulte a [documentação das views ACCOUNT_USAGE do Snowflake](https://docs.snowflake.com/en/sql-reference/account-usage.html)
- Abra uma issue neste repositório

## Agradecimentos

Construído com:

- [Snowflake](https://www.snowflake.com/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- Baseado no [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)

---

**Construído por Engenheiros de Soluções Snowflake para a Comunidade Snowflake** ❄️

