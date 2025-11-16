# Visão Geral da Arquitetura

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Aplicação Streamlit                           │
│                        (app.py)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ Performance│  │Confiabili- │  │ Segurança  │  ...          │
│  │    Aba     │  │  dade Aba  │  │    Aba     │              │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘              │
│        │                │                │                      │
│        └────────────────┴────────────────┘                      │
│                         │                                       │
│                         ▼                                       │
│              ┌──────────────────────┐                          │
│              │  Executor de Query   │                          │
│              │  (Sessão Snowpark)   │                          │
│              └──────────┬───────────┘                          │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │ Consultas SQL
                          ▼
        ┌─────────────────────────────────────┐
        │      Conta Snowflake                │
        ├─────────────────────────────────────┤
        │                                     │
        │  ┌─────────────────────────────┐  │
        │  │  Schema ACCOUNT_USAGE       │  │
        │  ├─────────────────────────────┤  │
        │  │ • QUERY_HISTORY             │  │
        │  │ • WAREHOUSE_METERING        │  │
        │  │ • STORAGE_USAGE             │  │
        │  │ • DATABASES                 │  │
        │  │ • WAREHOUSES                │  │
        │  │ • USERS                     │  │
        │  │ • LOGIN_HISTORY             │  │
        │  │ • SESSIONS                  │  │
        │  │ • RESOURCE_MONITORS         │  │
        │  │ • PIPES                     │  │
        │  │ • TASKS                     │  │
        │  │ • POLICY_REFERENCES         │  │
        │  │ • ACCESS_HISTORY            │  │
        │  │ • TABLE_STORAGE_METRICS     │  │
        │  │ • ... e mais                │  │
        │  └─────────────────────────────┘  │
        │                                     │
        └─────────────────────────────────────┘
```

## Arquitetura de Componentes

### 1. Camada de Interface do Usuário

```
┌──────────────────────────────────────────────────────────┐
│                    Interface Streamlit                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │ Barra Lateral│  • Seletor de Intervalo (7-90 dias)  │
│  │              │  • Opções de Configuração            │
│  │              │  • Informações Sobre                 │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Navegação por Abas                    │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ 🚀 Performance | 🛡️ Confiabilidade | ⚙️ Ops | ... │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Componentes de Visualização              │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ • Gráficos Plotly (Barra, Linha, Pizza, Dispers)│  │
│  │ • Tabelas de Dados (com config de coluna)       │  │
│  │ • Cartões de Métricas (st.metric)               │  │
│  │ • Caixas de Alerta (Sucesso, Aviso, Erro)       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 2. Camada de Processamento de Dados

```
┌──────────────────────────────────────────────────────────┐
│              Pipeline de Processamento de Dados          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Entrada do Usuário (Intervalo) ──┐                     │
│                                    │                     │
│                                    ▼                     │
│                    ┌─────────────────┐                  │
│                    │Construtor Query │                  │
│                    │ • Datas dinâmicas│                 │
│                    │ • Parametrizado │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │  Execução SQL   │                  │
│                    │    Snowpark     │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │    Conversão    │                  │
│                    │ Pandas DataFrame│                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │  Transformação  │                  │
│                    │   e Agregação   │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │ Verificação de  │                  │
│                    │    Limites      │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                        Visualização                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 3. Arquitetura de Consultas por Pilar

#### Consultas do Pilar de Performance

```
┌─────────────────────────────────────────────────┐
│      Consultas de Análise de Performance       │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. SLO de Latência (P50, P99)                 │
│    └─> QUERY_HISTORY                           │
│        • Latências percentis                   │
│        • Tendências por tipo de query          │
│                                                 │
│ 2. Utilização de Warehouse                     │
│    └─> QUERY_HISTORY                           │
│        • Total de queries por warehouse        │
│        • Tempo médio de execução               │
│        • Porcentagem de tempo de fila          │
│                                                 │
│ 3. Performance de Query                        │
│    └─> QUERY_HISTORY                           │
│        • Tendências de tempo de execução       │
│        • Eficiência de scan de partições       │
│        • Detecção de queries lentas            │
│                                                 │
│ 4. Análise de Clustering                       │
│    └─> AUTOMATIC_CLUSTERING_HISTORY            │
│        • Profundidade de clustering            │
│        • Sobreposições                         │
│                                                 │
│ 5. Taxa de Acerto de Cache                     │
│    └─> QUERY_HISTORY                           │
│        • Utilização de cache de resultados     │
│        • Tendências de acerto de cache         │
│                                                 │
│ 6. Configuração de Timeout de Warehouse        │
│    └─> SHOW PARAMETERS FOR WAREHOUSE           │
│        • STATEMENT_TIMEOUT_IN_SECONDS          │
│        • STATEMENT_QUEUED_TIMEOUT_IN_SECONDS   │
│                                                 │
│ 7. Detecção de Spillage de Query              │
│    └─> QUERY_HISTORY                           │
│        • Spillage de disco local               │
│        • Spillage de armazenamento remoto      │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas do Pilar de Confiabilidade

