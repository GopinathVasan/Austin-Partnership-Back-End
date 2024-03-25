
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from database import Base
from fastapi.middleware.cors import CORSMiddleware



router = APIRouter()


class UserLogin(BaseModel):
    username: str
    password: str



    # Add middleware to enable CORS

@router.post('/login')
async def login(user_login: UserLogin):
    username = user_login.username
    password = user_login.password

    # Check if username and password are provided
    if not username or not password:
        raise HTTPException(status_code=400, detail='Username and password are required')

    # Connect to the database
    try:
        conn = Base()
        cursor = conn.cursor()

        # Execute the query to fetch user information
        query = "SELECT * FROM USER WHERE username = %s AND password = %s"
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