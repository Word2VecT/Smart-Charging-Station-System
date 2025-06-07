import asyncio

# Import the Base from your models file
from app.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

# Your database URL
DATABASE_URL = "postgresql+asyncpg://tang@localhost:5432/charge"


async def create_tables():
    print("Connecting to the database...")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        print("Dropping all existing tables...")
        # Drop all tables managed by Base
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all new tables...")
        # Create all tables defined in your models
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables())
