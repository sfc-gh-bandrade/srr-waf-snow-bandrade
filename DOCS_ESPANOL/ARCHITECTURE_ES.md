# Descripción General de la Arquitectura

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Aplicación Streamlit                          │
│                        (app.py)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │Rendimiento │  │Confiabili- │  │ Seguridad  │  ...          │
│  │  Pestaña   │  │dad Pestaña │  │  Pestaña   │              │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘              │
│        │                │                │                      │
│        └────────────────┴────────────────┘                      │
│                         │                                       │
│                         ▼                                       │
│              ┌──────────────────────┐                          │
│              │  Ejecutor de Query   │                          │
│              │  (Sesión Snowpark)   │                          │
│              └──────────┬───────────┘                          │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │ Consultas SQL
                          ▼
        ┌─────────────────────────────────────┐
        │      Cuenta Snowflake               │
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
        │  │ • ... y más                 │  │
        │  └─────────────────────────────┘  │
        │                                     │
        └─────────────────────────────────────┘
```

## Arquitectura de Componentes

### 1. Capa de Interfaz de Usuario

```
┌──────────────────────────────────────────────────────────┐
│                  Interfaz Streamlit                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │ Barra Lateral│  • Selector de Rango (7-90 días)     │
│  │              │  • Opciones de Configuración         │
│  │              │  • Información Acerca de             │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Navegación por Pestañas                  │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ 🚀 Rendimiento | 🛡️ Confiabilidad | ⚙️ Ops | ... │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Componentes de Visualización             │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ • Gráficos Plotly (Barra, Línea, Pizza, Dispers)│  │
│  │ • Tablas de Datos (con config de columna)       │  │
│  │ • Tarjetas de Métricas (st.metric)              │  │
│  │ • Cajas de Alerta (Éxito, Advertencia, Error)   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 2. Capa de Procesamiento de Datos

```
┌──────────────────────────────────────────────────────────┐
│              Pipeline de Procesamiento de Datos          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Entrada del Usuario (Rango) ──┐                        │
│                                 │                        │
│                                 ▼                        │
│                    ┌─────────────────┐                  │
│                    │Constructor Query│                  │
│                    │ • Fechas dinámicas│                │
│                    │ • Parametrizado │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │  Ejecución SQL  │                  │
│                    │    Snowpark     │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │    Conversión   │                  │
│                    │ Pandas DataFrame│                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │  Transformación │                  │
│                    │   y Agregación  │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │ Verificación de │                  │
│                    │    Umbrales     │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                        Visualización                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 3. Arquitectura de Consultas por Pilar

#### Consultas del Pilar de Rendimiento

```
┌─────────────────────────────────────────────────┐
│      Consultas de Análisis de Rendimiento      │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. SLO de Latencia (P50, P99)                  │
│    └─> QUERY_HISTORY                           │
│        • Latencias percentiles                 │
│        • Tendencias por tipo de query          │
│                                                 │
│ 2. Utilización de Warehouse                    │
│    └─> QUERY_HISTORY                           │
│        • Total de consultas por warehouse      │
│        • Tiempo promedio de ejecución          │
│        • Porcentaje de tiempo de cola          │
│                                                 │
│ 3. Rendimiento de Query                        │
│    └─> QUERY_HISTORY                           │
│        • Tendencias de tiempo de ejecución     │
│        • Eficiencia de escaneo de particiones  │
│        • Detección de consultas lentas         │
│                                                 │
│ 4. Análisis de Clustering                      │
│    └─> AUTOMATIC_CLUSTERING_HISTORY            │
│        • Profundidad de clustering             │
│        • Solapamientos                         │
│                                                 │
│ 5. Tasa de Aciertos de Caché                   │
│    └─> QUERY_HISTORY                           │
│        • Utilización de caché de resultados    │
│        • Tendencias de aciertos de caché       │
│                                                 │
│ 6. Configuración de Timeout de Warehouse       │
│    └─> SHOW PARAMETERS FOR WAREHOUSE           │
│        • STATEMENT_TIMEOUT_IN_SECONDS          │
│        • STATEMENT_QUEUED_TIMEOUT_IN_SECONDS   │
│                                                 │
│ 7. Detección de Spillage de Query             │
│    └─> QUERY_HISTORY                           │
│        • Spillage de disco local               │
│        • Spillage de almacenamiento remoto     │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas del Pilar de Confiabilidad

