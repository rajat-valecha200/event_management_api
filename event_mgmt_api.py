from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, timedelta
from typing import List, Optional
import csv
import enum


DATABASE_URL = "sqlite:///./events.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EventStatus(str, enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"

class Event(Base):
    __tablename__ = "events"
    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    location = Column(String)
    max_attendees = Column(Integer)
    status = Column(Enum(EventStatus), default=EventStatus.scheduled)

class Attendee(Base):
    __tablename__ = "attendees"
    attendee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    check_in_status = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events/")
def create_event(name: str, description: str, start_time: datetime, end_time: datetime, location: str, max_attendees: int, db: Session = Depends(get_db)):
    event = Event(name=name, description=description, start_time=start_time, end_time=end_time, location=location, max_attendees=max_attendees, status=EventStatus.scheduled)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@app.put("/events/{event_id}")
def update_event(event_id: int, name: Optional[str] = None, description: Optional[str] = None, status: Optional[EventStatus] = None, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if name:
        event.name = name
    if description:
        event.description = description
    if status:
        event.status = status
    db.commit()
    return event

@app.post("/attendees/")
def register_attendee(first_name: str, last_name: str, email: str, phone_number: str, event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if db.query(Attendee).filter(Attendee.event_id == event_id).count() >= event.max_attendees:
        raise HTTPException(status_code=400, detail="Event is at full capacity")
    attendee = Attendee(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, event_id=event_id)
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    return attendee

@app.put("/attendees/{attendee_id}/check-in")
def check_in_attendee(attendee_id: int, db: Session = Depends(get_db)):
    attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    attendee.check_in_status = True
    db.commit()
    return {"message": "Check-in successful"}

@app.get("/events/")
def list_events(status: Optional[EventStatus] = None, location: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Event)
    if status:
        query = query.filter(Event.status == status)
    if location:
        query = query.filter(Event.location == location)
    return query.all()

@app.get("/attendees/")
def list_attendees(event_id: int, db: Session = Depends(get_db)):
    return db.query(Attendee).filter(Attendee.event_id == event_id).all()

@app.post("/attendees/bulk-check-in/")
def bulk_check_in(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8").splitlines()
    reader = csv.reader(content)
    for row in reader:
        attendee_id = int(row[0])
        attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()
        if attendee:
            attendee.check_in_status = True
    db.commit()
    return {"message": "Bulk check-in completed"}

@app.on_event("startup")
def auto_update_event_status():
    db = SessionLocal()
    current_time = datetime.utcnow()
    events = db.query(Event).all()
    for event in events:
        if event.end_time < current_time:
            event.status = EventStatus.completed
    db.commit()
    db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
