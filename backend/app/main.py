from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.config import settings
from app.database import get_db, DBFamilyMember
from app.schemas import Diner
from app.auth import verify_token
from app.agent import get_recommendations

app = FastAPI(title="WeEat API")

# Setup CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    query: str
    active_diner_names: List[str]
    user_lat: float
    user_lon: float
    max_distance_miles: float = 15.0

@app.get("/api/health")
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.get("/api/diners", response_model=List[Diner])
def get_diners(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    """Get all familty member profiles for the logged-in user."""
    db_diners = db.query(DBFamilyMember).filter(DBFamilyMember.user_id == user["uid"]).all()
    return [Diner(name=d.name, dislikes=d.dislikes, is_active=True) for d in db_diners]

@app.post("/api/diners", response_model=Diner)
def create_diner(diner: Diner, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    """Create a new family member profile."""
    existing = db.query(DBFamilyMember).filter(
        DBFamilyMember.user_id == user["uid"],
        DBFamilyMember.name == diner.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Diner profile already exists")
    
    db_diner = DBFamilyMember(
        user_id=user["uid"],
        name=diner.name,
        dislikes=diner.dislikes
    )
    db.add(db_diner)
    db.commit()
    db.refresh(db_diner)
    return diner

@app.delete("/api/diners/{name}")
def delete_diner(name: str, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    """Delete a family member profile."""
    db_diner = db.query(DBFamilyMember).filter(
        DBFamilyMember.user_id == user["uid"],
        DBFamilyMember.name == name
    ).first()
    if not db_diner:
        raise HTTPException(status_code=404, detail="Diner profile not found")
    
    db.delete(db_diner)
    db.commit()
    return {"message": "Diner profile deleted successfully"}

@app.post("/api/recommend")
def recommend_restaurants(req: RecommendRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    """Get family restaurant recommendations based on active diners."""
    db_diners = db.query(DBFamilyMember).filter(DBFamilyMember.user_id == user["uid"]).all()

    diners_list = []
    for d in db_diners:
        is_active = d.name in req.active_diner_names
        diners_list.append(Diner(name=d.name, dislikes=d.dislikes, is_active=is_active))

    recommendation = get_recommendations(
        query=req.query,
        diners=diners_list,
        user_lat=req.user_lat,
        user_lon=req.user_lon,
        max_distance_miles=req.max_distance_miles
    )
    return {"recommendation": recommendation}
