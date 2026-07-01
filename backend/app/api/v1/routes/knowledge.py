from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.knowledge import pest_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("/pests/{pest}")
def get_pest_profile(pest: str, db: Session = Depends(get_db)):
    return pest_service.get_profile(db, pest)


@router.get("/pests/{pest}/deterrents")
def get_pest_deterrents(pest: str, db: Session = Depends(get_db)):
    return pest_service.get_deterrent_plants(db, pest)


@router.get("/pests/{pest}/predators")
def get_pest_predators(pest: str):
    return pest_service.get_predators(pest)


@router.get("/pests/{pest}/hosts")
def get_pest_hosts(pest: str, db: Session = Depends(get_db)):
    return pest_service.get_host_plants(db, pest)