```
┌─────────────────────────────────────────────────┐
│      Consultas de Análisis de Confiabilidad    │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Estado de Replicación                       │
│    └─> DATABASES                               │
│        • Replicación habilitada/deshabilitada  │
│        • Programaciones de replicación         │
│                                                 │
│ 2. Fallos de Query                             │
│    └─> QUERY_HISTORY                           │
│        • Conteo de consultas fallidas          │
│        • Mensajes de error                     │
│        • Tendencias de fallos                  │
│                                                 │
│ 3. Confiabilidad de Pipeline                   │
│    └─> PIPES                                   │
│        • Conteo de errores                     │
│        • Últimos mensajes de error             │
│                                                 │
│ 4. Confiabilidad de Task                       │
│    └─> TASKS                                   │
│        • Estado de integración de errores      │
│        • Estados de tasks                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas del Pilar de Excelencia Operacional

```
┌─────────────────────────────────────────────────┐
│ Consultas de Análisis de Excelencia Operacional│
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Monitores de Recursos                       │
│    └─> RESOURCE_MONITORS                       │
│        • Configuraciones de monitores          │
│        • Cuotas de créditos                    │
│        • Umbrales de alerta                    │
│                                                 │
│ 2. Configuración de Warehouse                  │
│    └─> WAREHOUSES                              │
│        • Configuraciones de auto-suspend       │
│        • Configuraciones de auto-resume        │
│        • Configuración multi-cluster           │
│                                                 │
│ 3. Consultas de Larga Duración                 │
│    └─> QUERY_HISTORY                           │
│        • Consultas > 5 minutos                 │
│        • Distribución de tiempo de ejecución   │
│                                                 │
│ 4. Patrones de Query                           │
│    └─> QUERY_HISTORY                           │
│        • Actividad de usuarios                 │
│        • Tipos de consulta                     │
│        • Uso de warehouse                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas del Pilar de Seguridad y Gobernanza

```
┌─────────────────────────────────────────────────┐
│ Consultas de Análisis de Seguridad y Gobernanza│
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Adopción de MFA                             │
│    └─> USERS                                   │
│        • Usuarios con MFA habilitado           │
│        • Tasa de adopción                      │
│                                                 │
│ 2. Políticas de Red                            │
│    └─> NETWORK_POLICIES                        │
│        • Configuraciones de políticas          │
│        • IPs permitidas/bloqueadas             │
│                                                 │
│ 3. Acceso Privilegiado                         │
│    └─> SESSIONS                                │
│        • Uso de ACCOUNTADMIN                   │
│        • Uso de SECURITYADMIN                  │
│        • Conteo de sesiones                    │
│                                                 │
│ 4. Enmascaramiento de Datos                    │
│    └─> POLICY_REFERENCES                       │
│        • Políticas de enmascaramiento          │
│        • Políticas de acceso a filas           │
│                                                 │
│ 5. Inicios de Sesión Fallidos                  │
│    └─> LOGIN_HISTORY                           │
│        • Intentos fallidos                     │
│        • Patrones de error                     │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Consultas del Pilar de Optimización de Costos

```
┌─────────────────────────────────────────────────┐
│  Consultas de Análisis de Optimización de Costos│
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Uso de Créditos                             │
│    └─> METERING_DAILY_HISTORY                  │
│        • Desglose por tipo de servicio         │
│        • Tendencias diarias                    │
│                                                 │
│ 2. Costos de Warehouse                         │
│    └─> WAREHOUSE_METERING_HISTORY              │
│        • Créditos de computación               │
│        • Créditos de servicios en la nube      │
│        • Costo por warehouse                   │
│                                                 │
│ 3. Costos de Almacenamiento                    │
│    └─> STORAGE_USAGE                           │
│        • Almacenamiento de base de datos       │
│        • Almacenamiento de stage               │
│        • Almacenamiento de failsafe            │
│        • Tendencias de crecimiento             │
│                                                 │
│ 4. Warehouses Inactivos                        │
│    └─> WAREHOUSES + QUERY_HISTORY              │
│        • Timestamp del último uso              │
│        • Duración de inactividad               │
│                                                 │
│ 5. Optimización de Almacenamiento              │
│    └─> TABLE_STORAGE_METRICS + ACCESS_HISTORY  │
│        • Tablas grandes no utilizadas          │
│        • Desglose de almacenamiento            │
│        • Frecuencia de acceso                  │
│                                                 │
│ 6. Uso de Almacenamiento con Time Travel       │
│    └─> TABLE_STORAGE_METRICS                   │
│        • Almacenamiento activo vs time travel  │
│        • Overhead de time travel               │
│        • Oportunidades de optimización         │
│                                                 │
│ 7. Uso de Tablas Iceberg (Gen2)               │
│    └─> TABLES                                  │
│        • Adopción de tablas Iceberg            │
│        • Distribución por base de datos        │
│        • Beneficios de rendimiento             │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Flujo de Datos

