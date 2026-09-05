# HOTEL LA VISTA

Hotel management system with a browser frontend and two backend implementations:

- `python backend/`: procedural Flask backend currently used by the frontend
- `java backend/`: separate OOP Spark/Maven backend
- `frontend/`: login and hotel management dashboard

## Python Backend Setup

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirement.txt
python "python backend/app.py"
```

The Python API runs at:

```text
http://localhost:5000/api
```

Open `frontend/index.html` in a browser after starting the backend.

Demo accounts:

```text
Admin: admin / admin123
Guest: user / user123
```

## Frontend Features

- Guest and admin login
- Room browsing with images, custom names, details, prices, and availability windows
- Date and time overlap validation for bookings
- Guest booking history and cancellation
- Admin room creation, editing, and deletion
- Admin guest management
- Admin payment recording and refunds
- Occupancy, revenue, guest, and booking reports

## Java Backend

> **Status: Not working yet.** The Java OOP backend is still under development and is not the active backend for the frontend. Use the Python backend for the working application.

The Java backend is a separate OOP implementation using Java 17, Spark Java, and Maven. Build it with:

```powershell
Set-Location "java backend"
mvn clean package
```

The Java application is configured to run on port `8080`:

```text
http://localhost:8080/api
```

The current frontend points to the Python API at `http://localhost:5000/api`. To use the Java backend, its request and response behavior must match the frontend API contract, or `API_BASE` in `frontend/js/auth.js` must be changed along with any incompatible field/response differences.

## API Response Contract

Successful responses should use this shape:

```json
{
  "success": true,
  "message": "Success",
  "status": 200,
  "data": {}
}
```

Authenticated requests use:

```text
Authorization: Bearer <token>
```

## Notes

- The Python backend stores data in `python backend/data/hotel_data.json`.
- Stop any previous backend process before switching between Python and Java backends.
- The frontend must be opened from a location that can reach the selected backend and its CORS configuration.
