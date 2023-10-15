import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal
import database
import crud, models, schemas
import redis
from typing import List
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_weather_data(zipcode: str):
    """Fetch weather data for a given ZIP code."""
    # Replace with actual API key and URL
    api_key = os.getenv('api_key')
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"zip": zipcode, "appid": api_key}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, params=params) as response:
            # Handle API request failure
            if response.status != 200:
                return None
            
            weather_data = await response.json()
            # Extract relevant weather information (adjust according to actual API response structure)
            temperature = int(weather_data['main']['temp'] * 9/5 - 459.67)  # Convert KtoF
            condition = weather_data['weather'][0]['description'].capitalize()
            
            return {"temperature": temperature, "condition": condition}
        
app = FastAPI()
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip_address = str(request.client.host)
    key = f"rate_limit:{ip_address}"
    current_count = redis_client.get(key)
    
    if current_count is None:
        redis_client.set(key, 1, ex=60)
    elif int(current_count) >= 10:
        raise HTTPException(status_code=429, detail="Too many requests")
    else:
        redis_client.incr(key)
        
    response = await call_next(request)
    return response

@app.on_event("startup")
async def startup():
    await database.create_tables()
    logger.info("Application started and tables created.")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutdown.")

async def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()

@app.post("/users/", response_model=schemas.UserCreated)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating user: {user.username}")
    db_user = await crud.create_user(db, user)
    return db_user


@app.post("/speedtests/")
async def create_speedtest(speedtest: schemas.SpeedTestCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating speedtest: {speedtest}")
    try:
        # Fetch weather data
        weather_data = await get_weather_data(speedtest.zipcode)
        if weather_data is not None:
            speedtest.temperature = weather_data['temperature']
            speedtest.condition = weather_data['condition']
        
        # Store the speedtest result, now including weather data, in the database
        await crud.create_speedtest(db, speedtest)
        return JSONResponse(content={"message": "Successful upload"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed to create speedtest: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{api_key}", response_model=schemas.UserRead)
async def get_user(api_key: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Getting user: {api_key}")
    db_user = await crud.get_user_by_api_key(db, api_key)
    if db_user is None:
        logger.warning(f"User not found: {api_key}")
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/speedtests/", response_model=List[schemas.SpeedTestRead])
async def get_speedtests(isp: str = None, zipcode: str = None, db: AsyncSession = Depends(get_db)):
    logger.info(f"Getting speedtests: isp={isp}, zipcode={zipcode}")
    db_speedtests = await crud.get_speedtests(db, isp=isp, zipcode=zipcode)
    return db_speedtests

@app.get("/speedtests/{isp}/{zipcode}", response_model=List[schemas.SpeedTestRead])
async def get_speedtests_by_isp_and_zipcode(isp: str, zipcode: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Getting speedtests: isp={isp}, zipcode={zipcode}")
    db_speedtests = await crud.get_speedtests_by_isp_and_zipcode(db, isp, zipcode)
    return db_speedtests
