from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db_connection
from typing import List, Dict, Any

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={401: {"user": "Not authorized"}}
)

RECENTTRANQUERY = """SELECT PROFILE_ID AS profileId,
                   CONCAT(FIRST_NAME, ' ', LAST_NAME) AS customerName,
                   DATE_FORMAT(DATE_OF_INVESTED, '%Y %M') AS investedDate,
                   AMOUNT_INVESTED AS amount 
            FROM AP_LLP_INVESTMENTS
            ORDER BY DATE_OF_INVESTED DESC;"""

@router.get("/investments", response_model=List[Dict[str, Any]])
async def get_investments(db: Session = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute(RECENTTRANQUERY)
        query_result = cursor.fetchall()
        cursor.close()
        
        # Convert query result into list of dictionaries
        result_list = [{"profileId": row[0],
                        "customerName": row[1],
                        "investedDate": row[2],
                        "amount": row[3]} for row in query_result]
        
        return result_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

