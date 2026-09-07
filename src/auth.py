"""
src/auth.py — Authentication and Role-Based Access Control (RBAC) Module for ClimaCrop Intelligence.
Manages user accounts, secure salted password hashing, role definitions, and session state.
"""

import os
import json
import hashlib
import hmac
from typing import Optional, Dict, Any, List

# Path to persistent users database
USERS_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.json")

# Role definitions & descriptions
ROLES = {
    "cooperative": {
        "name": "Cooperative Member / Farmer",
        "icon": "👨‍🌾",
        "description": "Access crop recommendations, farm profit calculator, harvest calendar, and market arbitrage.",
        "badge_color": "#10b981",
        "default_view": "🌱 Cooperative Advisory"
    },
    "bank_officer": {
        "name": "Bank & SACCO Credit Officer",
        "icon": "🏦",
        "description": "Underwrite agricultural loans, calculate DSCR, and stress-test portfolio credit risks.",
        "badge_color": "#3b82f6",
        "default_view": "🏦 Bank & Credit Risk"
    },
    "researcher": {
        "name": "Climate & Agronomy Researcher",
        "icon": "🌍",
        "description": "Analyze 10-year weather trends, 116 TAHMO stations, and benchmark AEZ rules vs ML models.",
        "badge_color": "#8b5cf6",
        "default_view": "🌍 Climate Trends"
    },
    "admin": {
        "name": "System Administrator",
        "icon": "👑",
        "description": "Full platform access, system configuration, and dynamic persona preview.",
        "badge_color": "#f59e0b",
        "default_view": "🌱 Cooperative Advisory"
    }
}

# Fixed salt for consistent hashing across instances
SALT = "ClimaCrop_Kilimo_Smart_2025_Salt"

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a salt."""
    salted = f"{SALT}:{password}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

# Default pre-seeded demo accounts
DEFAULT_USERS: Dict[str, Dict[str, Any]] = {
    "coop_user": {
        "username": "coop_user",
        "password_hash": hash_password("kilimo2025"),
        "full_name": "Wanjiku Mwangi",
        "role": "cooperative",
        "organization": "Nakuru Grain Growers Co-op",
        "email": "wanjiku@nakurugrain.co.ke",
        "county": "Nakuru"
    },
    "bank_officer": {
        "username": "bank_officer",
        "password_hash": hash_password("sacco2025"),
        "full_name": "Kevin Kiprop",
        "role": "bank_officer",
        "organization": "Agricultural Finance SACCO",
        "email": "k.kiprop@agrifinance.co.ke",
        "county": "Uasin Gishu"
    },
    "researcher": {
        "username": "researcher",
        "password_hash": hash_password("tahmo2025"),
        "full_name": "Dr. Amina Ochieng",
        "role": "researcher",
        "organization": "Kenya Agro-Meteorological Lab",
        "email": "a.ochieng@agrometeorology.ke",
        "county": "Machakos"
    },
    "admin": {
        "username": "admin",
        "password_hash": hash_password("admin2025"),
        "full_name": "Carson Sila",
        "role": "admin",
        "organization": "ClimaCrop Core Engineering",
        "email": "admin@climacrop.ai",
        "county": "Nakuru"
    }
}


def load_users() -> Dict[str, Dict[str, Any]]:
    """Load users from JSON file, initializing defaults if file does not exist."""
    os.makedirs(os.path.dirname(USERS_DB_PATH), exist_ok=True)
    if not os.path.exists(USERS_DB_PATH):
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS.copy()
    
    try:
        with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
            users = json.load(f)
            # Ensure default demo users always exist
            for u_key, u_val in DEFAULT_USERS.items():
                if u_key not in users:
                    users[u_key] = u_val
            return users
    except Exception:
        return DEFAULT_USERS.copy()


def save_users(users: Dict[str, Dict[str, Any]]) -> bool:
    """Save users dictionary to JSON file."""
    try:
        os.makedirs(os.path.dirname(USERS_DB_PATH), exist_ok=True)
        with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception:
        return False


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate username and password. Returns user dict without password_hash if valid, None otherwise."""
    users = load_users()
    u_clean = username.strip().lower()
    
    if u_clean not in users:
        return None
    
    user_record = users[u_clean]
    if user_record.get("password_hash") == hash_password(password):
        # Return safe copy without password hash
        user_safe = user_record.copy()
        user_safe.pop("password_hash", None)
        return user_safe
    
    return None


def register_user(
    username: str,
    password: str,
    full_name: str,
    role: str,
    organization: str,
    email: str = "",
    county: str = "Nakuru"
) -> tuple[bool, str]:
    """Register a new user account. Returns (success_bool, message_str)."""
    u_clean = username.strip().lower()
    if not u_clean:
        return False, "Username cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."
    if role not in ROLES:
        return False, f"Invalid role. Must be one of: {', '.join(ROLES.keys())}"
    
    users = load_users()
    if u_clean in users:
        return False, f"Username '{u_clean}' already exists. Please choose a different username."
    
    users[u_clean] = {
        "username": u_clean,
        "password_hash": hash_password(password),
        "full_name": full_name.strip() or u_clean.capitalize(),
        "role": role,
        "organization": organization.strip() or "Independent Member",
        "email": email.strip(),
        "county": county
    }
    
    if save_users(users):
        return True, f"Account '{u_clean}' successfully created! You can now sign in."
    else:
        return False, "Failed to save user database."


def get_demo_account(role_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve pre-configured demo account for a specific role."""
    role_to_user = {
        "cooperative": "coop_user",
        "bank_officer": "bank_officer",
        "researcher": "researcher",
        "admin": "admin"
    }
    username = role_to_user.get(role_key)
    if username and username in DEFAULT_USERS:
        safe_copy = DEFAULT_USERS[username].copy()
        safe_copy.pop("password_hash", None)
        return safe_copy
    return None
