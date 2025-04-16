from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

import httpx
from fastapi import HTTPException

from app.config import settings
from app.models import DatosRegistro


class HubspotService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
        }

    async def search_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Busca un contacto en HubSpot por su dirección de correo electrónico.

        Args:
            email (str): El correo electrónico a buscar

        Returns:
            Optional[Dict[str, Any]]: Los datos del contacto si se encuentra, None si no existe

        Raises:
            HTTPException: Si hay un error en la API de HubSpot
        """
        url = f"{self.base_url}/crm/v3/objects/contacts/search"

        # Definir las propiedades que queremos obtener
        properties = ["email", "firstname", "lastname", "phone", "rut", "hs_object_id"]

        # Construir el payload de búsqueda
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": "email", "operator": "EQ", "value": email}
                    ]
                }
            ],
            "properties": properties,
            "limit": 1,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)

                # Verificar si la respuesta es exitosa
                response.raise_for_status()

                data = response.json()

                # Si encontramos resultados, devolver el primer contacto
                if data.get("total") > 0 and data.get("results"):
                    return data["results"][0]

                return None

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail={
                    "message": "Error en HubSpot API",
                    "status": e.response.json(),
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error interno del servidor: {str(e)}"
            )

    async def create_contact(
        self,
        email: str,
        firstname: str,
        lastname: str,
        rut: Optional[str] = None,
        pasaporte: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Crea un nuevo contacto en HubSpot.

        Args:
            email (str): Correo electrónico del contacto
            firstname (str): Nombre del contacto
            lastname (str): Apellido del contacto
            rut (Optional[str]): RUT del contacto, si aplica
            pasaporte (Optional[str]): Número de pasaporte, si aplica

        Returns:
            Dict[str, Any]: Los datos del contacto creado

        Raises:
            HTTPException: Si hay un error en la API de HubSpot
        """
        url = f"{self.base_url}/crm/v3/objects/contacts"

        # Construir las propiedades del contacto
        properties = {
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
        }

        # Agregar RUT o pasaporte solo si se proporcionan
        if rut:
            properties["rut"] = rut
        if pasaporte:
            properties["pasaporte"] = pasaporte

        payload = {"properties": properties}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)

                # Verificar si la respuesta es exitosa
                response.raise_for_status()

                return response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail={
                    "message": "Error al crear contacto en HubSpot",
                    "status": e.response.json(),
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor al crear contacto: {str(e)}",
            )

    async def update_contact(
        self,
        contact_id: str,
        email: Optional[str] = None,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        rut: Optional[str] = None,
        pasaporte: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Actualiza un contacto existente en HubSpot.

        Args:
            contact_id (str): ID del contacto en HubSpot
            email (Optional[str]): Nuevo correo electrónico
            firstname (Optional[str]): Nuevo nombre
            lastname (Optional[str]): Nuevo apellido
            rut (Optional[str]): Nuevo RUT
            pasaporte (Optional[str]): Nuevo número de pasaporte

        Returns:
            Dict[str, Any]: Los datos actualizados del contacto

        Raises:
            HTTPException: Si hay un error en la API de HubSpot o si el contacto no existe
        """
        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"

        # Construir las propiedades a actualizar (solo las que se proporcionan)
        properties = {}
        if email is not None:
            properties["email"] = email
        if firstname is not None:
            properties["firstname"] = firstname
        if lastname is not None:
            properties["lastname"] = lastname
        if rut is not None:
            properties["rut"] = rut
        if pasaporte is not None:
            properties["pasaporte"] = pasaporte

        # Si no hay propiedades para actualizar, lanzar error
        if not properties:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar",
            )

        payload = {"properties": properties}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=self.headers, json=payload)

                # Verificar si la respuesta es exitosa
                response.raise_for_status()

                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Contacto con ID {contact_id} no encontrado",
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail={
                    "message": "Error al actualizar contacto en HubSpot",
                    "status": e.response.json(),
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor al actualizar contacto: {str(e)}",
            )

    async def search_beca_by_email(
        self, email: str, carrera_consolidada: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Busca una beca en HubSpot por el correo electrónico del postulante.

        Args:
            email (str): El correo electrónico a buscar
            carrera_consolidada (Optional[str]): La carrera consolidada a buscar

        Returns:
            Optional[Dict[str, Any]]: Los datos de la beca si se encuentra, None si no existe

        Raises:
            HTTPException: Si hay un error en la API de HubSpot
        """
        url = f"{self.base_url}/crm/v3/objects/{settings.beca_object_id}/search"

        # Definir las propiedades que queremos obtener
        properties = [
            "email",
            "nombre",
            "apellidos",
            "rut",
            "pasaporte",
            "carrera_consolidada",
            "hs_object_id",
        ]

        # Construir el payload de búsqueda
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": "email", "operator": "EQ", "value": email},
                        {
                            "propertyName": "carrera_consolidada",
                            "operator": "EQ",
                            "value": carrera_consolidada,
                        },
                    ]
                }
            ],
            "properties": properties,
            "limit": 1,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()

                data = response.json()

                if data.get("total") > 0 and data.get("results"):
                    return data["results"][0]

                return None

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail={
                    "message": "Error en HubSpot API al buscar beca",
                    "status": e.response.json(),
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor al buscar beca: {str(e)}",
            )

    async def create_beca(
        self,
        email: str,
        nombre: str,
        apellidos: str,
        carrera_consolidada: str,
        rut: Optional[str] = None,
        pasaporte: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Crea una nueva beca en HubSpot.

        Args:
            email (str): Correo electrónico del postulante
            nombre (str): Nombre del postulante
            apellidos (str): Apellidos del postulante
            carrera_consolidada (str): Carrera consolidada
            rut (Optional[str]): RUT del postulante, si aplica
            pasaporte (Optional[str]): Número de pasaporte, si aplica

        Returns:
            Dict[str, Any]: Los datos de la beca creada

        Raises:
            HTTPException: Si hay un error en la API de HubSpot
        """
        url = f"{self.base_url}/crm/v3/objects/{settings.beca_object_id}"

        # Construir las propiedades de la beca
        properties = {
            "email": email,
            "nombre": nombre,
            "apellidos": apellidos,
            "carrera_consolidada": carrera_consolidada,  # HubSpot espera string
            "id": str(uuid4()),
        }

        # Agregar RUT o pasaporte solo si se proporcionan
        if rut:
            properties["rut"] = rut
        if pasaporte:
            properties["pasaporte"] = pasaporte

        payload = {"properties": properties}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail={
                    "message": "Error al crear beca en HubSpot",
                    "status": e.response.json(),
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor al crear beca: {str(e)}",
            )

    async def update_beca(
        self,
        beca_id: str,
        email: Optional[str] = None,
        nombre: Optional[str] = None,
        apellidos: Optional[str] = None,
        carrera_consolidada: Optional[str] = None,
        rut: Optional[str] = None,
        pasaporte: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Actualiza una beca existente en HubSpot.

        Args:
            beca_id (str): ID de la beca en HubSpot
            email (Optional[str]): Nuevo correo electrónico
            nombre (Optional[str]): Nuevo nombre
            apellidos (Optional[str]): Nuevos apellidos
            carrera_consolidada (Optional[str]): Nueva carrera consolidada
            rut (Optional[str]): Nuevo RUT
            pasaporte (Optional[str]): Nuevo número de pasaporte

        Returns:
            Dict[str, Any]: Los datos actualizados de la beca

        Raises:
            HTTPException: Si hay un error en la API de HubSpot
        """
        url = f"{self.base_url}/crm/v3/objects/{settings.beca_object_id}/{beca_id}"

        # Construir las propiedades a actualizar
        properties = {}
        if email is not None:
            properties["email"] = email
        if nombre is not None:
            properties["nombre"] = nombre
        if apellidos is not None:
            properties["apellidos"] = apellidos
        if carrera_consolidada is not None:
            properties["carrera_consolidada"] = carrera_consolidada
        if rut is not None:
            properties["rut"] = rut
        if pasaporte is not None:
            properties["pasaporte"] = pasaporte

        # Si no hay propiedades para actualizar, lanzar error
        if not properties:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar",
            )

        payload = {"properties": properties}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Beca con ID {beca_id} no encontrada",
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail={
                    "message": "Error al actualizar beca en HubSpot",
                    "status": e.response.json(),
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor al actualizar beca: {str(e)}",
            )

    async def associate_contact_with_beca(
        self, contact_id: str, beca_id: str
    ) -> Dict[str, Any]:
        """
        Asocia un contacto con una beca en HubSpot.

        Args:
            contact_id (str): ID del contacto en HubSpot
            beca_id (str): ID de la beca en HubSpot

        Returns:
            Dict[str, Any]: Respuesta de la API de HubSpot

        Raises:
            HTTPException: Si hay un error en la API de HubSpot
        """
        url = f"{self.base_url}/crm/v4/objects/0-1/{contact_id}/associations/{settings.beca_object_id}/{beca_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    json=[
                        {
                            "associationCategory": "USER_DEFINED",
                            "associationTypeId": 409,
                        }
                    ],
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="No se encontró el contacto o la beca especificada",
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail={
                    "message": "Error al asociar contacto con beca en HubSpot",
                    "status": e.response.json(),
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor al asociar objetos: {str(e)}",
            )

    async def process_registro(
        self, datos: DatosRegistro
    ) -> Tuple[Dict[str, Any], Dict[str, Any], bool, bool]:
        """
        Procesa un registro de datos, creando o actualizando el contacto y la beca, y los asocia.

        Args:
            datos (DatosRegistro): Datos del registro a procesar

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any], bool, bool]:
            - Datos del contacto
            - Datos de la beca
            - Si el contacto fue creado (True) o actualizado (False)
            - Si la beca fue creada (True) o actualizada (False)

        Raises:
            HTTPException: Si hay un error en la API de HubSpot
        """
        # Extraer datos personales
        persona = datos.datos_personales
        email = persona.correo

        # Buscar si existe el contacto
        contacto_existente = await self.search_contact_by_email(email)

        # Preparar datos de identificación
        id_data = persona.identificacion
        rut = id_data.numero if id_data.tipo == "rut" else None
        pasaporte = id_data.numero if id_data.tipo == "pasaporte" else None

        # Buscar si existe la beca
        beca_existente = await self.search_beca_by_email(
            email, datos.carrera_consolidada
        )

        # Si la beca no existe, crearla o actualizarla
        has_existing_beca = beca_existente is not None

        if beca_existente:
            # Actualizar beca existente
            beca_id = beca_existente["id"]
            resultado_beca = await self.update_beca(
                beca_id=beca_id,
                email=email,
                nombre=persona.nombre,
                apellidos=persona.apellidos,
                carrera_consolidada=datos.carrera_consolidada,
                rut=rut,
                pasaporte=pasaporte,
            )
        else:
            # Crear nueva beca
            resultado_beca = await self.create_beca(
                email=email,
                nombre=persona.nombre,
                apellidos=persona.apellidos,
                carrera_consolidada=datos.carrera_consolidada,
                rut=rut,
                pasaporte=pasaporte,
            )

        # Si el contacto no existe, crearlo o actualizarlo
        has_existing_contact = contacto_existente is not None

        if contacto_existente:
            contact_id = contacto_existente["id"]
            resultado_contacto = await self.update_contact(
                contact_id=contact_id,
                email=email,
                firstname=persona.nombre,
                lastname=persona.apellidos,
                rut=rut,
                pasaporte=pasaporte,
            )
        else:
            resultado_contacto = await self.create_contact(
                email=email,
                firstname=persona.nombre,
                lastname=persona.apellidos,
                rut=rut,
                pasaporte=pasaporte,
            )

        # Asociar el contacto con la beca
        await self.associate_contact_with_beca(
            contact_id=resultado_contacto["id"], beca_id=resultado_beca["id"]
        )

        return (
            resultado_contacto,
            resultado_beca,
            not has_existing_contact,
            not has_existing_beca,
        )
