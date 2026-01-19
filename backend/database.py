from pymongo import MongoClient
from datetime import datetime
import os
import uuid

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URL", os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
client = MongoClient(MONGO_URI)
db = client["costar_scraper"]

# Collections
properties_collection = db["properties"]

# Create indexes
properties_collection.create_index("costar_id", unique=True)
properties_collection.create_index([("city", 1), ("state", 1)])
properties_collection.create_index("created_at")


def property_exists(costar_id: str) -> bool:
    """Check if property already exists."""
    return properties_collection.find_one({"costar_id": costar_id}) is not None


def insert_property(property_data: dict) -> dict:
    """Insert a new property if it doesn't exist."""
    if not property_data.get("costar_id"):
        return None
    
    if property_exists(property_data.get("costar_id")):
        return None
    
    # Use UUID instead of ObjectId for JSON serialization
    property_data["id"] = str(uuid.uuid4())
    property_data["created_at"] = datetime.utcnow()
    property_data["updated_at"] = datetime.utcnow()
    
    result = properties_collection.insert_one(property_data)
    property_data["_id"] = str(result.inserted_id)
    return property_data


def get_properties(
    city: str = None,
    state: str = None,
    property_type: str = None,
    search_name: str = None,
    skip: int = 0,
    limit: int = 50
) -> list:
    """Get properties with filters."""
    query = {}
    
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if state:
        query["state"] = state.upper()
    if property_type:
        query["property_type"] = {"$regex": property_type, "$options": "i"}
    if search_name:
        query["search_name"] = {"$regex": search_name, "$options": "i"}
    
    cursor = properties_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
    
    properties = []
    for prop in cursor:
        prop["_id"] = str(prop["_id"])
        if prop.get("email_date"):
            prop["email_date"] = prop["email_date"].isoformat() if hasattr(prop["email_date"], 'isoformat') else str(prop["email_date"])
        if prop.get("created_at"):
            prop["created_at"] = prop["created_at"].isoformat() if hasattr(prop["created_at"], 'isoformat') else str(prop["created_at"])
        properties.append(prop)
    
    return properties


def get_property_count() -> int:
    """Get total property count."""
    return properties_collection.count_documents({})


