from datetime import datetime
from typing import Any, Callable, TypeVar

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from redis.exceptions import RedisError

from API.database import CLAVE_CACHE_BARRIOS, r

T = TypeVar("T")


def a_objectid(id_texto: str) -> ObjectId:
    """Convierte el id de la URL a ObjectId; si no tiene formato válido responde 400."""
    try:
        return ObjectId(id_texto)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="El id no tiene un formato válido (24 caracteres hexadecimales).",
        )


def serializar(doc: dict[str, Any]) -> dict[str, Any]:
    """Prepara un documento de Mongo para devolverlo como JSON."""
    doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("fecha_reporte"), datetime):
        doc["fecha_reporte"] = doc["fecha_reporte"].date().isoformat()
    return doc


def invalidar_cache_reporte() -> None:
    """Borra la caché del reporte cuando cambian los datos que la alimentan."""
    try:
        r.delete(CLAVE_CACHE_BARRIOS)
    except RedisError as e:
        print(f"Aviso: no se pudo invalidar la caché ({e.__class__.__name__}).")


def exigir_redis(operacion: Callable[[], T]) -> T:
    """Ejecuta una operación Redis y responde 503 si Redis no está disponible."""
    try:
        return operacion()
    except RedisError:
        raise HTTPException(status_code=503, detail="Redis no está disponible en este momento.")
