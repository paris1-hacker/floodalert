FloodAlert API
Overview

FloodAlert API is the backend service for the FloodAlert MVP. It enables users to report flooded locations, confirm existing reports, and retrieve active hazards displayed on the live map.

The API is built with Django and Django REST Framework and uses JWT authentication for protected endpoints.

API Version

Current Version: v1

Features
User registration
User authentication (JWT)
User profile endpoint
Create flood reports
Retrieve all active reports
Retrieve individual reports
Confirm ("Still Flooded") reports
Automatic report lifecycle
Nearby report retrieval
GPS duplicate detection (30-meter tolerance)
Swagger/OpenAPI documentation
Flood Report Lifecycle

Every report progresses through the following states:

Live
Created successfully
Visible on the map
Duration: 0–2 hours
Warning
No confirmation received for 2 hours
Report remains visible
Frontend may display a warning indicator
Duration: 2–4 hours
Expired
No confirmation received for 4 hours
Report becomes inactive
Removed from active map results
Authentication

Protected endpoints require a JWT access token.

Example:

Authorization: Bearer <access_token>

Public endpoints:

GET /api/reports/
GET /api/reports/{id}/
GET /api/reports/nearby/

Protected endpoints:

POST /api/reports/
POST /api/reports/{id}/confirm/
Profile
Logout
Main Endpoints
Method	Endpoint	Description
POST	/api/accounts/register/	Register user
POST	/api/accounts/login/	Login
POST	/api/accounts/logout/	Logout
GET	/api/accounts/profile/	Current user
GET	/api/reports/	Active reports
POST	/api/reports/	Create report
GET	/api/reports/{id}/	Report details
POST	/api/reports/{id}/confirm/	Confirm report
GET	/api/reports/nearby/	Nearby reports
Status Filtering

Retrieve reports by status:

GET /api/reports/?status=live
GET /api/reports/?status=warning
Standard Response Format
Success
{
    "success": true,
    "message": "Flood report created successfully.",
    "data": {}
}
Failure
{
    "success": false,
    "message": "Validation failed.",
    "errors": {}
}
Common Error Codes
Status	Meaning
400	Validation error
400	Duplicate nearby report
400	User has already confirmed this report
401	Authentication required
404	Report not found
500	Internal server error
Business Rules
Reports require GPS coordinates.
Duplicate reports within approximately 30 meters are rejected.
A user can confirm a report only once.
Every confirmation resets the report to Live.
Every confirmation extends the expiry window by two hours.
Reports expire after four hours without new confirmations.
MVP Limitations

The current MVP has the following limitations:

No image uploads.
No push notifications.
No offline reporting.
Automatic expiry currently uses request-triggered status refresh.
No scheduled background worker (Celery) in the current deployment.
GPS accuracy depends on the user's device.
Future Improvements
Celery + Redis scheduled expiry processing.
Image attachments.
Push notifications.
Administrative dashboard.
Analytics and reporting.
Spatial database support (PostGIS).
Real-time updates using WebSockets.
Technology Stack
Python
Django
Django REST Framework
JWT Authentication
SQLite/PostgreSQL
OpenAPI / Swagger
Vercel (current deployment)
API Documentation

Interactive API documentation is available through Swagger/OpenAPI.