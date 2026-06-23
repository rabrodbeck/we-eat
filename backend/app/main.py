import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.database import get_db, DBFamilyMember, DBFamily
from app.schemas import Diner
from app.auth import verify_token
from app.agent import get_recommendations

app = FastAPI(title="WeEat API")

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

class FamilyResponse(BaseModel):
    id: str
    family_name: str
    created_by: str

class InviteMemberRequest(BaseModel):
    member_id: int
    email: EmailStr

class AcceptInviteRequest(BaseModel):
    invite_token: str

# Helper function to get a user's family or create one if th ey are new
def get_user_family_member(user_uid: str, db: Session) -> DBFamilyMember:
    # 1. Look for a family member profile mapped to this user login
    member = db.query(DBFamilyMember).filter(DBFamilyMember.user_id == user_uid).first()

    if not member:
        # User is brand new (not invited and has no family yet) Auto-create family.
        family_id = str(uuid.uuid4())
        new_family = DBFamily(
            id=family_id,
            family_name="My Family",
            created_by=user_uid
        )
        db.add(new_family)

        # Create their corresponding Head of Family diner profile
        member = DBFamilyMember(
            family_id=family_id,
            user_id=user_uid,
            name="Head of Family",
            role="head",
            invite_accepted=True
        )
        db.add(member)
        db.commit()
        db.refresh(member)

    return member

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Get a user's active family metadata
@app.get("/api/family", response_model=FamilyResponse)
def get_family(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member(user["uid"], db)
    family = db.query(DBFamily).filter(DBFamily.id == user_member.family_id).first()
    return FamilyResponse(
        id=str(family.id),
        family_name=family.family_name,
        created_by=family.created_by
    )

# Send an invite to an existing family member profile
@app.post("/api/family/invite")
def invite_member(req: InviteMemberRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member(user["uid"], db)

    # Verify requesting user is the Head of the Family
    if user_member.role != "head":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the family head can invite members")
    
    # Find the diner profile to invite
    target_member = db.query(DBFamilyMember).filter(
        DBFamilyMember.id == req.member_id,
        DBFamilyMember.family_id == user_member.family_id
    ).first()

    if not target_member:
        raise HTTPException(status_code=404, detail="Diner profile not found in your family")
    
    # Generate token and save email
    target_member.email = req.email
    target_member.invite_token = str(uuid.uuid4())
    target_member.invite_accepted = False
    
    db.commit()

    # Return the link so the owner can copy/send it
    invite_link = f"/invite?token={target_member.invite_token}"
    return {"message": "Invite generated successfully", "invite_link": invite_link}

# Accept and invitation
@app.post("/api/family/accept-invite")
def accept_invite(req: AcceptInviteRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    # Find the diner profile matching this invite token
    member = db.query(DBFamilyMember).filter(DBFamilyMember.invite_token == req.invite_token).first()
    if not member:
        raise HTTPException(status_code=404, detail="Invalid or expired invite token")
    
    if member.invite_accepted:
        raise HTTPException(status_code=400, detail="Invite has already been accepted")
    
    # Check if this user account is already linked to another family member
    existing_link = db.query(DBFamilyMember).filter(DBFamilyMember.user_id == user["uid"]).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Your user account is already linked to a family")
    
    # Link the logged-in user account to this diner profile
    member.user_id = user["uid"]
    member.invite_accepted = True
    db.commit()

    return {"message": "Successfully joined the family"}

# Get all diners in the user's family
@app.get("/api/diners", response_model=List[Diner])
def get_diners(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member(user["uid"], db)
    db_diners = db.query(DBFamilyMember).filter(DBFamilyMember.family_id == user_member.family_id).all()
    return [Diner(id=d.id, name=d.name, dislikes=d.dislikes, is_active=True, role=d.role, invite_accepted=d.invite_accepted) for d in db_diners]

# Add a diner to the family
@app.post("/api/diners", response_model=Diner)
def create_diner(diner: Diner, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member(user["uid"], db)

    existing = db.query(DBFamilyMember).filter(
        DBFamilyMember.family_id == user_member.family_id,
        DBFamilyMember.name == diner.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Diner profile already exists in this family")
    
    db_diner = DBFamilyMember(
        family_id=user_member.family_id,
        name=diner.name,
        dislikes=diner.dislikes,
        role="member",
        invite_accepted=False
    )
    db.add(db_diner)
    db.commit()
    db.refresh(db_diner)
    return Diner(
        id=db_diner.id,
        name=db_diner.name,
        dislikes=db_diner.dislikes,
        is_active=True,
        role=db_diner.role,
        invite_accepted=db_diner.invite_accepted
    )

# Delete a diner from the family
@app.delete("/api/diners/{name}")
def delete_diner(name: str, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member(user["uid"], db)

    db_diner = db.query(DBFamilyMember).filter(
        DBFamilyMember.family_id == user_member.family_id,
        DBFamilyMember.name == name
    ).first()
    if not db_diner:
        raise HTTPException(status_code=404, detail="Diner profile not found in this family")
    
    # Prevent deleting the Head of Family
    if db_diner.role == "head":
        raise HTTPException(status_code=400, detail="Cannot delete the head of the family")
    
    db.delete(db_diner)
    db.commit()
    return {"message": "Diner profile deleted successfully"}

# Recommendation scopes within the active family
@app.post("/api/recommend")
def recommend_restaurants(req: RecommendRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member(user["uid"], db)
    db_diners = db.query(DBFamilyMember).filter(DBFamilyMember.family_id == user_member.family_id).all()

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
