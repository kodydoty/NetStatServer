
import uuid  # Import uuid to generate API keys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models, schemas  # Import schemas

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user.dict(), api_key=str(uuid.uuid4()))  # Generate and assign API key
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_speedtest(db: AsyncSession, speedtest: schemas.SpeedTestCreate):
    db_speedtest = models.SpeedTest(**speedtest.dict())
    db.add(db_speedtest)
    await db.commit()
    await db.refresh(db_speedtest)
    return db_speedtest

async def get_user_by_api_key(db: AsyncSession, api_key: str):
    result = await db.execute(select(models.User).where(models.User.api_key == api_key))
    return result.scalar_one_or_none()

async def get_speedtests(db: AsyncSession, isp: str = None, zipcode: str = None):
    query = select(models.SpeedTest)
    if isp:
        query = query.where(models.SpeedTest.isp == isp)
    if zipcode:
        query = query.where(models.SpeedTest.zipcode == zipcode)
    result = await db.execute(query)
    return result.scalars().all()

async def get_speedtests_by_isp_and_zipcode(db: AsyncSession, isp: str, zipcode: str):
    query = select(models.SpeedTest).where(models.SpeedTest.isp == isp, models.SpeedTest.zipcode == zipcode)
    result = await db.execute(query)
    return result.scalars().all()
