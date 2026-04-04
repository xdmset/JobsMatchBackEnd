from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_same_user, get_current_user
from app.core.enums import NombreRol
from app.db.session import get_db
from app.models.user import User
from app.schemas.match import MatchResponse
from app.services.subscription_service import build_plan_context, get_student_match_history

router = APIRouter()


def _bounded_limit(skip: int, requested_limit: int, max_items: int | None) -> int:
    if max_items is None:
        return requested_limit
    remaining = max(max_items - skip, 0)
    return min(requested_limit, remaining)


@router.get("/estudiante/{estudiante_id}", response_model=list[MatchResponse])
def read_student_match_history(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)
    plan_context = build_plan_context(current_user)
    effective_limit = _bounded_limit(skip, limit, plan_context.match_history_limit)
    return get_student_match_history(db, estudiante_id=estudiante_id, skip=skip, limit=effective_limit)
