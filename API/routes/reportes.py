import json
import time
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import DuplicateKeyError
from redis.exceptions import RedisError

from API.database import (
    CACHE_TTL,
    CLAVE_CACHE_BARRIOS,
    CLAVE_CONTADOR,
    reportes,
    r,
)
from API.schemas.reportes import EstadoReporte, ReporteIn, ReporteUpdate, TipoEstructura
from API.utils import a_objectid, invalidar_cache_reporte, serializar

router = APIRouter()


@router.get("/reportes", tags=["Reportes (MongoDB)"])
def listar_reportes(
    estado: Optional[EstadoReporte] = None,
    tipo_estructura: Optional[TipoEstructura] = None,
    barrio: Optional[str] = None,
    severidad_min: Optional[int] = Query(None, ge=1, le=5),
    limite: int = Query(20, ge=1, le=100),
):
    """Lista reportes. Todos los filtros son opcionales; los más graves salen primero."""
    filtro = {}
    if estado:
        filtro["estado"] = estado
    if tipo_estructura:
        filtro["tipo_estructura"] = tipo_estructura
    if barrio:
        filtro["barrio"] = barrio
    if severidad_min:
        filtro["severidad"] = {"$gte": severidad_min}
    cursor = reportes.find(filtro).sort([("severidad", -1), ("fecha_reporte", -1)]).limit(limite)
    lista = [serializar(d) for d in cursor]
    return {"cantidad": len(lista), "reportes": lista}


@router.get("/reportes/resumen/barrios", tags=["Reporte con caché (MongoDB + Redis)"])
def reporte_resumen_barrios():
    """
    Devuelve los barrios con más daños sin resolver, usando caché Redis y MongoDB.
    """
    inicio = time.perf_counter()
    try:
        r.incr(CLAVE_CONTADOR)
    except RedisError:
        pass

    try:
        guardado = r.get(CLAVE_CACHE_BARRIOS)
    except RedisError:
        guardado = None
    if guardado:
        return {
            "origen": "redis",
            "ttl_segundos_restantes": r.ttl(CLAVE_CACHE_BARRIOS),
            "milisegundos": round((time.perf_counter() - inicio) * 1000, 2),
            "datos": json.loads(guardado),
        }

    pipeline = [
        {"$match": {"estado": {"$in": ["pendiente", "en_reparacion"]}}},
        {"$group": {
            "_id": "$barrio",
            "reportes_abiertos": {"$sum": 1},
            "personas_afectadas": {"$sum": "$personas_afectadas"},
            "severidad_promedio": {"$avg": "$severidad"},
            "severidad_maxima": {"$max": "$severidad"},
        }},
        {"$sort": {"severidad_maxima": -1, "personas_afectadas": -1}},
        {"$project": {
            "_id": 0,
            "barrio": "$_id",
            "reportes_abiertos": 1,
            "personas_afectadas": 1,
            "severidad_promedio": {"$round": ["$severidad_promedio", 1]},
            "severidad_maxima": 1,
        }},
    ]
    datos = list(reportes.aggregate(pipeline))

    try:
        r.set(CLAVE_CACHE_BARRIOS, json.dumps(datos, ensure_ascii=False), ex=CACHE_TTL)
    except RedisError:
        pass
    return {
        "origen": "mongo",
        "ttl_segundos_restantes": CACHE_TTL,
        "milisegundos": round((time.perf_counter() - inicio) * 1000, 2),
        "datos": datos,
    }


@router.get("/reportes/{reporte_id}", tags=["Reportes (MongoDB)"])
def obtener_reporte(reporte_id: str):
    """Devuelve un reporte. 400 si el id es inválido, 404 si no existe."""
    doc = reportes.find_one({"_id": a_objectid(reporte_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="No existe un reporte con ese id.")
    return serializar(doc)


@router.post("/reportes", status_code=201, tags=["Reportes (MongoDB)"])
def crear_reporte(reporte: ReporteIn):
    """Crea un reporte validado e invalida la caché del resumen por barrio."""
    doc = reporte.model_dump()
    fecha = doc["fecha_reporte"] or date.today()
    doc["fecha_reporte"] = datetime(fecha.year, fecha.month, fecha.day)
    try:
        resultado = reportes.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail=f"Ya existe un reporte con el código {reporte.codigo}.")
    invalidar_cache_reporte()
    doc["_id"] = resultado.inserted_id
    return serializar(doc)


@router.put("/reportes/{reporte_id}", tags=["Reportes (MongoDB)"])
def actualizar_reporte(reporte_id: str, cambios: ReporteUpdate):
    """Actualiza uno o varios campos y solo persiste los enviados."""
    oid = a_objectid(reporte_id)
    datos = cambios.model_dump(exclude_unset=True)
    if not datos:
        raise HTTPException(status_code=400, detail="No se envió ningún campo para actualizar.")
    resultado = reportes.update_one({"_id": oid}, {"$set": datos})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="No existe un reporte con ese id.")
    invalidar_cache_reporte()
    return serializar(reportes.find_one({"_id": oid}))


@router.delete("/reportes/{reporte_id}", tags=["Reportes (MongoDB)"])
def borrar_reporte(reporte_id: str):
    """Borra un reporte e invalida la caché del resumen por barrio."""
    resultado = reportes.delete_one({"_id": a_objectid(reporte_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No existe un reporte con ese id.")
    invalidar_cache_reporte()
    return {"mensaje": "Reporte eliminado", "id": reporte_id}
