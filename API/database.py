import os

import redis
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "infraestructura_alcaldia")
REDIS_URL = os.getenv("REDIS_URL")
CACHE_TTL = int(os.getenv("CACHE_TTL_SEGUNDOS", "60"))
CUADRILLA_TTL = int(os.getenv("CUADRILLA_TTL_SEGUNDOS", "300"))

if not MONGO_URI or not REDIS_URL:
    raise RuntimeError(
        "Faltan variables de entorno. Copia .env.example a .env y completa MONGO_URI y REDIS_URL."
    )

cliente_mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
reportes = cliente_mongo[MONGO_DB]["reportes"]
r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=5)

CLAVE_CACHE_BARRIOS = "cache:reporte:resumen_barrios"
CLAVE_CONTADOR = "contador:reporte:consultas"
PREFIJO_CUADRILLA = "estado:cuadrilla:"

__all__ = [
    "CACHE_TTL",
    "CLAVE_CACHE_BARRIOS",
    "CLAVE_CONTADOR",
    "CUADRILLA_TTL",
    "PREFIJO_CUADRILLA",
    "ASCENDING",
    "DESCENDING",
    "cliente_mongo",
    "r",
    "reportes",
]
