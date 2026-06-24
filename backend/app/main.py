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

class CreateFamilyRequest(BaseModel):
    family_name: str
    head_name: str

class UpdateFamilyRequest(BaseModel):
    family_name: str

class UpdateDinerRequest(BaseModel):
    name: str
    dislikes: List[str]

# Helper function to find a user's family membership (without auto-creating)
def get_user_family_member_or_none(user_uid: str, db: Session) -> Optional[DBFamilyMember]:
    return db.query(DBFamilyMember).filter(DBFamilyMember.user_id == user_uid).first()
    

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Get a user's active family metadata
@app.get("/api/family", response_model=Optional[FamilyResponse])
def get_family(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member_or_none(user["uid"], db)
    if not user_member:
        return None # TReturn 200 OK with null instead of raising a 404
    
    family = db.query(DBFamily).filter(DBFamily.id == user_member.family_id).first()
    return FamilyResponse(
        id=str(family.id),
        family_name=family.family_name,
        created_by=family.created_by
    )

# Create/Initialize a new family (first-time setup)
@app.post("/api/family", response_model=FamilyResponse)
def create_family(req: CreateFamilyRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    # Check if user already belongs to a family
    existing_member = get_user_family_member_or_none(user["uid"], db)
    if existing_member:
        raise HTTPException(status_code=400, detail="User already belongs to a family")
    
    family_id = str(uuid.uuid4())

    # Create new family
    new_family = DBFamily(
        id=family_id,
        family_name=req.family_name,
        created_by=user["uid"]
    )
    db.add(new_family)

    # Create corresponding head-of-family diner profile
    new_member = DBFamilyMember(
        family_id=family_id,
        user_id=user["uid"],
        name=req.head_name,
        role="head",
        invite_accepted=True
    )
    db.add(new_member)

    db.commit()
    db.refresh(new_family)

    return FamilyResponse(
        id=str(new_family.id),
        family_name=new_family.family_name,
        created_by=new_family.created_by
    )

# Rename the family (Family Head only)
@app.put("/api/family", response_model=FamilyResponse)
def update_family(req: UpdateFamilyRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member_or_none(user["uid"], db)
    if not user_member:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    if user_member.role != "head":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the family head can rename the family")
    
    family = db.query(DBFamily).filter(DBFamily.id == user_member.family_id).first()
    family.family_name = req.family_name
    db.commit()
    db.refresh(family)
    return FamilyResponse(
        id=str(family.id),
        family_name=family.family_name,
        created_by=family.created_by
    )

# Send an invite to an existing family member profile
@app.post("/api/family/invite")
def invite_member(req: InviteMemberRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member_or_none(user["uid"], db)
    if not user_member:
        raise HTTPException(status_code=404, detail="User profile not found")
    
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

# Accept an invitation
@app.post("/api/family/accept-invite")
def accept_invite(req: AcceptInviteRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    # Find the diner profile matching this invite token
    member = db.query(DBFamilyMember).filter(DBFamilyMember.invite_token == req.invite_token).first()
    if not member:
        raise HTTPException(status_code=404, detail="invalid or expired invite token")
    
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
    user_member = get_user_family_member_or_none(user["uid"], db)
    if not user_member:
        return [] # Return empty list if no family exists yet
    
    db_diners = db.query(DBFamilyMember).filter(DBFamilyMember.family_id == user_member.family_id).all()
    return [Diner(id=d.id, name=d.name, dislikes=d.dislikes, is_active=True, role=d.role, invite_accepted=d.invite_accepted, user_id=d.user_id) for d in db_diners]

# Add a diner to the family
@app.post("/api/diners", response_model=Diner)
def create_diner(diner: Diner, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member_or_none(user["uid"], db)
    if not user_member:
        raise HTTPException(status_code=400, detail="User must belong to a family to add diners")
    
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
        invite_accepted=db_diner.invite_accepted,
        user_id=db_diner.user_id
    )

# Update a diner profile (Family Head of the linked user only)
@app.put("/api/diners/{member_id}", response_model=Diner)
def update_diner(member_id: int, req: UpdateDinerRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member_or_none(user["uid"], db)
    if not user_member:
        raise HTTPException(status_code=400, detail="User profile not found")
    
    target_member = db.query(DBFamilyMember).filter(
        DBFamilyMember.id == member_id,
        DBFamilyMember.family_id == user_member.family_id
    ).first()

    if not target_member:
        raise HTTPException(status_code=404, detail="Diner profile not found in your family")
    
    if user_member.role != "head" and target_member.user_id != user["uid"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this diner profile")
    
    target_member.name = req.name
    target_member.dislikes = req.dislikes
    db.commit()
    db.refresh(target_member)

    return Diner(
        id=target_member.id,
        name=target_member.name,
        dislikes=target_member.dislikes,
        is_active=True,
        role=target_member.role,
        invite_accepted=target_member.invite_accepted,
        user_id=target_member.user_id
    )

# Delete a diner profile (Family Head only)
@app.delete("/api/diners/{member_id}")
def delete_user(member_id: int, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member_or_none(user["uid"], db)
    if not user_member:
        raise HTTPException(status_code=400, detail="User profile not found")
    
    if user_member.role != "head":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the family head can delete profiles")
    
    db_diner = db.query(DBFamilyMember).filter(
        DBFamilyMember.id == member_id,
        DBFamilyMember.family_id == user_member.family_id
    ).first()

    if not db_diner:
        raise HTTPException(status_code=404, detail="Diner profile not found in your family")
    
    if db_diner.role == "head":
        raise HTTPException(status_code=400, detail="Cannot delete the head of the family")
    
    db.delete(db_diner)
    db.commit()
    return {"message": "Diner profile deleted successfully"}

# Recommendation scopes within the active family
@app.post("/aip/recommend")
def recommend_restaurants(req: RecommendRequest, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_member = get_user_family_member_or_none(user["uid"])
    if not user_member:
        raise HTTPException(status_code=400, detail="User must belong to a family to request recommendations")
    
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