"""
Database Schemas for Droomwoordjes Webshop

Each Pydantic model represents a MongoDB collection. The collection name
is the lowercase class name by convention (e.g., Product -> "product").
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="URL friendly slug")
    description: str = Field(..., description="Long description")
    short_description: str = Field(..., description="Short teaser")
    price: float = Field(..., ge=0, description="Price in euros")
    currency: str = Field("eur", description="ISO currency code")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    features: List[str] = Field(default_factory=list, description="Key benefits/features")
    in_stock: bool = Field(True, description="Whether product is in stock")
    stripe_price_id: Optional[str] = Field(None, description="Stripe Price ID for Checkout")

class OrderItem(BaseModel):
    product_id: Optional[str] = Field(None, description="Reference to product _id")
    title: str
    quantity: int = Field(..., ge=1)
    unit_amount: int = Field(..., ge=0, description="Amount in cents")

class Order(BaseModel):
    email: Optional[str] = None
    items: List[OrderItem]
    amount_total: int = Field(..., ge=0)
    currency: str = Field("eur")
    stripe_session_id: Optional[str] = None
    status: str = Field("created", description="created|paid|canceled")

class Testimonial(BaseModel):
    name: str
    role: Optional[str] = None
    quote: str

class ContactMessage(BaseModel):
    name: str
    email: str
    message: str
