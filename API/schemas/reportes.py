from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

TipoEstructura = Literal["via", "edificio", "puente", "anden"]
EstadoReporte = Literal["pendiente", "en_reparacion", "resuelto"]


class ReporteIn(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=20)
    tipo_estructura: TipoEstructura
    descripcion: str = Field(..., min_length=5, max_length=500)
    barrio: str = Field(..., min_length=2, max_length=60)
    severidad: int = Field(..., ge=1, le=5)
    personas_afectadas: int = Field(0, ge=0)
    estado: EstadoReporte = "pendiente"
    fecha_reporte: Optional[date] = None
    etiquetas: list[str] = Field(default_factory=list)
    fotos: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo": "REP-031",
                "tipo_estructura": "via",
                "descripcion": "Hundimiento del pavimento frente a la escuela",
                "barrio": "Cuba",
                "severidad": 4,
                "personas_afectadas": 80,
                "estado": "pendiente",
                "etiquetas": ["hundimiento", "pavimento"],
                "fotos": ["rep031_a.jpg"],
            }
        }
    }


class ReporteUpdate(BaseModel):
    """Todos los campos son opcionales: solo se actualizan los que lleguen."""

    tipo_estructura: Optional[TipoEstructura] = None
    descripcion: Optional[str] = Field(None, min_length=5, max_length=500)
    barrio: Optional[str] = Field(None, min_length=2, max_length=60)
    severidad: Optional[int] = Field(None, ge=1, le=5)
    personas_afectadas: Optional[int] = Field(None, ge=0)
    estado: Optional[EstadoReporte] = None
    etiquetas: Optional[list[str]] = None
    fotos: Optional[list[str]] = None

    model_config = {"json_schema_extra": {"example": {"estado": "en_reparacion"}}}
