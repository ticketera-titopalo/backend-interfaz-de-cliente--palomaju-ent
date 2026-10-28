<!-- calidad:inicio -->
![Calidad](https://img.shields.io/badge/Calidad-25%2F100-red) ![Aprobado](https://img.shields.io/badge/Aprobado-NO-red) ![Cumple](https://img.shields.io/badge/Cumple-12%2F15-green) ![Duplicación](https://img.shields.io/badge/Duplicaci%C3%B3n-6.5%25-green) ![SEC](https://img.shields.io/badge/SEC-0-green) ![SQL](https://img.shields.io/badge/SQL-0-green) ![DBG](https://img.shields.io/badge/DBG-0-green) ![Capas](https://img.shields.io/badge/Capas-3-green) ![Tests](https://img.shields.io/badge/Tests-10-green) ![Cob](https://img.shields.io/badge/Cob-88%25-green) ![EP](https://img.shields.io/badge/EP-18-green)

**Calidad de servicios (heurístico):** índice **25/100** · cumple **12/15** · aprobado **NO** · capas **3**
Detalle completo en [`docs/EVALUACION.md`](docs/EVALUACION.md).
<!-- calidad:fin -->

# backend-interfaz-de-cliente--palomaju-ent
backend de interfaz de cliente paloma juñent - flask 

# Ticketera - Backend

## Infraestructura Base
Este proyecto utiliza Docker para la base de datos MySQL.

### Cómo levantar el entorno:
1. Copiar el archivo de ejemplo: `cp .env.example .env`
2. Configurar las variables en el `.env`.
3. Ejecutar:
   ```bash
   docker compose up -d


## Cómo correr el backend (Flask)

```bash
cd client-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

El servidor queda en `http://0.0.0.0:5000`. La base se crea automáticamente con `db.create_all()` al arrancar.

## Variables de entorno (.env)

Ver `.env.example`. Principales:

- `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_ROOT_PASSWORD`
- `JWT_SECRET_KEY` (obligatorio, sin fallback)
- `JWT_ACCESS_TOKEN_EXPIRES` (segundos, default 900)
- `JWT_REFRESH_TOKEN_EXPIRES` (segundos, default 604800)
- `FRONTEND_URL` (origen del front, soporta varios separados por coma)
- `DATABASE_URI` (opcional; si se define, se usa en lugar de MySQL, útil para tests con SQLite)

## Cómo correr los tests

```bash
cd client-backend
pytest -q
```

Los tests usan SQLite en memoria (no requieren MySQL). Cobertura mínima exigida: 70%.

```bash
cd client-backend
pytest --cov=. --cov-report=term-missing
```

## Prueba cross-machine (front en otra compu)

- Back: `.env` con `FRONTEND_URL=http://IP-FRONT:5173`, arrancar con `python app.py` (binding `0.0.0.0:5000`).
- Front: `.env` con `VITE_API_URL=http://IP-BACK:5000`.
- Verificar conectividad: `curl http://IP-BACK:5000/api/status` desde la otra compu.

## Estructura del backend (capas)

```
client-backend/
  app.py              # composition root
  extensions.py       # db, jwt
  core/               # decoradores (admin_required)
  models/             # Concert, User, Purchase, Ticket, TicketRedemption, RevokedToken
  services/           # auth, concert, purchase, ticket, user, admin_concert
  routes/             # status, concerts, auth, purchase, tickets, users, admin, admin_concerts
  errors.py           # helper + handlers globales
  tests/              # pytest (SQLite in-memory)
```
