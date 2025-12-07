# 📘 Akua Integration PoC — FastAPI

Esta es una prueba técnica que implementa una **capa de integración simulada hacia la API de Akua**.  
El objetivo es demostrar:

- Diseño limpio de API (FastAPI + arquitectura modular).
- Modelado de flujos de pago: **autorización, pre-autorización, captura, cancelación y reembolso**.
- Ejemplo realista de un **checkout de e-commerce** que:
  - recibe datos de la orden,
  - los mapea al formato Akua,
  - llama al cliente de Akua ,
  - y persiste la respuesta en **SQLite**.
- Documentación automática con Swagger para pruebas manuales.

---

## 🚀 1. Requisitos

- Python 3.10+
- pip
- (Opcional) virtualenv o pyenv

---

## 🏗️ 2. Instalación

```bash
git clone <REPO_URL>
cd akua_poc
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# o .venv\Scripts\activate en Windows
pip install -r requirements.txt
```

---

## ⚙️ 3. Variables de Entorno (.env)

Crear un archivo `.env` en la raíz del proyecto:

```
AKUA_MODE=MOCK
AKUA_BASE_URL=https://sandbox.akua.la
AKUA_ACCESS_TOKEN=
AKUA_MERCHANT_ID=mer-csuvatde7f1jb0qgqjvg
```

### Modo MOCK
- No hace llamadas HTTP reales
- Genera respuestas simuladas con estructura válida

### Modo REAL
Cuando recibas credenciales:

```
AKUA_MODE=REAL
AKUA_ACCESS_TOKEN=<TOKEN_REAL>
```

---

## ▶️ 4. Ejecutar el proyecto

```bash
uvicorn app.main:app --reload
```

Servicio disponible en:  
👉 http://localhost:8000

Documentación Swagger:  
👉 http://localhost:8000/docs

---

## ❤️‍🔥 5. Probar la API desde Swagger

Swagger expone todos los flujos implementados.

---

### ✔️ 5.1 Healthcheck  
`GET /v1/health`

Verifica que el servicio está operativo.

Respuesta esperada:

```json
{
  "status": "ok",
  "message": "Servicio operativo",
  "component": "Akua Integration PoC"
}
```

---

### 🧾 5.2 Autorización / Pre-autorización  
`POST /v1/authorization`  
`POST /v1/preauthorization`

Swagger incluye un body de ejemplo automático basado en la documentación real de Akua.

---

### 💳 5.3 Flujo de Checkout (E-commerce)

`POST /v1/ecommerce/checkout`

Simula un e-commerce real:

1. Recibe `order_id`, monto y tarjeta.  
2. Construye internamente `AuthorizationRequest`.  
3. Llama a Akua.  
4. Persiste el resultado en SQLite (`app/data/akua_poc.db`).  

Ejemplo visible en Swagger:

```json
{
  "order_id": "ORD-12345",
  "amount": 150000,
  "currency": "COP",
  "card": {
    "number": "5191872272166422",
    "cvv": "917",
    "exp_month": "12",
    "exp_year": "26",
    "holder_name": "Alejandro Bogotá"
  },
  "capture_mode": "AUTOMATIC"
}
```

---

### 🔄 5.4 Captura manual  
`POST /v1/capture/{payment_id}`  

Swagger muestra:

```json
{
  "amount": {
    "value": 100,
    "currency": "USD"
  }
}
```

---

### ↩️ 5.5 Reembolso  
`POST /v1/refund/{payment_id}`

```json
{
  "amount": {
    "value": 100,
    "currency": "USD"
  }
}
```

---

### ❌ 5.6 Cancelación  
`POST /v1/cancel/{payment_id}`

```json
{
  "taxes": [
    {
      "type": "IVA",
      "percentage": 19,
      "base_amount": {
        "currency": "COP",
        "value": 100000
      },
      "laws": ["4x1000"]
    }
  ]
}
```

---

## 🗄️ 6. Persistencia en SQLite

El checkout registra pagos en:

```
app/data/akua_poc.db
```

Campos guardados:
- order_id  
- payment_id  
- transaction_id  
- status  
- raw_response  
- created_at  

---

## 🧱 7. Arquitectura del Proyecto

```
app/
 ├── api/
 │   └── v1/
 │        ├── authorization.py
 │        ├── cancel.py
 │        ├── refund.py
 │        ├── capture.py
 │        ├── checkout.py
 │        └── health.py
 ├── schemas/
 ├── infrastructure/
 │      ├── akua_client.py
 │      └── database.py
 └── main.py
```

Modular, extensible y alineado a una arquitectura hexagonal ligera.

---

## 🧪 8. Cómo probar la integración completa

1. Abrir Swagger: http://localhost:8000/docs  
2. Ejecutar checkout.  
3. Ver respuesta MOCK con `payment_id`.  
4. Revisar SQLite.  
5. Probar captura, reembolso o cancelación con ese `payment_id`.

---

## 🏁 9. Notas finales

Este proyecto está listo para:

- correr en modo MOCK sin credenciales,  
- habilitar modo REAL con token sandbox,  
- extenderse hacia webhooks o flujos avanzados de pagos.

