# CoStar Email Scraper

A web application that automatically scrapes property data from CoStar Daily Alert emails and stores it in MongoDB.

## Tech Stack

- **Backend:** FastAPI (Python)
- - **Database:** MongoDB
  - - **Email:** Gmail API
    - - **Frontend:** React + Tailwind CSS (coming soon)
     
      - ## Features
     
      - - Automatically parse CoStar Daily Alert emails
        - - Extract property data: Image, Address, City, State, ZIP, Property Type, Square Feet, Year Built, Price
          - - Store properties in MongoDB with duplicate detection
            - - REST API for querying properties with filters
              - - Statistics and analytics endpoints
               
                - ## Project Structure
               
                - ```
                  costar-scraper/
                  ├── backend/
                  │   ├── main.py           # FastAPI application
                  │   ├── database.py       # MongoDB connection and queries
                  │   ├── email_parser.py   # CoStar email HTML parser
                  │   ├── gmail_service.py  # Gmail API integration
                  │   └── requirements.txt  # Python dependencies
                  └── README.md
                  ```

                  ## Setup Instructions

                  ### 1. Prerequisites

                  - Python 3.9+
                  - - MongoDB (local or MongoDB Atlas)
                    - - Google Cloud Project with Gmail API enabled
                     
                      - ### 2. Google Cloud Setup
                     
                      - 1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                        2. 2. Create a new project
                           3. 3. Enable the Gmail API
                              4. 4. Create OAuth 2.0 credentials (Desktop application)
                                 5. 5. Download `credentials.json` to the backend folder
                                   
                                    6. ### 3. Installation
                                   
                                    7. ```bash
                                       cd backend
                                       pip install -r requirements.txt
                                       ```

                                       ### 4. Environment Variables

                                       Create a `.env` file in the backend folder:

                                       ```
                                       MONGODB_URI=mongodb://localhost:27017
                                       ```

                                       ### 5. Run the Server

                                       ```bash
                                       cd backend
                                       uvicorn main:app --reload
                                       ```

                                       The API will be available at `http://localhost:8000`

                                       ## API Endpoints

                                       | Endpoint | Method | Description |
                                       |----------|--------|-------------|
                                       | `/` | GET | API info |
                                       | `/api/properties` | GET | List properties (with filters) |
                                       | `/api/properties/count` | GET | Total property count |
                                       | `/api/properties/stats` | GET | Statistics by state/type |
                                       | `/api/sync-emails` | POST | Trigger email sync |
                                       | `/health` | GET | Health check |

                                       ### Query Parameters for `/api/properties`

                                       - `city` - Filter by city name
                                       - - `state` - Filter by state (e.g., OH, PA)
                                         - - `property_type` - Filter by property type
                                           - - `search_name` - Filter by CoStar search name
                                             - - `skip` - Pagination offset
                                               - - `limit` - Max results (default: 50)
                                                
                                                 - ## Data Model
                                                
                                                 - Each property document in MongoDB contains:
                                                
                                                 - ```json
                                                   {
                                                     "costar_id": "1431229",
                                                     "address": "2695 Gilchrist Rd",
                                                     "city": "Akron",
                                                     "state": "OH",
                                                     "zip_code": "44305",
                                                     "property_type": "Fast Food",
                                                     "square_feet": "3591",
                                                     "year_built": "1990",
                                                     "price": "$1",
                                                     "price_per_sf": "$0.00",
                                                     "image_url": "https://...",
                                                     "costar_url": "https://...",
                                                     "search_name": "Ohio 70 Mile",
                                                     "email_date": "2026-01-17T07:00:00",
                                                     "created_at": "2026-01-18T..."
                                                   }
                                                   ```

                                                   ## Usage with Emergent.sh

                                                   This project is designed to work with [Emergent.sh](https://emergent.sh) for building the frontend. The backend API is ready to be consumed by a React + Tailwind frontend.

                                                   ## License

                                                   MIT
