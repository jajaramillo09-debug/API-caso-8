from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Path

from API.database import CLAVE_CONTADOR, CUADRILLA_TTL, PREFIJO_CUADRILLA, r, reportes
from API.schemas.cuadrillas import EstadoCuadrilla
from API.utils import exigir_redis

router = APIRouter()
ID_CUADRILLA = Path(..., pattern=r"^[A-Za-z0-9_-]{1,20}$", description="Ej.: C-01")


@router.put("/cuadrillas/{cuadrilla_id}/estado", tags=["Cuadrillas (Redis)"])
def actualizar_estado_cuadrilla(cuadrilla_id: str = ID_CUADRILLA, datos: EstadoCuadrilla = ...):
    """Guarda el estado temporal de una cuadrilla en Redis."""
    if datos.reporte_codigo and not reportes.find_one({"codigo": datos.reporte_codigo}, {"_id": 1}):
        raise HTTPException(status_code=404, detail=f"No existe el reporte {datos.reporte_codigo}.")
    clave = f"{PREFIJO_CUADRILLA}{cuadrilla_id}"
    campos = {
        "estado": datos.estado,
        "reporte_codigo": datos.reporte_codigo or "",
        "actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    def guardar():
        tuberia = r.pipeline()
        tuberia.hset(clave, mapping=campos)
        tuberia.expire(clave, CUADRILLA_TTL)
        tuberia.execute()

    exigir_redis(guardar)
    return {"clave": clave, "ttl_segundos": CUADRILLA_TTL, **campos}


@router.get("/cuadrillas/{cuadrilla_id}/estado", tags=["Cuadrillas (Redis)"])
def consultar_estado_cuadrilla(cuadrilla_id: str = ID_CUADRILLA):
    """Devuelve el estado vigente de una cuadrilla."""
    clave = f"{PREFIJO_CUADRILLA}{cuadrilla_id}"
    datos = exigir_redis(lambda: r.hgetall(clave))
    if not datos:
        raise HTTPException(status_code=404, detail="Sin estado: la cuadrilla no ha reportado o el dato expiró.")
    return {"clave": clave, "ttl_segundos_restantes": exigir_redis(lambda: r.ttl(clave)), **datos}


@router.get("/cuadrillas", tags=["Cuadrillas (Redis)"])
def listar_cuadrillas():
    """Lista las cuadrillas con estado vigente."""

    def leer():
        lista = []
        for clave in r.scan_iter(match=f"{PREFIJO_CUADRILLA}*"):
            lista.append({"cuadrilla": clave.removeprefix(PREFIJO_CUADRILLA), **r.hgetall(clave)})
        return sorted(lista, key=lambda x: x["cuadrilla"])

    lista = exigir_redis(leer)
    return {"cantidad": len(lista), "cuadrillas": lista}


@router.get("/estadisticas/consultas", tags=["Cuadrillas (Redis)"])
def total_consultas_reporte():
    """Devuelve el contador Redis de consultas al reporte por barrio."""
    total = exigir_redis(lambda: r.get(CLAVE_CONTADOR))
    return {"clave": CLAVE_CONTADOR, "consultas_al_reporte": int(total or 0)}
