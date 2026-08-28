# EcoSort AI Flask backend

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py backend.py
```

Open `http://127.0.0.1:5000` so Flask serves the frontend and the API from the same origin.

## API

- `GET /api/health` checks MongoDB connectivity.
- `POST /api/users` creates or updates a profile. `user_id` is the student registration number or employee ID.
- `GET /api/users/<user_id>` reads a profile.
- `POST /api/users/<user_id>/scans` records a scan and increments rewards when `correct` is true.
- `GET /api/users/<user_id>/scans` returns recent scan history.

Example profile payload:

```json
{
  "user_id": "22BCE1042",
  "username": "Ruksana",
  "user_type": "student",
  "college": "ABC University",
  "hostel": "Block B",
  "room": "204",
  "department": "Computer Science",
  "year": "3rd Year",
  "description": "EcoSort AI user"
}
```