```
┌─────────────────────────────────────────────────┐
│      Consultas de Análise de Confiabilidade    │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Status de Replicação                        │
│    └─> DATABASES                               │
│        • Replicação habilitada/desabilitada    │
│        • Agendamentos de replicação            │
│                                                 │
│ 2. Falhas de Query                             │
│    └─> QUERY_HISTORY                           │
│        • Contagem de queries falhadas          │
│        • Mensagens de erro                     │
│        • Tendências de falhas                  │
│                                                 │
│ 3. Confiabilidade de Pipeline                  │
│    └─> PIPES                                   │
│        • Contagem de erros                     │
│        • Últimas mensagens de erro             │
│                                                 │
│ 4. Confiabilidade de Task                      │
│    └─> TASKS                                   │
│        • Status de integração de erros         │
│        • Estados de tasks                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas do Pilar de Excelência Operacional

```
┌─────────────────────────────────────────────────┐
│ Consultas de Análise de Excelência Operacional │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Monitores de Recursos                       │
│    └─> RESOURCE_MONITORS                       │
│        • Configurações de monitores            │
│        • Quotas de créditos                    │
│        • Limites de alerta                     │
│                                                 │
│ 2. Configuração de Warehouse                   │
│    └─> WAREHOUSES                              │
│        • Configurações de auto-suspend         │
│        • Configurações de auto-resume          │
│        • Configuração multi-cluster            │
│                                                 │
│ 3. Queries de Longa Duração                    │
│    └─> QUERY_HISTORY                           │
│        • Queries > 5 minutos                   │
│        • Distribuição de tempo de execução     │
│                                                 │
│ 4. Padrões de Query                            │
│    └─> QUERY_HISTORY                           │
│        • Atividade de usuários                 │
│        • Tipos de query                        │
│        • Uso de warehouse                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas do Pilar de Segurança e Governança

```
┌─────────────────────────────────────────────────┐
│ Consultas de Análise de Segurança e Governança │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Adoção de MFA                               │
│    └─> USERS                                   │
│        • Usuários com MFA habilitado           │
│        • Taxa de adoção                        │
│                                                 │
│ 2. Políticas de Rede                           │
│    └─> NETWORK_POLICIES                        │
│        • Configurações de políticas            │
│        • IPs permitidos/bloqueados             │
│                                                 │
│ 3. Acesso Privilegiado                         │
│    └─> SESSIONS                                │
│        • Uso de ACCOUNTADMIN                   │
│        • Uso de SECURITYADMIN                  │
│        • Contagem de sessões                   │
│                                                 │
│ 4. Mascaramento de Dados                       │
│    └─> POLICY_REFERENCES                       │
│        • Políticas de mascaramento             │
│        • Políticas de acesso a linhas          │
│                                                 │
│ 5. Logins Falhados                             │
│    └─> LOGIN_HISTORY                           │
│        • Tentativas falhadas                   │
│        • Padrões de erro                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas do Pilar de Otimização de Custos

```
┌─────────────────────────────────────────────────┐
│  Consultas de Análise de Otimização de Custos  │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Uso de Créditos                             │
│    └─> METERING_DAILY_HISTORY                  │
│        • Detalhamento por tipo de serviço      │
│        • Tendências diárias                    │
│                                                 │
│ 2. Custos de Warehouse                         │
│    └─> WAREHOUSE_METERING_HISTORY              │
│        • Créditos de computação                │
│        • Créditos de serviços em nuvem         │
│        • Custo por warehouse                   │
│                                                 │
│ 3. Custos de Armazenamento                     │
│    └─> STORAGE_USAGE                           │
│        • Armazenamento de banco de dados       │
│        • Armazenamento de stage                │
│        • Armazenamento de failsafe             │
│        • Tendências de crescimento             │
│                                                 │
│ 4. Warehouses Ociosos                          │
│    └─> WAREHOUSES + QUERY_HISTORY              │
│        • Timestamp do último uso               │
│        • Duração de inatividade                │
│                                                 │
│ 5. Otimização de Armazenamento                 │
│    └─> TABLE_STORAGE_METRICS + ACCESS_HISTORY  │
│        • Tabelas grandes não utilizadas        │
│        • Detalhamento de armazenamento         │
│        • Frequência de acesso                  │
│                                                 │
│ 6. Uso de Armazenamento com Time Travel        │
│    └─> TABLE_STORAGE_METRICS                   │
│        • Armazenamento ativo vs time travel    │
│        • Overhead de time travel               │
│        • Oportunidades de otimização           │
│                                                 │
│ 7. Uso de Tabelas Iceberg (Gen2)              │
│    └─> TABLES                                  │
│        • Adoção de tabelas Iceberg             │
│        • Distribuição por banco de dados       │
│        • Benefícios de performance             │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Fluxo de Dados

