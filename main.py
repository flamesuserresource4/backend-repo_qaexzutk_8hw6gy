import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem, Testimonial, ContactMessage

app = FastAPI(title="Droomwoordjes Webshop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Droomwoordjes API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Product Endpoints
@app.get("/api/products", response_model=List[Product])
def list_products():
    items = get_documents("product")
    # Convert Mongo _id to string and ensure fields exist
    result = []
    for it in items:
        it.pop("_id", None)
        result.append(Product(**it))
    return result

@app.post("/api/products", response_model=str)
def create_product(product: Product):
    inserted_id = create_document("product", product)
    return inserted_id

@app.get("/api/products/{slug}", response_model=Product)
def get_product(slug: str):
    docs = get_documents("product", {"slug": slug}, limit=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Product not found")
    doc = docs[0]
    doc.pop("_id", None)
    return Product(**doc)

# Testimonials
@app.get("/api/testimonials", response_model=List[Testimonial])
def list_testimonials():
    docs = get_documents("testimonial")
    res = []
    for d in docs:
        d.pop("_id", None)
        res.append(Testimonial(**d))
    return res

@app.post("/api/testimonials", response_model=str)
def create_testimonial(t: Testimonial):
    return create_document("testimonial", t)

# Contact
@app.post("/api/contact", response_model=str)
def send_contact(msg: ContactMessage):
    return create_document("contactmessage", msg)

# Simple cart/checkout scaffolding (without Stripe yet)
class CartItem(BaseModel):
    slug: str
    title: str
    quantity: int
    unit_amount: int

class CreateOrderRequest(BaseModel):
    email: Optional[str] = None
    items: List[CartItem]

@app.post("/api/orders", response_model=str)
def create_order(req: CreateOrderRequest):
    # Calculate totals
    total = sum(i.quantity * i.unit_amount for i in req.items)
    order_items = [
        OrderItem(product_id=None, title=i.title, quantity=i.quantity, unit_amount=i.unit_amount)
        for i in req.items
    ]
    order = Order(email=req.email, items=order_items, amount_total=total, currency="eur", status="created")
    return create_document("order", order)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
