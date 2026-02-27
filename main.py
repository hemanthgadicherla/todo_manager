from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. Create the application instance
app = FastAPI()

# Database Setup
# !!! IMPORTANT: Replace 'YOUR_PASSWORD' with your actual PostgreSQL password !!!
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model (Matches your PostgreSQL table)
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    time = Column(String(50))

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Model for API requests
class TodoItem(BaseModel):
    title: str
    description: str
    time: str

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI with PostgreSQL!"}

@app.post("/todoapp")
def create_todo(todo: TodoItem, db: Session = Depends(get_db)):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        time=todo.time
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return {"status": "Success", "todo": db_todo}

@app.get("/todoapp/{id}")
def get_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo:
        return {"status": "Success", "todo": todo}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todoapp/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo:
        db.delete(todo)
        db.commit()
        return {"status": "Success", "message": f"Deleted todo with ID {id}"}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/todoapp/{id}")
def update_todo(id: int, todo: TodoItem, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == id).first()
    if db_todo:
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.time = todo.time
        db.commit()
        db.refresh(db_todo)
        return {"status": "Success", "todo": db_todo}
    raise HTTPException(status_code=404, detail="Todo not found")
