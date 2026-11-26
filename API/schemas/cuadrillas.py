from typing import Literal, Optional

from pydantic import BaseModel, Field


class EstadoCuadrilla(BaseModel):
    estado: Literal["disponible", "en_camino", "en_obra"]
    reporte_codigo: Optional[str] = Field(None, examples=["REP-001"])