```
┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│          │     │           │     │          │     │          │
│Navegador │────▶│ Interfaz  │────▶│  Sesión  │────▶│  Cuenta  │
│ Usuario  │     │ Streamlit │     │ Snowpark │     │Snowflake │
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

### Flujo Detallado

1. **Interacción del Usuario**
   - Usuario selecciona rango de fechas vía barra lateral
   - Usuario navega a una pestaña específica de pilar

2. **Generación de Query**
   - Aplicación genera query SQL con parámetros de fecha
   - Query tiene como objetivo vistas específicas de ACCOUNT_USAGE

3. **Ejecución de Query**
   - Sesión Snowpark ejecuta SQL
   - Resultados devueltos a Snowpark

4. **Transformación de Datos**
   - Snowpark convierte a Pandas DataFrame
   - Agregación de datos y cálculos realizados
   - Umbrales verificados para alertas

5. **Visualización**
   - Plotly crea gráficos interactivos
   - Streamlit renderiza tablas
   - Cajas de alerta mostradas según umbrales

6. **Retroalimentación del Usuario**
   - Gráficos visuales mostrados
   - Recomendaciones presentadas
   - Tablas de datos disponibles para exportación

## Arquitecturas de Despliegue

### Arquitectura 1: Streamlit en Snowflake (Recomendado)

```
┌─────────────────────────────────────────────────────┐
│              Cuenta Snowflake                       │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │      Streamlit en Snowflake                │   │
│  │                                            │   │
│  │  • Integración nativa                      │   │
│  │  • Sin hospedaje externo                   │   │
│  │  • Autenticación integrada                 │   │
│  │  • Acceso directo a ACCOUNT_USAGE          │   │
│  │                                            │   │
│  └────────────────┬───────────────────────────┘   │
│                   │                                │
│                   ▼                                │
│  ┌────────────────────────────────────────────┐   │
│  │       Warehouse de Computación             │   │
│  │       (streamlit_wh - XSMALL)              │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
         ▲
         │ HTTPS
         │
    ┌────┴────┐
    │Navegador│
    │Usuarios │
    └─────────┘
```

**Pros**:
- Sin gestión de infraestructura
- Autenticación nativa de Snowflake
- Acceso directo a ACCOUNT_USAGE
- Seguro por defecto
- Sin dependencias externas

**Contras**:
- Requiere función Streamlit (puede necesitar actualización)
- Personalización limitada de hospedaje

### Arquitectura 2: Desarrollo Local

```
┌──────────────────────┐         ┌─────────────────────┐
│  Máquina Desarrollo  │         │  Cuenta Snowflake   │
│                      │         │                     │
│  ┌────────────────┐ │         │  ┌──────────────┐  │
│  │   Aplicación   │ │ HTTPS   │  │  ACCOUNT     │  │
│  │Streamlit Local │─┼─────────┼─▶│  USAGE       │  │
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

**Pros**:
- Iteración rápida de desarrollo
- Control total sobre el entorno
- Depuración más fácil

**Contras**:
- Requiere configuración local
- Necesario gestión de credenciales
- No adecuado para producción

## Arquitectura de Seguridad

