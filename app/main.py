from fastapi import APIRouter, FastAPI

from app.config import settings
from app.services import HubspotService

# Create the FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A basic FastAPI application with example endpoints",
    version=settings.version,
)

# Create API router with prefix
api_router = APIRouter(prefix="/api/v1")

# Inicializar servicio de HubSpot
hubspot_service = HubspotService(api_key=settings.hubspot_api_key)


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": app.version}


@api_router.get("/sdk/fech-request")
async def hubspot_webhook():
    return {
        "results": [
            {
                "objectId": "1234567890",
                "title": "Test SDK",
                "reported_by": "m.rodrigo@cebra.la",
                "properties": [
                    {"label": "Mensaje", "dataType": "STRING", "value": "Bienvenido!"}
                ],
            }
        ],
        "primaryAction": {
            "type": "IFRAME",
            "width": 350,
            "height": 550,
            "uri": f"{settings.http_host}/?hs_object_id=321654987",
            "label": "Abrir",
        },
    }


# Include the router in the main app
app.include_router(api_router)
