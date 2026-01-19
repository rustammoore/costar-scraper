from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os

# MongoDB connection
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
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
                            prop["email_date"] = prop["email_date"].isoformat()
                        if prop.get("created_at"):
                                      prop["created_at"] = prop["created_at"].isoformat()
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
