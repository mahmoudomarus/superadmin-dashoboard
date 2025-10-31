from fastapi import APIRouter
from app.api.v1 import auth, users, verification, properties, bookings, hosts

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(verification.router)
api_router.include_router(properties.router)
api_router.include_router(bookings.router)
api_router.include_router(hosts.router)

