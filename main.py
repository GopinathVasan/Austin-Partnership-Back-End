from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from database import get_db_connection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class UserLogin(BaseModel):
    username: str
    password: str



    # Add middleware to enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.post('/login')
async def login(user_login: UserLogin):
    username = user_login.username
    password = user_login.password

    # Check if username and password are provided
    if not username or not password:
        raise HTTPException(status_code=400, detail='Username and password are required')

    # Connect to the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the query to fetch user information
        query = "SELECT * FROM User WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))

        # Fetch the first row (user) from the result set
        user = cursor.fetchone()

        # Close the database connection
        cursor.close()
        conn.close()

        # Check if user exists
        if user:
            return {'message': 'Login successful', 'user': user}
        else:
            raise HTTPException(status_code=401, detail='Invalid username or password')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {e}')