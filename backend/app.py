import os
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

# --------------------------------------------------
# BASIC SETUP
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(
    __name__,
    static_folder=str(BASE_DIR),
    static_url_path=""
)

CORS(app, resources={r"/api/*": {"origins": "*"}})


# --------------------------------------------------
# MONGODB CONNECTION
# --------------------------------------------------

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing from backend/.env"
    )

mongo_client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000
)

database = mongo_client[
    os.getenv("MONGODB_DATABASE", "ecosort_ai")
]

users = database.users
scans = database.scans


# --------------------------------------------------
# DATABASE HELPERS
# --------------------------------------------------

def ensure_indexes():
    users.create_index(
        [("user_id", ASCENDING)],
        unique=True
    )

    scans.create_index(
        [
            ("user_id", ASCENDING),
            ("created_at", ASCENDING)
        ]
    )


def now():
    return datetime.now(timezone.utc)


def json_value(value):

    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: json_value(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            json_value(item)
            for item in value
        ]

    return value


# --------------------------------------------------
# USER HELPERS
# --------------------------------------------------

def required_user_id(payload):

    user_id = str(
        payload.get("user_id")
        or payload.get("registration")
        or payload.get("employee_id")
        or ""
    ).strip()

    if not user_id:
        raise ValueError(
            "user_id is required and must be the registration number or employee ID"
        )

    return user_id


def normalize_profile(payload):

    user_id = required_user_id(payload)

    user_type = str(
        payload.get("user_type")
        or payload.get("usertype")
        or "student"
    ).strip().lower()

    if user_type == "public":
        user_type = "employee"

    if user_type not in {"student", "employee"}:
        raise ValueError(
            "user_type must be student or employee"
        )

    return {
        "user_id": user_id,

        "username": str(
            payload.get("username")
            or payload.get("name")
            or ""
        ).strip(),

        "user_type": user_type,

        "registration":
            user_id if user_type == "student" else "",

        "employee_id":
            user_id if user_type == "employee" else "",

        "description":
            payload.get(
                "description",
                "EcoSort AI user"
            ),

        "college": str(
            payload.get("college")
            or payload.get("place")
            or ""
        ).strip(),

        "campus": str(
            payload.get("campus") or ""
        ).strip(),

        "hostel": str(
            payload.get("hostel")
            or payload.get("unit")
            or ""
        ).strip(),

        "room": str(
            payload.get("room")
            or payload.get("space")
            or ""
        ).strip(),

        "department": str(
            payload.get("department") or ""
        ).strip(),

        "year": str(
            payload.get("year") or ""
        ).strip(),

        "area": str(
            payload.get("area") or ""
        ).strip(),

        "building": str(
            payload.get("building") or ""
        ).strip(),

        "flat": str(
            payload.get("flat") or ""
        ).strip(),

        "tower": str(
            payload.get("tower") or ""
        ).strip(),

        "floor": str(
            payload.get("floor") or ""
        ).strip(),
    }


def public_user(user):

    user = dict(user)

    user.pop("_id", None)

    return json_value(user)


# --------------------------------------------------
# FRONTEND
# --------------------------------------------------

@app.get("/")
def index():

    return send_from_directory(
        BASE_DIR,
        "index.html"
    )


@app.get("/<path:filename>")
def frontend_file(filename):

    return send_from_directory(
        BASE_DIR,
        filename
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():

    try:

        mongo_client.admin.command("ping")

        ensure_indexes()

        return jsonify({
            "status": "online",
            "message": "EcoSort AI server is running",
            "database": database.name,
            "classes": 30
        })

    except PyMongoError as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 503


# --------------------------------------------------
# SAVE USER
# --------------------------------------------------

@app.post("/api/users")
def save_user():

    try:

        ensure_indexes()

        profile = normalize_profile(
            request.get_json(silent=True) or {}
        )

        if not profile["username"]:

            return jsonify({
                "error": "username is required"
            }), 400

        timestamp = now()

        result = users.update_one(

            {
                "user_id":
                    profile["user_id"]
            },

            {
                "$set": {
                    **profile,
                    "updated_at": timestamp
                },

                "$setOnInsert": {
                    "created_at": timestamp
                }
            },

            upsert=True
        )

        user = users.find_one(
            {
                "user_id":
                    profile["user_id"]
            }
        )

        return jsonify({
            "user": public_user(user),
            "created":
                result.upserted_id is not None
        }), (
            201
            if result.upserted_id
            else 200
        )

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 400

    except PyMongoError as error:

        return jsonify({
            "error": "MongoDB operation failed",
            "details": str(error)
        }), 503


# --------------------------------------------------
# GET USER
# --------------------------------------------------

@app.get("/api/users/<user_id>")
def get_user(user_id):

    try:

        ensure_indexes()

        user = users.find_one({
            "user_id": user_id
        })

        if not user:

            return jsonify({
                "error": "user not found"
            }), 404

        return jsonify({
            "user": public_user(user)
        })

    except PyMongoError as error:

        return jsonify({
            "error": "MongoDB operation failed",
            "details": str(error)
        }), 503


# --------------------------------------------------
# RECORD WASTE SCAN
# --------------------------------------------------

@app.post("/api/users/<user_id>/scans")
def record_scan(user_id):

    payload = request.get_json(
        silent=True
    ) or {}

    try:

        ensure_indexes()

        reward = {

            "user_id": user_id,

            "object": str(
                payload.get("object")
                or payload.get("name")
                or "Unknown waste"
            ),

            "category":
                payload.get("category", ""),

            "bin":
                payload.get("bin", ""),

            "confidence":
                payload.get("confidence"),

            "correct":
                bool(
                    payload.get(
                        "correct",
                        False
                    )
                ),

            "xp":
                int(
                    payload.get(
                        "xp",
                        0
                    )
                ),

            "credits":
                int(
                    payload.get(
                        "credits",
                        0
                    )
                ),

            "created_at": now()
        }

        result = scans.insert_one(
            reward
        )

        if reward["correct"]:

            users.update_one(

                {
                    "user_id": user_id
                },

                {
                    "$inc": {

                        "xp":
                            reward["xp"],

                        "credits":
                            reward["credits"],

                        "scans": 1,

                        "sorted": 1
                    }
                }
            )

        return jsonify({

            "scan_id":
                str(result.inserted_id),

            "scan":
                json_value(reward)

        }), 201

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "error":
                "xp, credits, and confidence must contain valid values"
        }), 400

    except PyMongoError as error:

        return jsonify({
            "error":
                "MongoDB operation failed",

            "details":
                str(error)

        }), 503


# --------------------------------------------------
# GET USER SCANS
# --------------------------------------------------

@app.get("/api/users/<user_id>/scans")
def list_scans(user_id):

    try:

        ensure_indexes()

        items = (
            scans
            .find({
                "user_id": user_id
            })
            .sort(
                "created_at",
                -1
            )
            .limit(50)
        )

        return jsonify({

            "scans": [
                json_value(item)
                for item in items
            ]

        })

    except PyMongoError as error:

        return jsonify({

            "error":
                "MongoDB operation failed",

            "details":
                str(error)

        }), 503


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                "5000"
            )
        ),
        debug=True
    )