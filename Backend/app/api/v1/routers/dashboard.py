
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, check_role
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardResumoResponse


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/resumo",
    response_model=DashboardResumoResponse,
    status_code=status.HTTP_200_OK
)
def obter_resumo_dashboard(
    data_inicial: date | None = Query(
        default=None,
        description="Data inicial do período de consulta."
    ),

    data_final: date | None = Query(
        default=None,
        description="Data final do período de consulta."
    ),

    db: Session = Depends(get_db),

    usuario=Depends(check_role("Gestão"))
):
    try:
        return DashboardService.obter_resumo(
            db=db,
            data_inicial=data_inicial,
            data_final=data_final
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )
