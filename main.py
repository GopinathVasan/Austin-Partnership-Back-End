import sys
import os
import logging
from fastapi import FastAPI, Request
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
    # allow_origins=["https://www.austinpartnership.in", "http://localhost:3000"],  # Add more origins as needed
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "PUT", "PATCH", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Cache-Control"]
)



# Middleware to log request headers (for debugging)
@app.middleware("http")
async def log_request_data(request: Request, call_next):
    logger.debug(f"Request Headers: {request.headers}")
    response = await call_next(request)
    return response

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
