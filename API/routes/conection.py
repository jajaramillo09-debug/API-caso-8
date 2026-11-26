from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

from API.database import cliente_mongo, r

router = APIRouter()


@router.get("/ping", tags=["Conexiones"])
def ping():
    """Comprueba la conexión a las dos bases de datos."""
    estado = {}
    try:
        cliente_mongo.admin.command("ping")
        estado["mongo"] = "ok"
    except PyMongoError as e:
        estado["mongo"] = f"error ({e.__class__.__name__})"
    try:
        r.ping()
        estado["redis"] = "ok"
    except RedisError as e:
        estado["redis"] = f"error ({e.__class__.__name__})"
    if any(v != "ok" for v in estado.values()):
        raise HTTPException(status_code=503, detail=estado)
    return estado
