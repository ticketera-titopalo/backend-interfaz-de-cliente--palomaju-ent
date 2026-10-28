<!-- calidad:inicio -->
![Calidad](https://img.shields.io/badge/Calidad-16%2F100-red) ![Aprobado](https://img.shields.io/badge/Aprobado-NO-red) ![Cumple](https://img.shields.io/badge/Cumple-12%2F15-green) ![Duplicación](https://img.shields.io/badge/Duplicaci%C3%B3n-6.5%25-green) ![SEC](https://img.shields.io/badge/SEC-0-green) ![SQL](https://img.shields.io/badge/SQL-0-green) ![DBG](https://img.shields.io/badge/DBG-0-green) ![Capas](https://img.shields.io/badge/Capas-3-green) ![Tests](https://img.shields.io/badge/Tests-10-green) ![Cob](https://img.shields.io/badge/Cob-88%25-green) ![EP](https://img.shields.io/badge/EP-18-green)

**Calidad de servicios (heurístico):** índice **16/100** · cumple **12/15** · aprobado **NO** · capas **3**
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