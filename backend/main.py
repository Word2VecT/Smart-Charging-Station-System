import asyncio
from contextlib import asynccontextmanager

from app.database import SessionLocal
from app.queue_manager import queue_manager
from app.routers import admin as admin_router
from app.routers import admin_auth as admin_auth_router
from app.routers import admin_resources  # 假设你把上面新路由放这里
from app.routers import auth as auth_router
from app.routers import history as history_router
from app.routers import orders as orders_router
from app.routers import requests as requests_router
from app.services.charging_monitor_service import charging_monitor_service
from app.services.scheduling_service import scheduling_service
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


async def run_scheduler_periodically():
    """Background task to run the scheduler periodically."""
    while True:
        await asyncio.sleep(10)  # Run every 10 seconds
        print("Running scheduler...")
        async with SessionLocal() as db_session:
            try:
                await scheduling_service.schedule_next_vehicle(db_session)
            except Exception as e:
                print(f"An error occurred in the scheduler: {e}")


async def run_monitor_periodically():
    """Background task to run the charging monitor periodically."""
    while True:
        await asyncio.sleep(5)  # Run every 5 seconds
        print("Running charging monitor...")
        async with SessionLocal() as db_session:
            try:
                await charging_monitor_service.check_completed_charges(db_session)
            except Exception as e:
                print(f"An error occurred in the charging monitor: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    print("Application startup: Initializing QueueManager...")
    async with SessionLocal() as db_session:
        try:
            await queue_manager.initialize(db_session)
        except Exception as e:
            print(f"Error initializing QueueManager: {e}")
            # Consider exiting if initialization is critical and fails

    # Start background tasks
    scheduler_task = asyncio.create_task(run_scheduler_periodically())
    monitor_task = asyncio.create_task(run_monitor_periodically())
    print("Scheduler and Monitor have been started.")

    yield

    # On shutdown
    scheduler_task.cancel()
    monitor_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        print("Scheduler task has been cancelled.")
    try:
        await monitor_task
    except asyncio.CancelledError:
        print("Monitor task has been cancelled.")
    print("Application shutdown.")


app = FastAPI(
    title="Smart Charging Station Management System",
    description="API for managing EV charging, queuing, and billing.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # Default Nuxt.js port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(requests_router.router)
app.include_router(admin_router.router)
app.include_router(orders_router.router)
app.include_router(history_router.router)
app.include_router(admin_auth_router.router)
app.include_router(admin_resources.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Smart Charging Station API"}


# To run this application:
# uvicorn uv run --cwd backend uvicorn main:app --reload
