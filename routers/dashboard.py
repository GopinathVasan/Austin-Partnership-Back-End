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

INVOICEQUERY = """SELECT ald.PROFILE_ID AS "id",
CONCAT(ald.FIRST_NAME,' ',ald.LAST_NAME)AS "name",
ald.PHONE as "phoneNumber",
ald.EMAIL AS "email",
AMOUNT_INVESTED as "cost",
DATE_FORMAT(DATE_OF_INVESTED,'%d/%m/%y') as "date"
FROM AP_LLP_DETAILS ald ,AP_LLP_INVESTMENTS a
WHERE ald.PROFILE_ID = a.PROFILE_ID 
ORDER BY DATE_OF_INVESTED DESC;"""


@router.get("/invoicebalance", response_model=List[Dict[str, Any]])
async def get_invoice(db: Session = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute(INVOICEQUERY)
        query_result = cursor.fetchall()
        cursor.close()
        
        # Convert query result into list of dictionaries
        result_list = [{"id": row[0],
                        "name": row[1],
                        "phoneNumber": row[2],
                        "email": row[3],
                        "totalInvestedAmount":row[4],
                        "date": row[5]} for row in query_result]
        
        return result_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
TEAMMEMBERS = """SELECT ald.PROFILE_ID AS "id",
CONCAT(ald.FIRST_NAME,' ',ald.LAST_NAME)AS "name",
`POSITION` AS "position",
ald.EMAIL AS "email",
ald.PHONE as "phoneNumber",
(SELECT IFNULL(SUM(AMOUNT_INVESTED),0) FROM AP_LLP_INVESTMENTS L
WHERE L.PROFILE_ID = ald.PROFILE_ID ) as "totalInvestedAmount"
FROM AP_LLP_DETAILS ald 
ORDER BY ald.ORDER;"""


@router.get("/teammembers", response_model=List[Dict[str, Any]])
async def get_team_members(db: Session = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute(TEAMMEMBERS)
        query_result = cursor.fetchall()
        cursor.close()
        
        # Convert query result into list of dictionaries
        result_list = [{"id": row[0],
                        "name": row[1],
                        "position": row[2],
                        "email": row[3],
                        "phoneNumber":row[4],
                        "totalInvestedAmount": row[5]} for row in query_result]
        
        return result_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


PROFITS ="""SELECT d.INVESTED_AMOUNT as "investedAmount",
d.REINVESTED_AMOUNT as "reinvestedAmount",
d.PROFIT_IN_AMOUNT as "revenueGenerated",
d.RETURNS as "returns",
d.COMPANY_EXPENSES "companyExpenses"
FROM AP_REVENUE_DETAILS d;"""


@router.get("/overallprofits", response_model=List[Dict[str, Any]])
async def get_overall_profits(db: Session = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute(PROFITS)
        query_result = cursor.fetchall()
        cursor.close()
        
        # Convert query result into list of dictionaries
        result_list = [{"investedAmount": row[0],
                        "reinvestedAmount": row[1],
                        "revenueGenerated": row[2],
                        "returns": row[3],
                        "companyExpenses":row[4]
                        } for row in query_result]
        
        return result_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


contact= """SELECT id as "id",
ald.PROFILE_ID AS "registerId",
CONCAT(ald.FIRST_NAME,' ',ald.LAST_NAME)AS "name",
ald.EMAIL AS "email",
ald.PHONE as "phoneNumber",
address as "address"
FROM AP_LLP_DETAILS ald ;"""



@router.get("/contactinformation", response_model=List[Dict[str, Any]])
async def get_contact_information(db: Session = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute(contact)
        query_result = cursor.fetchall()
        cursor.close()
        
        # Convert query result into list of dictionaries
        result_list = [{"id": row[0],
                        "registerId": row[1],
                        "name": row[2],
                        "email": row[3],
                        "phoneNumber":row[4],
                        "address":row[5]
                        } for row in query_result]
        
        return result_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

monthvalue= """SELECT SUM(D.REALISED_PL) as monthlyprofit, DATE_FORMAT(TRADE_DATE,'%M-%Y') as monthdate
FROM AP_LLP_DETAILS_DAY_TRADE_PROFITS D
GROUP BY DATE_FORMAT(TRADE_DATE,'%M-%Y') 
ORDER BY DATE_FORMAT(TRADE_DATE,'%M-%Y') DESC;"""



@router.get("/monthlyprofit", response_model=List[Dict[str, Any]])
async def get_contact_information(db: Session = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute(monthvalue)
        query_result = cursor.fetchall()
        cursor.close()
        
        # Convert query result into list of dictionaries
        result_list = [{"monthlyprofit": row[0],
                        "monthdate": row[1]
                        } for row in query_result]
        
        return result_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))