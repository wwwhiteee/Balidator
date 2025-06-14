"""FastAPI application for local OEE system."""

from __future__ import annotations

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from . import db, models, auth, oee_logic, acquisition, schemas
from .auth import router as auth_router, get_current_user

models.Base.metadata.create_all(bind=db.engine)

app = FastAPI(title="Mediseal OEE")
app.include_router(auth_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize acquisition background tasks."""
    await acquisition.start_acquisition_tasks()

templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# OEE endpoints
@app.get("/oee/blistera", summary="Get blistera OEE", response_model=schemas.OEEData)
async def get_blistera_oee(
    start: str = "-1h",
    end: str = "now()",
    current_user: models.User = Depends(get_current_user),
):
    """Return OEE data for Blistera.

    Query parameters:

    - ``start``: inicio del rango (ej. ``-1h``)
    - ``end``: fin del rango (ej. ``now()``)

    Example response::

        {
          "availability": 100,
          "performance": 100,
          "quality": 98,
          "oee": 98
        }
    """
    return oee_logic.calculate_oee("blistera", start, end)


@app.get(
    "/oee/estuchadora",
    summary="Get estuchadora OEE",
    response_model=schemas.OEEData,
)
async def get_estuchadora_oee(
    start: str = "-1h",
    end: str = "now()",
    current_user: models.User = Depends(get_current_user),
):
    """Return OEE data for Estuchadora.

    Query parameters are the same as in :func:`get_blistera_oee`.

    Example response::

        {
          "availability": 100,
          "performance": 100,
          "quality": 97,
          "oee": 97
        }
    """
    return oee_logic.calculate_oee("estuchadora", start, end)


@app.post(
    "/paradas",
    summary="Registrar parada de máquina",
    response_model=schemas.ParadaResponse,
)
async def registrar_parada(
    parada: schemas.ParadaCreate,
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Registrar una parada indicando motivo y sección.

    Ejemplo de payload::

        {
          "seccion": "blistera",
          "motivo": "Cambio de formato"
        }
    """
    db_parada = models.Parada(
        seccion=parada.seccion,
        motivo=parada.motivo,
        timestamp_inicio=parada.timestamp_inicio or datetime.utcnow(),
        timestamp_fin=parada.timestamp_fin,
        user_id=current_user.id,
    )
    db_session.add(db_parada)
    db_session.commit()
    db_session.refresh(db_parada)
    return db_parada


@app.get(
    "/paradas",
    summary="Consultar paradas registradas",
    response_model=list[schemas.ParadaResponse],
)
async def listar_paradas(
    seccion: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Devuelve la lista de paradas registradas.

    Parametros opcionales de consulta:

    - ``seccion``: Filtrar por seccion de la línea.
    - ``start`` y ``end``: Filtrar por rango de fechas.
    """
    query = db_session.query(models.Parada)
    if seccion:
        query = query.filter(models.Parada.seccion == seccion)
    if start:
        query = query.filter(models.Parada.timestamp_inicio >= start)
    if end:
        query = query.filter(models.Parada.timestamp_inicio <= end)
    return query.all()
