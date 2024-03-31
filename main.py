from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth,users


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://austinpartnership.in"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)    