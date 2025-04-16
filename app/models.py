from typing import Literal, Optional, Union

from pydantic import BaseModel, EmailStr, Field


class RutIdentificacion(BaseModel):
    tipo: Literal["rut"] = "rut"
    numero: str = Field(
        ...,
        pattern=r"^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]{1}$",
        description="RUT chileno en formato XX.XXX.XXX-X",
    )


class PasaporteIdentificacion(BaseModel):
    tipo: Literal["pasaporte"] = "pasaporte"
    numero: str = Field(..., min_length=5, description="Número de pasaporte")


class PersonaBase(BaseModel):
    nombre: str = Field(..., min_length=2, description="Nombre de la persona")
    apellidos: str = Field(..., min_length=2, description="Apellidos de la persona")
    correo: EmailStr = Field(..., description="Correo electrónico")
    identificacion: Union[RutIdentificacion, PasaporteIdentificacion] = Field(
        ..., description="Identificación (RUT o Pasaporte)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan",
                "apellidos": "Pérez",
                "correo": "juan.perez@ejemplo.com",
                "identificacion": {"tipo": "rut", "numero": "12.345.678-9"},
            }
        }


class DatosRegistro(BaseModel):
    datos_personales: PersonaBase
    carrera_consolidada: Optional[str] = Field(
        None,
        description="Carrera consolidada (requerido solo para becas)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "datos_personales": {
                    "nombre": "Juan",
                    "apellidos": "Pérez",
                    "correo": "juan.perez@ejemplo.com",
                    "identificacion": {"tipo": "rut", "numero": "12.345.678-9"},
                },
                "carrera_consolidada": "Ingeniería Civil",
            }
        }
