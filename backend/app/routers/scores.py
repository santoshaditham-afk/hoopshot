from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("", response_model=schemas.ScoreOut, status_code=status.HTTP_201_CREATED)
def submit_score(
    body: schemas.ScoreCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    score = models.Score(
        user_id=current_user.id,
        score=body.score,
        shots_taken=body.shots_taken,
        shots_made=body.shots_made,
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    result = schemas.ScoreOut.model_validate(score)
    result.username = current_user.username
    return result


@router.get("/me", response_model=list[schemas.ScoreOut])
def my_scores(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    scores = (
        db.query(models.Score)
        .filter(models.Score.user_id == current_user.id)
        .order_by(models.Score.created_at.desc())
        .all()
    )
    results = []
    for s in scores:
        out = schemas.ScoreOut.model_validate(s)
        out.username = current_user.username
        results.append(out)
    return results


@router.get("/leaderboard", response_model=list[schemas.ScoreOut])
def leaderboard(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Score, models.User.username)
        .join(models.User, models.Score.user_id == models.User.id)
        .order_by(models.Score.score.desc())
        .limit(10)
        .all()
    )
    results = []
    for score, username in rows:
        out = schemas.ScoreOut.model_validate(score)
        out.username = username
        results.append(out)
    return results
