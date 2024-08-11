import sys
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, users, forgotpassword, otp, dashboard

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3001"],  # Replace with your frontend URL
    allow_origins=["https://www.austinpartnership.in"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(forgotpassword.router)
app.include_router(otp.router)
app.include_router(dashboard.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
