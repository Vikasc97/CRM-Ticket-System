from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models

from datetime import datetime
import random

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# HOME PAGE
@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    db: Session = Depends(get_db),
    search: str = "",
    status: str = "",
    priority: str = ""
):

    query = db.query(models.Ticket)

    if search:
        query = query.filter(
            models.Ticket.customer_name.contains(search) |
            models.Ticket.customer_email.contains(search) |
            models.Ticket.subject.contains(search) |
            models.Ticket.description.contains(search)
        )

    if status:
        query = query.filter(models.Ticket.status == status)

    if priority:
        query = query.filter(models.Ticket.priority == priority)

    tickets = query.all()

    all_tickets = db.query(models.Ticket).all()
    count_open = sum(1 for t in all_tickets if t.status == "Open")
    count_in_progress = sum(1 for t in all_tickets if t.status == "In Progress")
    count_closed = sum(1 for t in all_tickets if t.status == "Closed")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tickets": tickets,
            "count_open": count_open,
            "count_in_progress": count_in_progress,
            "count_closed": count_closed,
        }
    )

# CREATE PAGE
@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create.html",
        context={}
    )

# CREATE TICKET
@app.post("/create")
def create_ticket(
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db)
):

    random_id = f"TKT-{random.randint(1000,9999)}"

    new_ticket = models.Ticket(
        ticket_id=random_id,
        customer_name=customer_name,
        customer_email=customer_email,
        subject=subject,
        description=description,
        priority=priority,
    )

    db.add(new_ticket)
    db.commit()

    return RedirectResponse("/", status_code=303)

# TICKET DETAIL PAGE
@app.get("/ticket/{ticket_id}", response_class=HTMLResponse)
def ticket_detail(
    request: Request,
    ticket_id: str,
    db: Session = Depends(get_db)
):

    ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        return RedirectResponse("/", status_code=302)

    history = db.query(models.TicketHistory).filter(
        models.TicketHistory.ticket_id == ticket_id
    ).order_by(models.TicketHistory.changed_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={"ticket": ticket, "history": history}
    )

# DELETE TICKET
@app.post("/delete/{ticket_id}")
def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id
    ).first()

    if ticket:
        db.delete(ticket)
        db.commit()

    return RedirectResponse("/", status_code=303)

# UPDATE TICKET
@app.post("/update/{ticket_id}")
def update_ticket(
    ticket_id: str,
    status: str = Form(...),
    priority: str = Form("Medium"),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):

    ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id
    ).first()

    if ticket.status != status:
        db.add(models.TicketHistory(
            ticket_id=ticket_id,
            field="Status",
            old_value=ticket.status,
            new_value=status
        ))

    if ticket.priority != priority:
        db.add(models.TicketHistory(
            ticket_id=ticket_id,
            field="Priority",
            old_value=ticket.priority,
            new_value=priority
        ))

    ticket.status = status
    ticket.priority = priority
    ticket.notes = notes
    ticket.updated_at = datetime.utcnow()

    db.commit()

    return RedirectResponse(
        f"/ticket/{ticket_id}",
        status_code=303
    )