```
┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│          │     │           │     │          │     │          │
│ Navegador│────▶│ Interface │────▶│ Sessão   │────▶│  Conta   │
│  Usuário │     │ Streamlit │     │ Snowpark │     │Snowflake │
│          │     │           │     │          │     │          │
└──────────┘     └───────────┘     └──────────┘     └──────────┘
     ▲                                                    │
     │                                                    │
     │           ┌───────────┐     ┌──────────┐         │
     │           │           │     │          │         │
     └───────────│ Gráficos  │◀────│  Pandas  │◀────────┘
                 │  Plotly   │     │DataFrame │
                 │           │     │          │
                 └───────────┘     └──────────┘
```

### Fluxo Detalhado

1. **Interação do Usuário**
   - Usuário seleciona intervalo de datas via barra lateral
   - Usuário navega para uma aba específica de pilar

2. **Geração de Query**
   - Aplicação gera query SQL com parâmetros de data
   - Query tem como alvo views específicas do ACCOUNT_USAGE

3. **Execução de Query**
   - Sessão Snowpark executa SQL
   - Resultados retornados ao Snowpark

4. **Transformação de Dados**
   - Snowpark converte para Pandas DataFrame
   - Agregação de dados e cálculos realizados
   - Limites verificados para alertas

5. **Visualização**
   - Plotly cria gráficos interativos
   - Streamlit renderiza tabelas
   - Caixas de alerta exibidas com base em limites

6. **Feedback do Usuário**
   - Gráficos visuais exibidos
   - Recomendações mostradas
   - Tabelas de dados disponíveis para exportação

## Arquiteturas de Implantação

### Arquitetura 1: Streamlit no Snowflake (Recomendado)

```
┌─────────────────────────────────────────────────────┐
│              Conta Snowflake                        │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │      Streamlit no Snowflake                │   │
│  │                                            │   │
│  │  • Integração nativa                       │   │
│  │  • Sem hospedagem externa                  │   │
│  │  • Autenticação integrada                  │   │
│  │  • Acesso direto ao ACCOUNT_USAGE          │   │
│  │                                            │   │
│  └────────────────┬───────────────────────────┘   │
│                   │                                │
│                   ▼                                │
│  ┌────────────────────────────────────────────┐   │
│  │       Warehouse de Computação              │   │
│  │       (streamlit_wh - XSMALL)              │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
         ▲
         │ HTTPS
         │
    ┌────┴────┐
    │Navegador│
    │Usuários │
    └─────────┘
```

**Prós**:
- Sem gerenciamento de infraestrutura
- Autenticação nativa do Snowflake
- Acesso direto ao ACCOUNT_USAGE
- Seguro por padrão
- Sem dependências externas

**Contras**:
- Requer recurso Streamlit (pode precisar de upgrade)
- Personalização limitada de hospedagem

### Arquitetura 2: Desenvolvimento Local

```
┌──────────────────────┐         ┌─────────────────────┐
│  Máquina Desenvolv.  │         │  Conta Snowflake    │
│                      │         │                     │
│  ┌────────────────┐ │         │  ┌──────────────┐  │
│  │   Aplicação    │ │ HTTPS   │  │  ACCOUNT     │  │
│  │ Streamlit Local│─┼─────────┼─▶│  USAGE       │  │
│  │                │ │  Auth   │  │              │  │
│  └────────────────┘ │         │  └──────────────┘  │
│         ▲            │         │                     │
│         │            │         └─────────────────────┘
│    ┌────┴────┐      │
│    │localhost│      │
│    │  :8501  │      │
│    └─────────┘      │
│                      │
└──────────────────────┘
```

**Prós**:
- Iteração rápida de desenvolvimento
- Controle total sobre o ambiente
- Depuração mais fácil

