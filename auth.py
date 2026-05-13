"""
auth.py — AspirantFlow Authentication
======================================
Handles password hashing (bcrypt) and login/signup validation.

Flow:
  signup(username, password)
    → hash password → DatabaseManager.create_user() → True/False

  login(username, password)
    → DatabaseManager.get_user() → bcrypt.checkpw() → user dict / None
"""

import bcrypt
from database import DatabaseManager

db = DatabaseManager()


def signup(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (True, "OK") on success or (False, reason) on failure.
    """
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    # bcrypt handles salting internally
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    created = db.create_user(username, hashed)
    if not created:
        return False, "Username already taken. Try another."
    return True, "Account created! Please log in."


def login(username: str, password: str) -> tuple[dict | None, str]:
    """
    Verify credentials.
    Returns (user_dict, "OK") or (None, error_message).
    """
    username = username.strip()
    user = db.get_user(username)
    if not user:
        return None, "User not found."
    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None, "Incorrect password."
    return user, "OK"
