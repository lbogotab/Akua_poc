# 📘 Akua Integration PoC — FastAPI

Esta prueba técnica implementa una **capa de integración real hacia la API de Akua**, con soporte total para los flujos principales del proceso de pago:

- **Autorización**
- **Pre-autorización**
- **Captura**
- **Cancelación**
- **Reembolso**
- **Consultas de Organizaciones**
- **Consultas de Comercios**

Incluye persistencia en **SQLite** para almacenar las respuestas de Akua y un entorno totalmente ejecutable mediante **Uvicorn** o **Docker Compose**.

---

## 🚀 1. Requisitos

- Python 3.10+
- pip
- (Opcional) virtualenv / pyenv
- Docker + Docker Compose (opcional, recomendado)

---

## ⚙️ 2. Variables de Entorno (.env)

El proyecto **no funcionará** sin un archivo `.env`. Tomar como copia el archivo `.env.template`

Crea uno basado en:

```
AKUA_API_BASE_URL=https://sandbox.akua.la
AKUA_ACCESS_TOKEN=<Token generado de autenticación - no necesario si se tiene cliente y secret>
AKUA_CLIENT_ID=<client_id_entregado>
AKUA_CLIENT_SECRET=<secret_entregado>

```

### Explicación

- **AKUA_CLIENT_ID / SECRET** → Para obtener el access token  


Se incluye también `.env.template` como referencia.  
**No se commitea el `.env` real.**

---

## 🗂️ 3. Estructura del Proyecto

```
app/
 ├── api/
 │   └── v1/
 │        ├── authorization.py
 │        ├── preauthorization.py
 │        ├── capture.py
 │        ├── cancel.py
 │        ├── refund.py
 │        ├── organizations.py
 │        ├── merchants.py
 │        └── health.py
 ├── schemas/
 ├── infrastructure/
 │      ├── akua_client.py
 │      └── database.py
 └── main.py
```

Arquitectura modular y alineada al enfoque **hexagonal** ligero.

---

## 🗄️ 4. Base de Datos (SQLite)

El proyecto persiste respuestas relevantes de Akua en:

```
app/data/akua_poc.db
```

Se registran:

- Autorizaciones  
- Pre-autorizaciones  
- Capturas  
- Cancelaciones  

Cada registro contiene:

- payment_id  
- transaction_id  
- status  
- amount  
- raw_response  
- timestamps  

Esto permite auditar los flujos ejecutados sin depender de Akua

---

## ▶️ 5. Ejecutar el Proyecto (Modo Local)

### Instalación manual

```bash
git clone <REPO_URL>
cd akua_poc
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# editar .env con tus credenciales reales
uvicorn app.main:app --reload
```

Acceder a Swagger:  
👉 http://localhost:8000/docs

Healthcheck:  
👉 http://localhost:8000/hello

---

## 🐳 6. Ejecutar con Docker Compose (recomendado)

### Paso 1 — Crear `.env`

```bash
cp .env.template .env
# editar con valores reales
```

### Paso 2 — Levantar el servicio

```bash
docker compose up --build
```

Swagger disponible en:  
👉 http://localhost:8000/docs

---

## 🔌 7. Endpoints Principales

Todos accesibles desde Swagger.

---

### 🧾 Autorización  
`POST /v1/authorization`

Permite enviar monto, tarjeta y datos mínimos desde Swagger.  
El ID y la idempotency key se generan automáticamente.

---

### 🧾 Pre-autorización  
`POST /v1/preauthorization`

Igual al flujo de autorización, pero con:

```
"intent": "pre-authorization"
```

Forzado internamente.

---

### 💰 Captura  
`POST /v1/capture/{payment_id}`

Permite:

- Captura total (sin parámetros)
- Captura parcial (parámetros `value` y `currency`)

---

### ❌ Cancelación  
`POST /v1/cancel/{payment_id}`

Cancela pagos **antes de ser capturados**.  
Persiste el resultado en DB.

---

### ↩️ Reembolso  
`POST /v1/refund/{payment_id}`

Requiere que el pago esté capturado.

---

### 🏢 Consultar Organizaciones  
`GET /v1/organizations`

---

### 🏪 Consultar Comercios  
`GET /v1/merchants?organization_id=XYZ`

---

### ❤️‍🔥 Healthcheck  
`GET /v1/health`

---

## 🧪 8. Flujo Completo de Prueba Recomendada

1. Obtener organizaciones  
2. Obtener merchants válidos  
3. Ejecutar autorización  
4. Ejecutar captura o cancelación  
5. Ejecutar reembolso  
6. Verificar registros en SQLite

---

## 🏁 9. Notas Finales

Este proyecto está diseñado para:

- Usarse como PoC realista para integraciones con Akua  
- Ser ejecutado tanto localmente como en Docker  
- Servir como base para flujos avanzados o webhooks  
- Mantener claridad en código, separación de capas y escalabilidad futura  

