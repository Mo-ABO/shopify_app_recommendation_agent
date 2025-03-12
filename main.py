from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
from config import settings as s
from pydantic import BaseModel
from chains.langchain_agent import get_recommendation
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.security import create_access_token, verify_token
from datetime import timedelta
from auth.security import get_current_user


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# data model for incoming requests
class RecommendationRequest(BaseModel):
    query: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Shopify App Recommendation Agent")

fake_user_db = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Doe",
        "hashed_password": "fakehashedpassword",
    }
}

def fake_hash_password(password: str):
    return "fakehashed" + password

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_user_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    hashed_password = fake_hash_password(form_data.password)
    if hashed_password != user_dict["hashed_password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_dict["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Shopify App Recommendation Agent API!"}

@app.post("/v1/ai/recom-app")
async def recommend_app(request: RecommendationRequest):
    try:
        db_path = s.db_path
        logger.info("Received query: %s", request.query)
        
        # generate recommendation using hybrid context (semantic and keywords)
        recommendation = get_recommendation(request.query, db_path)
        logger.info("Generated recommendation: %s", recommendation)
        
        return {"recommendations": [recommendation]}
    
    except Exception as e:
        logger.error("Error processing request: %s", e, exc_info=True)
        return {"error": "Internal server error"}



if __name__ == "__main__":
    # import sys
    # print(sys.executable)
    # print(sys.path)

    uvicorn.run("main:app", host="127.0.0.1", port=s.port, reload=True)