**Contras**:
- Requer configuração local
- Necessário gerenciamento de credenciais
- Não adequado para produção

## Arquitetura de Segurança

```
┌─────────────────────────────────────────────────────┐
│                 Camadas de Segurança                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Autenticação                                    │
│     ├─> Autenticação de usuário Snowflake          │
│     ├─> Aplicação de MFA                           │
│     └─> Integração SSO                             │
│                                                     │
│  2. Autorização                                     │
│     ├─> Controle de acesso baseado em role (RBAC)  │
│     ├─> Privilégios ACCOUNT_USAGE                  │
│     └─> Concessões de uso de warehouse             │
│                                                     │
│  3. Segurança de Rede                               │
│     ├─> Políticas de rede                          │
│     ├─> Lista de permissões de IP                  │
│     └─> Private Link (opcional)                    │
│                                                     │
│  4. Acesso a Dados                                  │
│     ├─> Queries somente leitura                    │
│     ├─> Sem modificação de dados                   │
│     └─> Somente views ACCOUNT_USAGE                │
│                                                     │
│  5. Segurança de Aplicação                          │
│     ├─> Sem armazenamento de credenciais           │
│     ├─> Autenticação baseada em sessão             │
│     └─> Sanitização de entrada (Snowpark)          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Considerações de Performance

### Estratégia de Cache

```
┌─────────────────────────────────────────────┐
│           Camadas de Cache                  │
├─────────────────────────────────────────────┤
│                                             │
│  1. Cache de Sessão Streamlit              │
│     └─> @st.cache_resource                 │
│         • Conexão Snowflake                │
│         • Persiste entre execuções         │
│                                             │
│  2. Cache de Resultado de Query Snowflake  │
│     └─> Cache automático de 24 horas       │
│         • Queries idênticas reutilizam     │
│         • Sem custo de computação          │
│                                             │
│  3. Latência de View ACCOUNT_USAGE         │
│     └─> Atraso de 45 min - 3 horas         │
│         • Inerente ao design do sistema    │
│         • Consistência de dados garantida  │
│                                             │
└─────────────────────────────────────────────┘
```

### Otimização de Query

- Usar filtros de data para limitar dados escaneados
- Agregar antes de retornar ao Streamlit
- Limitar conjuntos de resultados (queries TOP N)
- Usar índices apropriados em views ACCOUNT_USAGE (automático)

## Escalabilidade

A aplicação escala naturalmente com o Snowflake:

- **Dimensionamento de Warehouse**: Ajustar warehouse de query com base no volume de dados
- **Usuários Concorrentes**: Snowflake lida com múltiplas conexões simultâneas
- **Crescimento de Dados**: Views ACCOUNT_USAGE lidam com qualquer tamanho de conta
- **Performance de Query**: Computação elástica escala com a carga de trabalho

## Monitoramento e Observabilidade

```
┌─────────────────────────────────────────────┐
│        Monitoramento de Aplicação          │
├─────────────────────────────────────────────┤
│                                             │
│  1. Performance de Query                   │
│     └─> QUERY_HISTORY rastreia queries app│
│                                             │
│  2. Uso de Warehouse                       │
│     └─> Monitorar créditos streamlit_wh   │
│                                             │
│  3. Rastreamento de Erros                  │
│     └─> Logs de erro Streamlit            │
│                                             │
│  4. Acesso de Usuário                      │
│     └─> SESSION_HISTORY                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Stack de Tecnologia

| Camada | Tecnologia | Versão |
|--------|-----------|---------|
| **Frontend** | Streamlit | ≥1.28.0 |
| **Visualização** | Plotly | ≥5.17.0 |
| **Processamento de Dados** | Pandas | ≥2.0.0 |
| **Conector de Banco** | Snowflake Snowpark | ≥1.11.1 |
| **Banco de Dados** | Snowflake | Qualquer edição |
| **Linguagem** | Python | ≥3.8 |

---

## Princípios de Design

1. **Simplicidade**: Aplicação em arquivo único para implantação fácil
2. **Segurança**: Queries somente leitura, sem modificação de dados
3. **Performance**: Queries eficientes com filtragem de data
4. **Usabilidade**: Visualizações claras e recomendações acionáveis
5. **Manutenibilidade**: Código bem documentado e estrutura modular
6. **Escalabilidade**: Aproveita a computação elástica do Snowflake
7. **Confiabilidade**: Tratamento de erros para degradação elegante

---

**Última Atualização**: 16 de Novembro, 2025

