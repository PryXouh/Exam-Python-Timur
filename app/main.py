from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, Literal
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import IntegrityError

SQLALCHEMY_DATABASE_URL = "sqlite:///./stations.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StationDB(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String, default="open", nullable=False)

Base.metadata.create_all(bind=engine)

class StationCreate(BaseModel):
    code: str
    name: str
    capacity: int = Field(ge=1)
    status: Literal["open", "closed", "maintenance"] = "open"

class StationUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[Literal["open", "closed", "maintenance"]] = None

class StationResponse(BaseModel):
    id: int
    code: str
    name: str
    capacity: int
    status: str
    
    class Config:
        from_attributes = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/stations", status_code=status.HTTP_201_CREATED, response_model=StationResponse)
def create_station(station: StationCreate, db: Session = Depends(get_db)):
    db_station = StationDB(**station.model_dump())
    try:
        db.add(db_station)
        db.commit()
        db.refresh(db_station)
        return db_station
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Code déjà utilisé")

@app.get("/stations", response_model=list[StationResponse])
def get_stations(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(StationDB)
    if status:
        query = query.filter(StationDB.status == status)
    return query.all()

@app.get("/stations/{station_id}", response_model=StationResponse)
def get_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(StationDB).filter(StationDB.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station introuvable")
    return station

@app.patch("/stations/{station_id}", response_model=StationResponse)
def update_station(station_id: int, updates: StationUpdate, db: Session = Depends(get_db)):
    station = db.query(StationDB).filter(StationDB.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station introuvable")
    
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(station, key, value)
    
    db.commit()
    db.refresh(station)
    return station