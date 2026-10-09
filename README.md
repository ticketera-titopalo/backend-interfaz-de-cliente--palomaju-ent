<!-- calidad:inicio -->
![Calidad](https://img.shields.io/badge/Calidad-34%2F100-red) ![Cumple](https://img.shields.io/badge/Cumple-8%2F15-orange) ![Aprobado](https://img.shields.io/badge/Aprobado-NO-red)

**Calidad de servicios (heurístico):** índice **34/100** · cumple **8/15** · aprobado **NO** · capas **0**
`SEC 0 · SQL 0 · DBG 2 · duplicación 4.2% · endpoints 6 · tests 0`
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