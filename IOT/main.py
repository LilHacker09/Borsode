from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models, discord_bot
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Borsode CsomagPont API", version="1.0.PLUS_ULTRA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PackageCreate(BaseModel):
    tracking_number: str
    owner_id: int

class PackageUpdate(BaseModel):
    status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def serve_frontend():
    return FileResponse("index.html")


@app.post("/packages/")
def create_package(pkg: PackageCreate, db: Session = Depends(get_db)):
 
    existing_pkg = db.query(models.Package).filter(models.Package.tracking_number == pkg.tracking_number).first()
    if existing_pkg:
        raise HTTPException(status_code=400, detail="Ez a csomagszám már létezik a rendszerben!")

    db_pkg = models.Package(tracking_number=pkg.tracking_number, owner_id=pkg.owner_id)
    db.add(db_pkg)
    db.commit()
    db.refresh(db_pkg)
    
    
    try:
        discord_bot.send_status_update(pkg.tracking_number, "Nincs", "Feldolgozás alatt (Új)")
    except Exception as e:
        print(f"Hiba a Discord webhook küldésekor: {e}")
        
    return db_pkg


@app.put("/packages/{tracking_number}")
def update_package(tracking_number: str, pkg_update: PackageUpdate, db: Session = Depends(get_db)):
    db_pkg = db.query(models.Package).filter(models.Package.tracking_number == tracking_number).first()
    if not db_pkg:
        raise HTTPException(status_code=404, detail="Csomag nem található")
    
    old_status = db_pkg.status
    db_pkg.status = pkg_update.status
    db.commit()
    
    try:
        discord_bot.send_status_update(tracking_number, old_status, pkg_update.status)
    except Exception as e:
        print(f"Hiba a Discord webhook küldésekor: {e}")
        
    return {"message": "Sikeres frissítés", "status": pkg_update.status}

@app.get("/packages/{tracking_number}")
def get_package(tracking_number: str, db: Session = Depends(get_db)):
    db_pkg = db.query(models.Package).filter(models.Package.tracking_number == tracking_number).first()
    if not db_pkg:
        raise HTTPException(status_code=404, detail="Csomag nem található")
    return db_pkg
