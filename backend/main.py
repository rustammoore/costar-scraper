from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os

from database import (
    get_properties, 
    get_property_count, 
    get_property_stats,
    insert_property
)
from gmail_service import get_gmail_service, get_costar_emails, get_email_html, get_email_date
from email_parser import parse_costar_email

app = FastAPI(title="CoStar Scraper API", version="1.0.0")

# CORS for React frontend
app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
)


# Pydantic Models
class SyncResponse(BaseModel):
      status: str
      total_found: int
      new_added: int
      duplicates_skipped: int


# API Endpoints
@app.get("/")
def root():
      return {"message": "CoStar Scraper API", "version": "1.0.0"}


@app.get("/api/properties")
def list_properties(
      city: Optional[str] = Query(None, description="Filter by city"),
      state: Optional[str] = Query(None, description="Filter by state"),
      property_type: Optional[str] = Query(None, description="Filter by property type"),
      search_name: Optional[str] = Query(None, description="Filter by search name"),
      skip: int = Query(0, ge=0),
      limit: int = Query(50, ge=1, le=100)
):
      """Get list of properties with optional filters."""
      properties = get_properties(
          city=city,
          state=state,
          property_type=property_type,
          search_name=search_name,
          skip=skip,
          limit=limit
      )
      return {"properties": properties, "count": len(properties)}


@app.get("/api/properties/count")
def count_properties():
      """Get total property count."""
      count = get_property_count()
      return {"count": count}


@app.get("/api/properties/stats")
def property_stats():
      """Get property statistics."""
      stats = get_property_stats()
      return stats


@app.post("/api/sync-emails", response_model=SyncResponse)
def sync_emails(
      days_back: int = Query(7, ge=1, le=90),
      max_emails: int = Query(50, ge=1, le=200)
):
      """Manually trigger email sync."""
      try:
                service = get_gmail_service()
                after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

        emails = get_costar_emails(service, max_results=max_emails, after_date=after_date)

        total_found = 0
        new_added = 0

        for email in emails:
                      html_content = get_email_html(email)
                      if not html_content:
                                        continue

                      email_date_str = get_email_date(email)
                      email_date = None
                      if email_date_str:
                                        from dateutil import parser as date_parser
                                        try:
                                                              email_date = date_parser.parse(email_date_str)
                                                          except:
                    pass

            properties = parse_costar_email(html_content)
            total_found += len(properties)

            for prop in properties:
                              prop["email_date"] = email_date
                              result = insert_property(prop)
                              if result:
                                                    new_added += 1

                      return SyncResponse(
                                    status="success",
                                    total_found=total_found,
                                    new_added=new_added,
                                    duplicates_skipped=total_found - new_added
                      )

except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
      return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
