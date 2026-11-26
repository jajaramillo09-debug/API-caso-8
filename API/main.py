from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from API.database import reportes
from API.routes import cuadrillas, health, reportes as rutas_reportes


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Crea los índices necesarios al iniciar la API."""
    try:
        reportes.create_index("codigo", unique=True)
        reportes.create_index("estado")
        reportes.create_index([("tipo_estructura", ASCENDING), ("severidad", DESCENDING)])
    except PyMongoError as e:
        print(f"Aviso: no se pudieron crear los índices ({e.__class__.__name__}).")
    yield


app = FastAPI(
    title="API de infraestructura dañada · Caso 8",
    description="Reportes ciudadanos en MongoDB y caché/estado en tiempo real en Redis.",
    version="1.0.0",
    lifespan=ciclo_de_vida,
)

app.include_router(health.router)
app.include_router(rutas_reportes.router)
app.include_router(cuadrillas.router)
