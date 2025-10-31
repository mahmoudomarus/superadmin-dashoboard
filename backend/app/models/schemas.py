from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

# Enums
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ANALYST = "analyst"

class UserType(str, Enum):
    HOST = "host"
    AGENT = "agent"
    CUSTOMER = "customer"
    GUEST = "guest"

class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class PlatformStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# User Schemas
class UnifiedUserResponse(BaseModel):
    id: str
    email: str
    platform_id: str
    platform_user_id: str
    user_type: UserType
    full_name: Optional[str] = None
    phone: Optional[str] = None
    verification_status: Optional[str] = None
    account_status: AccountStatus
    last_synced_at: Optional[datetime] = None
    created_at: datetime

class UpdateUserStatusRequest(BaseModel):
    status: AccountStatus
    reason: Optional[str] = None

# Property Schemas
class UnifiedPropertyResponse(BaseModel):
    id: str
    platform_id: str
    platform_property_id: str
    owner_user_id: str
    title: str
    property_type: str
    listing_type: str
    city: Optional[str] = None
    price: float
    price_currency: str = "AED"
    status: str
    is_featured: bool = False
    last_synced_at: Optional[datetime] = None
    created_at: datetime

class UpdatePropertyRequest(BaseModel):
    status: Optional[str] = None
    is_featured: Optional[bool] = None

# Booking Schemas
class UnifiedBookingResponse(BaseModel):
    id: str
    platform_id: str
    platform_booking_id: str
    property_id: str
    guest_user_id: str
    host_user_id: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    payment_status: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime

class CancelBookingRequest(BaseModel):
    reason: str

# Verification Schemas
class VerificationQueueItem(BaseModel):
    id: str
    platform_id: str
    user_id: str
    platform_user_id: str
    verification_type: str
    status: VerificationStatus
    documents: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ApproveVerificationRequest(BaseModel):
    notes: str

class RejectVerificationRequest(BaseModel):
    reason: str
    notes: Optional[str] = None

class RequestResubmissionRequest(BaseModel):
    reason: str

# Platform Schemas
class PlatformResponse(BaseModel):
    id: str
    name: str
    display_name: str
    api_base_url: str
    status: PlatformStatus
    last_health_check: Optional[datetime] = None
    created_at: datetime

class PlatformHealthResponse(BaseModel):
    platform_id: str
    name: str
    status: PlatformStatus
    is_healthy: bool
    response_time_ms: Optional[int] = None
    last_checked: datetime

# Analytics Schemas
class PlatformStats(BaseModel):
    total_users: int
    total_properties: int
    total_bookings: int
    total_revenue: float
    active_bookings: int

class DashboardMetrics(BaseModel):
    total_users: int
    total_properties: int
    total_bookings: int
    total_revenue: float
    platforms: List[PlatformStats]
    recent_verifications: int
    pending_verifications: int

# Admin Action Schemas
class AdminActionLog(BaseModel):
    id: str
    admin_user_id: str
    action_type: str
    target_platform: Optional[str] = None
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    action_details: Dict[str, Any]
    created_at: datetime

# Response Wrappers
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel):
    data: List[Any]
    page: int
    limit: int
    total: int
    total_pages: int

