# Bot transaccional de vuelos (NLP → JSON + IATA)

Proyecto académico (Minería de Datos) que implementa un bot transaccional para búsqueda de vuelos.
Convierte frases en lenguaje natural a un JSON estructurado con:
- Ciudad Origen / Ciudad Destino
- Fecha (dd-mm-yyyy)
- Pax (cantidad de pasajeros)
- Aerolínea
- Códigos IATA (From/To) usando la API Air-PortCodes

## Estructura del proyecto

- `assistant_bot.py` → Asistente conversacional (CLI).
- `nlp_parser.py` → Extracción de entidades desde texto (origen, destino, fecha, pax, aerolínea).
- `date_utils.py` → Normalización de fechas (mes, día-mes-año, etc.).
- `iata_client.py` → Cliente para consultar Air-PortCodes.
- `iata_service.py` → Construye el JSON final integrando NLP + fecha + IATA.
- `bot_vuelos.ipynb` → Notebook demo solicitado en el enunciado.

## Requisitos

- Python 3.10+ recomendado
- Conexión a Internet (para geocodificación y consulta IATA)

Instalar dependencias:

```bash
pip install -r requirements.txt