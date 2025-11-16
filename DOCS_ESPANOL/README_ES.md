# ❄️ Revisión del Snowflake Well-Architected Framework

Una aplicación Streamlit completa para analizar cuentas de Snowflake basada en las mejores prácticas del [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/).

## Descripción General

Esta aplicación proporciona información procesable en los cinco pilares del Well-Architected Framework:

### 🚀 Eficiencia de Rendimiento

- Análisis de utilización y eficiencia de warehouses
- Tendencias de rendimiento de consultas y oportunidades de optimización
- Monitoreo de la salud del clustering de tablas
- Análisis de tasa de aciertos de caché de resultados
- Configuración de timeouts de warehouse
- Detección de spillage de consultas
- Monitoreo de SLO de latencia (P50, P99)

**Referencia de Mejores Prácticas**: [Guía de Rendimiento](https://www.snowflake.com/en/developers/guides/well-architected-framework-performance/)

### 🛡️ Confiabilidad y Resiliencia

- Monitoreo del estado de replicación de bases de datos
- Análisis de fallos y errores de consultas
- Confiabilidad de pipelines de datos (Snowpipe)
- Monitoreo de ejecución de tasks

**Referencia de Mejores Prácticas**: [Guía de Confiabilidad](https://www.snowflake.com/en/developers/guides/well-architected-framework-reliability/)

### ⚙️ Excelencia Operacional

- Configuración de monitores de recursos
- Configuraciones de auto-suspend/resume de warehouses
- Detección de consultas de larga duración
- Análisis de patrones de ejecución de consultas

**Referencia de Mejores Prácticas**: [Guía de Excelencia Operacional](https://www.snowflake.com/en/developers/guides/well-architected-framework-operational-excellence/)

### 🔒 Seguridad y Gobernanza

- Seguimiento de adopción de autenticación multifactor (MFA)
- Revisión de configuración de políticas de red
- Monitoreo de acceso a roles privilegiados
- Políticas de enmascaramiento de datos y acceso a filas
- Seguimiento de intentos de autenticación fallidos

**Referencia de Mejores Prácticas**: [Guía de Seguridad y Gobernanza](https://www.snowflake.com/en/developers/guides/well-architected-framework-security-and-governance/)

### 💰 Optimización de Costos y FinOps

- Consumo de créditos por tipo de servicio
- Análisis detallado de costos de warehouses
- Tendencias de costos de almacenamiento y optimización
- Detección de warehouses inactivos
- Oportunidades de optimización de almacenamiento (tablas grandes no utilizadas)
- Uso de almacenamiento con Time Travel
- Uso de tablas Iceberg (Gen2)

**Referencia de Mejores Prácticas**: [Guía de Optimización de Costos](https://www.snowflake.com/en/developers/guides/well-architected-framework-cost-optimization-and-finops/)

## Funcionalidades

- **Análisis Visuales**: Gráficos y visualizaciones interactivas usando Plotly
- **Recomendaciones Procesables**: Detección automatizada de oportunidades de mejora
- **Período de Análisis Configurable**: Ajuste el intervalo de tiempo (7-90 días) para análisis
- **Datos en Tiempo Real**: Consulta las vistas `ACCOUNT_USAGE` de Snowflake para métricas actualizadas
- **Alertas Codificadas por Colores**: Alertas de éxito, advertencia y críticas para fácil identificación

## Requisitos Previos

- Cuenta de Snowflake con permisos apropiados
- Acceso al esquema `SNOWFLAKE.ACCOUNT_USAGE` (requiere `ACCOUNTADMIN` o privilegios otorgados)
- Entorno Snowflake Streamlit o conexión Snowflake local

## Instalación

### Opción 1: Desplegar en Snowflake (Recomendado)

1. **Crear una aplicación Streamlit en Snowflake:**

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE <SU_BASE_DE_DATOS>;
USE SCHEMA <SU_ESQUEMA>;

CREATE STREAMLIT snowflake_waf_review
  ROOT_LOCATION = '@<SU_STAGE>'
  MAIN_FILE = 'app.py'
  QUERY_WAREHOUSE = <SU_WAREHOUSE>;
```

2. **Subir los archivos:**

```sql
PUT file:///ruta/a/app.py @<SU_STAGE>/app.py AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

3. **Otorgar privilegios necesarios:**

```sql
-- Otorgar acceso a ACCOUNT_USAGE
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <SU_ROL>;
```

### Opción 2: Ejecutar Localmente

1. **Clonar el repositorio:**

```bash
git clone <url-de-su-repo>
cd snowflake-readiness-review
```

2. **Instalar dependencias:**

```bash
pip install -r requirements-local.txt
```

3. **Configurar conexión Snowflake:**

Crear un archivo `.streamlit/secrets.toml`:

```toml
[snowflake]
account = "su_cuenta"
token = "su_token_oauth"
role = "ACCOUNTADMIN"
warehouse = "su_warehouse"
```

4. **Ejecutar la aplicación:**

```bash
streamlit run app_local.py
```

## Permisos Necesarios

La aplicación requiere acceso a las siguientes vistas de Snowflake:

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

**Nota**: Las vistas `ACCOUNT_USAGE` tienen latencia (45 minutos a 3 horas). Para datos en tiempo real, considere usar vistas `INFORMATION_SCHEMA` cuando sea aplicable.

## Uso

1. **Iniciar la aplicación** en su entorno Snowflake o localmente
2. **Configurar el período de análisis** usando el control deslizante de la barra lateral (7-90 días)
3. **Navegar por las pestañas** para explorar cada pilar del Well-Architected Framework
4. **Revisar recomendaciones** destacadas en cajas de alerta de advertencia y críticas
5. **Exportar información** tomando capturas de pantalla o copiando tablas de datos

## Métricas y Recomendaciones Principales

### Rendimiento

- ✅ El tiempo de cola debe ser <20% del tiempo de ejecución
- ✅ La tasa de aciertos de caché debe ser >50%
- ✅ La profundidad de clustering debe ser <3 para rendimiento óptimo
- ✅ El spillage local debe ser <5% de las consultas
- ✅ El spillage remoto debe ser <1% de las consultas
- ✅ P99 de latencia debe estar dentro de los SLOs definidos

### Confiabilidad

- ✅ Habilitar replicación para bases de datos críticas
- ✅ Monitorear y resolver errores de pipelines
- ✅ Configurar notificaciones de error para tasks

### Excelencia Operacional

- ✅ Configurar monitores de recursos
- ✅ Definir auto-suspend a 60-300 segundos
- ✅ Habilitar auto-resume para todos los warehouses

### Seguridad y Gobernanza

- ✅ Imponer MFA para todos los usuarios
- ✅ Implementar políticas de red
- ✅ Aplicar políticas de enmascaramiento a datos sensibles
- ✅ Monitorear uso de roles privilegiados

### Optimización de Costos

- ✅ Identificar y suspender warehouses inactivos
- ✅ Monitorear uso de créditos de servicios en la nube (<10%)
- ✅ Archivar o eliminar tablas grandes no utilizadas
- ✅ Revisar políticas de retención de datos
- ✅ Optimizar configuraciones de Time Travel
- ✅ Considerar tablas Iceberg para grandes volúmenes

## Solución de Problemas

### "No se pudo conectar a Snowflake"

- Asegúrese de que está ejecutando en un entorno Snowflake Streamlit, o
- Verifique su configuración de conexión en `.streamlit/secrets.toml`

### "Error al obtener datos"

- Verifique que su rol tenga `IMPORTED PRIVILEGES` en la base de datos `SNOWFLAKE`
- Verifique que el rol tenga acceso al esquema `ACCOUNT_USAGE`
- Algunas vistas pueden requerir el rol `ACCOUNTADMIN`

### "No hay datos disponibles"

- Las vistas `ACCOUNT_USAGE` tienen latencia (45 min - 3 horas)
- Asegúrese de que la cuenta haya estado activa durante el período de análisis
- Intente aumentar el período de análisis usando el control deslizante de la barra lateral

## Personalización

Puede personalizar la aplicación:

1. **Ajustando umbrales**: Modificar umbrales de advertencia en el código (ej: % de tiempo de cola, tasa de aciertos de caché)
2. **Agregando consultas personalizadas**: Extender cada pestaña con análisis adicionales específicos a su caso de uso
3. **Estilización**: Modificar el CSS en la sección `st.markdown()` para personalización de marca
4. **Agregando pestañas**: Crear nuevas pestañas para análisis personalizados o tipos específicos de workload

## Contribuciones

¡Las contribuciones son bienvenidas! No dude en enviar issues o pull requests.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.

## Soporte

Para preguntas o problemas:

- Revise la [documentación del Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)
- Consulte la [documentación de las vistas ACCOUNT_USAGE de Snowflake](https://docs.snowflake.com/en/sql-reference/account-usage.html)
- Abra un issue en este repositorio

## Reconocimientos

Construido con:

- [Snowflake](https://www.snowflake.com/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- Basado en el [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)

---

**Construido por Ingenieros de Soluciones de Snowflake para la Comunidad Snowflake** ❄️

