from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.employer import EmployerCreate, EmployerResponse
from backend.services import crud

router = APIRouter(prefix="/employers", tags=["Employers"])


@router.post("/", response_model=EmployerResponse)
def create_employer(employer: EmployerCreate, db: Session = Depends(get_db)):
    """
    Create a new employer profile (linked to an existing user).
    """
    created_employer = crud.create_employer(db=db, employer=employer)
    if not created_employer:
        raise HTTPException(status_code=400, detail="Failed to create employer")
    return created_employer


@router.get("/", response_model=List[EmployerResponse])
def get_employers(db: Session = Depends(get_db)):
    """
    Get all employers.
    """
    return crud.get_employers(db)