def get_property_stats() -> dict:
    """Get aggregate statistics."""
    total = properties_collection.count_documents({})
    
    # Count by state
    by_state = list(properties_collection.aggregate([
        {"$group": {"_id": "$state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]))
    
    # Count by property type
    by_type = list(properties_collection.aggregate([
        {"$match": {"property_type": {"$ne": None}}},
        {"$group": {"_id": "$property_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]))
    
    return {
        "total_properties": total,
        "by_state": {item["_id"]: item["count"] for item in by_state if item["_id"]},
        "by_type": {item["_id"]: item["count"] for item in by_type if item["_id"]}
    }


def seed_sample_properties() -> int:
    """Seed database with sample properties from the CoStar email PDF."""
    sample_properties = [
        {
            "costar_id": "1431229",
            "address": "2695 Gilchrist Rd",
            "city": "Akron",
            "state": "OH",
            "zip_code": "44305",
            "property_type": "Fast Food",
            "square_feet": "3,591",
            "year_built": "1990",
            "price": "$1",
            "price_per_sf": "$0.00/SF",
            "image_url": "https://images.unsplash.com/photo-1606787364406-a3cdf06c6d0c?w=400&h=300&fit=crop",
            "search_name": "Ohio 70 Mile"
        },
        {
            "costar_id": "1431230",
            "address": "5706 Heinton Rd",
            "city": "Valley View",
            "state": "OH",
            "zip_code": "44125",
            "property_type": "Commercial Vacant Land",
            "square_feet": "513,572 SF (11.79 AC)",
            "year_built": None,
            "price": "$3,000,000",
            "price_per_sf": "$254,452.93/AC",
            "image_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=300&fit=crop",
            "search_name": "Ohio 70 Mile"
        },
        {
            "costar_id": "1431231",
            "address": "399 Adams St",
            "city": "Rochester",
            "state": "PA",
            "zip_code": "15074",
            "property_type": "Retail",
            "square_feet": "1,920",
            "year_built": "1900",
            "price": "$150,000",
            "price_per_sf": "$78.13/SF",
            "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop",
            "search_name": "Pennsylvania"
        },
        {
            "costar_id": "1431232",
            "address": "3107 Market St",
            "city": "Youngstown",
            "state": "OH",
            "zip_code": "44507",
            "property_type": "Commercial Land",
            "square_feet": "25,788 SF (0.59 AC)",
            "year_built": None,
            "price": "$80,000",
            "price_per_sf": "$135,135.14/AC",
            "image_url": "https://images.unsplash.com/photo-1448630360428-65456885c650?w=400&h=300&fit=crop",
            "search_name": "Ohio 70 Mile"
        },
        {
            "costar_id": "1431233",
            "address": "610 New York Ave",
            "city": "Rochester",
            "state": "PA",
            "zip_code": "15074",
            "property_type": "Warehouse",
            "square_feet": "7,260",
            "year_built": "1980",
            "price": "$475,000",
            "price_per_sf": "$65.43/SF",
            "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=300&fit=crop",
            "search_name": "Pennsylvania"
        },
        {
            "costar_id": "1431234",
            "address": "3032 N Ridge Rd E",
            "city": "Ashtabula",
            "state": "OH",
            "zip_code": "44004",
            "property_type": "Drug Store",
            "square_feet": "30,426",
            "year_built": "1999",
            "price": "$3,300,000",
            "price_per_sf": "$108.46/SF",
            "cap_rate": "8.55%",
            "image_url": "https://images.unsplash.com/photo-1582560475093-ba66accbc424?w=400&h=300&fit=crop",
            "search_name": "Ohio 70 Mile"
        },
        {
            "costar_id": "1431235",
            "address": "3119 Train Ave",
            "city": "Cleveland",
            "state": "OH",
            "zip_code": "44113",
            "property_type": "Auto Salvage Facility",
            "square_feet": "5,742",
            "year_built": "1930",
            "price": "Price Not Disclosed",
            "price_per_sf": None,
            "image_url": "https://images.unsplash.com/photo-1565793298595-6a879b1d9492?w=400&h=300&fit=crop",
            "search_name": "Ohio 70 Mile"
        },
        {
            "costar_id": "1431236",
            "address": "1307 3rd St",
            "city": "Beaver",
            "state": "PA",
            "zip_code": "15009",
            "property_type": "Office",
            "square_feet": "2,534",
            "year_built": "1900",
            "price": "$307,000",
            "price_per_sf": "$121.15/SF",
            "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&h=300&fit=crop",
            "search_name": "Pennsylvania"
        },
        {
            "costar_id": "1431237",
            "address": "17500 Territorial Rd",
            "city": "Osseo",
            "state": "MN",
            "zip_code": "55369",
            "property_type": "Industrial Land",
            "square_feet": "100,001 SF (2.30 AC)",
            "year_built": None,
            "price": "Price Not Disclosed",
            "price_per_sf": None,
            "image_url": "https://images.unsplash.com/photo-1416339306562-f3d12fefd36f?w=400&h=300&fit=crop",
            "search_name": "Minnesota"
        },
        {
            "costar_id": "1431238",
            "address": "3535 Blue Cross Rd",
            "city": "Eagan",
            "state": "MN",
            "zip_code": "55122",
            "property_type": "Commercial Land",
            "square_feet": "1,100,199 SF (25.26 AC)",
            "year_built": None,
            "price": "Price Not Disclosed",
            "price_per_sf": None,
            "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&h=300&fit=crop",
            "search_name": "Minnesota"
        },
        {
            "costar_id": "1431239",
            "address": "7777 W Blue Mound Rd",
            "city": "Milwaukee",
            "state": "WI",
            "zip_code": "53213",
            "property_type": "Office",
            "square_feet": "44,328",
            "year_built": "1988",
            "price": "$5,000,000",
            "price_per_sf": "$112.80/SF",
            "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=300&fit=crop",
            "search_name": "Wisconsin"
        },
        {
            "costar_id": "1431240",
            "address": "9620 Forest Hills Rd",
            "city": "Machesney Park",
            "state": "IL",
            "zip_code": "61115",
            "property_type": "Light Manufacturing",
            "square_feet": "21,912",
            "year_built": "2000",
            "price": "Price Not Disclosed",
            "price_per_sf": "$8-9/SF (Est.)",
            "image_url": "https://images.unsplash.com/photo-1565793298595-6a879b1d9492?w=400&h=300&fit=crop",
            "search_name": "Illinois"
        },
        {
            "costar_id": "1431241",
            "address": "410 Main St",
            "city": "Racine",
            "state": "WI",
            "zip_code": "53403",
            "property_type": "Office",
            "square_feet": "14,245",
            "year_built": "1887",
            "price": "$750,000",
            "price_per_sf": "$52.65/SF",
            "image_url": "https://images.unsplash.com/photo-1554469384-e58fac16e23a?w=400&h=300&fit=crop",
            "search_name": "Wisconsin"
        },
        {
            "costar_id": "1431242",
            "address": "10533 W National Ave",
            "city": "West Allis",
            "state": "WI",
            "zip_code": "53227",
            "property_type": "Office",
            "square_feet": "19,010",
            "year_built": "1971",
            "price": "$899,000",
            "price_per_sf": "$47.29/SF",
            "image_url": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=400&h=300&fit=crop",
            "search_name": "Wisconsin"
        },
        {
            "costar_id": "1431243",
            "address": "1405 W Silver Spring Dr",
            "city": "Milwaukee",
            "state": "WI",
            "zip_code": "53209",
            "property_type": "Veterinarian/Kennel",
            "square_feet": "2,474",
            "year_built": "1940",
            "price": "$499,900",
            "price_per_sf": "$202.06/SF",
            "image_url": "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&h=300&fit=crop",
            "search_name": "Wisconsin"
        },
        {
            "costar_id": "1431244",
            "address": "913 Tower Rd",
            "city": "Mundelein",
            "state": "IL",
            "zip_code": "60060",
            "property_type": "Commercial Land",
            "square_feet": "132,858 SF (3.05 AC)",
            "year_built": None,
            "price": "$850,000",
            "price_per_sf": "$278,688.52/AC",
            "image_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=300&fit=crop",
            "search_name": "Illinois"
        },
        {
            "costar_id": "1431245",
            "address": "121 S Wilson Ave",
            "city": "Hartford",
            "state": "WI",
            "zip_code": "53027",
            "property_type": "Flex",
            "square_feet": "8,572",
            "year_built": "2020",
            "price": "$1,600,000",
            "price_per_sf": "$186.65/SF",
            "image_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=400&h=300&fit=crop",
            "search_name": "Wisconsin"
        }
    ]
    
    added_count = 0
    for prop in sample_properties:
        result = insert_property(prop)
        if result:
            added_count += 1
    
    return added_count
