from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models, discord_bot
from pydantic import BaseModel

# Adatbázis táblák létrehozása
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Borsode CsomagPont API", version="1.0.PLUS_ULTRA")

# Pydantic sémák az adatok validálásához
class PackageCreate(BaseModel):
    tracking_number: str
    owner_id: int

class PackageUpdate(BaseModel):
    status: str

# Adatbázis session kezelő
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/packages/")
def create_package(pkg: PackageCreate, db: Session = Depends(get_db)):
    db_pkg = models.Package(tracking_number=pkg.tracking_number, owner_id=pkg.owner_id)
    db.add(db_pkg)
    db.commit()
    db.refresh(db_pkg)
    discord_bot.send_status_update(pkg.tracking_number, "Nincs", "Feldolgozás alatt (Új)")
    return db_pkg

@app.put("/packages/{tracking_number}")
def update_package(tracking_number: str, pkg_update: PackageUpdate, db: Session = Depends(get_db)):
    db_pkg = db.query(models.Package).filter(models.Package.tracking_number == tracking_number).first()
    if not db_pkg:
        raise HTTPException(status_code=404, detail="Csomag nem található")
    
    old_status = db_pkg.status
    db_pkg.status = pkg_update.status
    db.commit()
    
    discord_bot.send_status_update(tracking_number, old_status, pkg_update.status)
    return {"message": "Sikeres frissítés", "status": pkg_update.status}

@app.get("/packages/{tracking_number}")
def get_package(tracking_number: str, db: Session = Depends(get_db)):
    db_pkg = db.query(models.Package).filter(models.Package.tracking_number == tracking_number).first()
    if not db_pkg:
        raise HTTPException(status_code=404, detail="Csomag nem található")
    return db_pkg
