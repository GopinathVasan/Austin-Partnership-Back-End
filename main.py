from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth,users,forgotpassword,otp,dashboard


# /clientlogin

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://www.austinpartnership.in"],
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(forgotpassword.router)
app.include_router(otp.router)
app.include_router(dashboard.router)    
