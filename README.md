# Balidator
Este repositorio incluye un ejemplo sencillo de calculadora de rendimiento en Tkinter 
y un proyecto de *OEE* local basado en **FastAPI**.

## Estructura

```
backend/   # Código backend con FastAPI
frontend/  # Plantillas HTML mínimas
config/    # Archivos de configuración
data/      # Base de datos SQLite y buffer JSON
```

Para ejecutar el API localmente:

```bash
uvicorn backend.main:app --reload
```

Opcionalmente se puede iniciar la pila completa (API + InfluxDB + Grafana) con:

```bash
docker compose up
```

Las variables de configuración (claves JWT, conexión a InfluxDB, etc.) se encuentran en `.env` (copiar el archivo `.env.example`).

Variables principales:

```
JWT_SECRET=changeme
JWT_ALGORITHM=HS256
ACQUISITION_INTERVAL_SECONDS=5
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=my-token
INFLUXDB_ORG=oee
INFLUXDB_BUCKET=oee
GRAFANA_USER=admin
 GRAFANA_PASSWORD=admin
```

El sistema implementa *store & forward*: si InfluxDB no está disponible, las
mediciones se guardan con timestamp en `data/buffer/buffer.json` y se reenvían
cuando la conexión regresa.

Para visualizar datos en Grafana:
1. Inicie la pila con `docker compose up`.
2. Acceda a `http://localhost:3000` con las credenciales definidas en `.env`.
3. Importe el dashboard `data/dashboards/oee_dashboard.json` desde el menú *Import Dashboard*.

### Escalar a otras líneas

La arquitectura es modular y permite crear nuevas secciones añadiendo mediciones
en InfluxDB y configurando más tareas de adquisición.