```
┌─────────────────────────────────────────────────────┐
│                 Capas de Seguridad                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Autenticación                                   │
│     ├─> Autenticación de usuario Snowflake         │
│     ├─> Aplicación de MFA                          │
│     └─> Integración SSO                            │
│                                                     │
│  2. Autorización                                    │
│     ├─> Control de acceso basado en roles (RBAC)   │
│     ├─> Privilegios ACCOUNT_USAGE                  │
│     └─> Concesiones de uso de warehouse            │
│                                                     │
│  3. Seguridad de Red                                │
│     ├─> Políticas de red                           │
│     ├─> Lista de permitidos de IP                  │
│     └─> Private Link (opcional)                    │
│                                                     │
│  4. Acceso a Datos                                  │
│     ├─> Consultas de solo lectura                  │
│     ├─> Sin modificación de datos                  │
│     └─> Solo vistas ACCOUNT_USAGE                  │
│                                                     │
│  5. Seguridad de Aplicación                         │
│     ├─> Sin almacenamiento de credenciales         │
│     ├─> Autenticación basada en sesión             │
│     └─> Sanitización de entrada (Snowpark)         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Consideraciones de Rendimiento

### Estrategia de Caché

```
┌─────────────────────────────────────────────┐
│           Capas de Caché                    │
├─────────────────────────────────────────────┤
│                                             │
│  1. Caché de Sesión Streamlit              │
│     └─> @st.cache_resource                 │
│         • Conexión Snowflake               │
│         • Persiste entre ejecuciones       │
│                                             │
│  2. Caché de Resultado de Query Snowflake  │
│     └─> Caché automático de 24 horas       │
│         • Consultas idénticas reutilizan   │
│         • Sin costo de computación         │
│                                             │
│  3. Latencia de Vista ACCOUNT_USAGE        │
│     └─> Retraso de 45 min - 3 horas        │
│         • Inherente al diseño del sistema  │
│         • Consistencia de datos garantizada│
│                                             │
└─────────────────────────────────────────────┘
```

### Optimización de Query

- Usar filtros de fecha para limitar datos escaneados
- Agregar antes de devolver a Streamlit
- Limitar conjuntos de resultados (consultas TOP N)
- Usar índices apropiados en vistas ACCOUNT_USAGE (automático)

## Escalabilidad

La aplicación escala naturalmente con Snowflake:

- **Dimensionamiento de Warehouse**: Ajustar warehouse de consulta según volumen de datos
- **Usuarios Concurrentes**: Snowflake maneja múltiples conexiones simultáneas
- **Crecimiento de Datos**: Vistas ACCOUNT_USAGE manejan cualquier tamaño de cuenta
- **Rendimiento de Query**: Computación elástica escala con la carga de trabajo

## Monitoreo y Observabilidad

```
┌─────────────────────────────────────────────┐
│        Monitoreo de Aplicación             │
├─────────────────────────────────────────────┤
│                                             │
│  1. Rendimiento de Query                   │
│     └─> QUERY_HISTORY rastrea queries app │
│                                             │
│  2. Uso de Warehouse                       │
│     └─> Monitorear créditos streamlit_wh  │
│                                             │
│  3. Rastreo de Errores                     │
│     └─> Registros de error Streamlit      │
│                                             │
│  4. Acceso de Usuario                      │
│     └─> SESSION_HISTORY                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Stack de Tecnología

| Capa | Tecnología | Versión |
|------|-----------|---------|
| **Frontend** | Streamlit | ≥1.28.0 |
| **Visualización** | Plotly | ≥5.17.0 |
| **Procesamiento de Datos** | Pandas | ≥2.0.0 |
| **Conector de Base de Datos** | Snowflake Snowpark | ≥1.11.1 |
| **Base de Datos** | Snowflake | Cualquier edición |
| **Lenguaje** | Python | ≥3.8 |

---

## Principios de Diseño

1. **Simplicidad**: Aplicación de archivo único para despliegue fácil
2. **Seguridad**: Consultas de solo lectura, sin modificación de datos
3. **Rendimiento**: Consultas eficientes con filtrado de fecha
4. **Usabilidad**: Visualizaciones claras y recomendaciones procesables
5. **Mantenibilidad**: Código bien documentado y estructura modular
6. **Escalabilidad**: Aprovecha la computación elástica de Snowflake
7. **Confiabilidad**: Manejo de errores para degradación elegante

---

**Última Actualización**: 16 de Noviembre, 2025

