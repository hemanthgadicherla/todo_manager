from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. Create the application instance
app = FastAPI()

# --- DATABASE SETUP (The "Restaurant Infrastructure") ---
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    time = Column(String)

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# The "Waiter Manager" (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

list1 = [
    {"id": 1, "data": {"title": "Buy Milk", "description": "Get 2L of semi-skimmed milk", "time": "08:00 AM"}},
    {"id": 2, "data": {"title": "Workout", "description": "Morning cardio and weights", "time": "07:00 AM"}},
    {"id": 3, "data": {"title": "Meeting", "description": "Sync with the design team", "time": "10:00 AM"}},
    {"id": 4, "data": {"title": "Code Review", "description": "Review PRs for the new API", "time": "02:00 PM"}},
    {"id": 5, "data": {"title": "Grocery Shopping", "description": "Buy vegetables and fruits", "time": "06:00 PM"}}
]

# Global counter for IDs matching the seeded data
todo_index = 5

class TodoItem(BaseModel):
    title: str
    description: str
    time: str

# class calculate(BaseModel):
#     num1: int
#     num2: int

# class UserProfile(BaseModel):
#     first_name: str
#     last_name: str

# # 2. Define a root endpoint
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to my first FastAPI!"}

# # 3. Define an endpoint with a parameter
# @app.get("/hello/{name}")
# def say_hello(name: str):
#     return {"message": f"Hello, {name}!"}

# @app.post("/profile")
# def create_profile(profile: UserProfile):
#     # This automatically converts JSON input into a Python object!
#     fullname = f"{profile.first_name} {profile.last_name}"
#     return {"status": "Success", "full_name": fullname}

# @app.post("/math")
# def cal(math1: calculate): 
#     sum1 = math1.num1 + math1.num2
#     multiplication = math1.num1 * math1.num2
#     return {"status": "Success", "sum": sum1, "multiplication": multiplication}

@app.post("/todoapp")
def create_todo(todo: TodoItem):
    global todo_index
    todo_index += 1
    # Adding ID to the record
    todo_record = {"id": todo_index, "data": todo}
    list1.append(todo_record)
    return {"status": "Success", "todo": todo_record}

# --- NEW: POST TODO TO DATABASE ---
@app.post("/db/todoapp")
def create_todo_db(todo: TodoItem, db: Session = Depends(get_db)):
    # 1. Create the object (The Plate)
    new_todo = Todo(title=todo.title, description=todo.description, time=todo.time)
    # 2. Add to context
    db.add(new_todo)
    # 3. Commit to Postgres
    db.commit()
    # 4. Refresh to get ID
    db.refresh(new_todo)
    return {"status": "Success", "todo": new_todo}

@app.get("/todoapp/{id}")
def get_todo(id: int):
    for i in list1:
        if i["id"]==id:
            return {"status": "Success", "todo": i}
    return {"status": "Error", "todo": "not found"}


@app.delete("/todoapp/{id}")
def delete_todo(id: int):
    for i in list1:
        if i["id"] == id:
            list1.remove(i)
            return {"status": "Success", "todo": f"deleted {id}", "list": list1}
    return {"status": "Error", "todo": "not found"}

@app.put("/todoapp/{id}")
def update_todo(id: int, todo: TodoItem):
    for i in list1:
        if i["id"] == id:
            i["data"] = todo
            return {"status": "Success", "todo": f"updated {id}", "list": list1}
    return {"status": "Error", "todo": "not found"}
