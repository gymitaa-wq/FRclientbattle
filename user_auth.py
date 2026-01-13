"""
User Authentication and Management System
Simple file-based authentication for simulation app
"""

import json
import hashlib
import os
from typing import Optional, Dict, Any
from datetime import datetime


class UserManager:
    """Manages user authentication and user data"""
    
    def __init__(self, users_file: str = "users.json"):
        # Use absolute path to ensure file is in script directory
        if not os.path.isabs(users_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            users_file = os.path.join(script_dir, users_file)
        self.users_file = users_file
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file if it doesn't exist"""
        if not os.path.exists(self.users_file):
            default_users = {
                "demo": {
                    "password_hash": self._hash_password("demo123"),
                    "created_at": datetime.now().isoformat(),
                    "full_name": "Demo User"
                }
            }
            self._save_users(default_users)
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict[str, Any]):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user credentials
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            True if authentication successful
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        password_hash = self._hash_password(password)
        return users[username]["password_hash"] == password_hash
    
    def create_user(self, username: str, password: str, full_name: str = "") -> bool:
        """
        Create new user account
        
        Args:
            username: Desired username
            password: Plain text password
            full_name: User's full name
            
        Returns:
            True if user created successfully
        """
        users = self._load_users()
        
        if username in users:
            return False  # User already exists
        
        users[username] = {
            "password_hash": self._hash_password(password),
            "created_at": datetime.now().isoformat(),
            "full_name": full_name
        }
        
        self._save_users(users)
        return True
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information (without password hash)"""
        users = self._load_users()
        
        if username not in users:
            return None
        
        user_data = users[username].copy()
        user_data.pop("password_hash", None)  # Remove password from returned data
        user_data["username"] = username
        return user_data
    
    def user_exists(self, username: str) -> bool:
        """Check if username exists"""
        users = self._load_users()
        return username in users
    
    def create_google_user(self, email: str, name: str, google_id: str) -> bool:
        """
        Create user account from Google OAuth
        
        Args:
            email: Google email address (used as username)
            name: User's full name from Google
            google_id: Google user ID
            
        Returns:
            True if user created successfully
        """
        users = self._load_users()
        
        # Use email as username (lowercase, no @)
        username = email.split('@')[0].lower()
        
        # If username exists, append number
        original_username = username
        counter = 1
        while username in users:
            username = f"{original_username}{counter}"
            counter += 1
        
        users[username] = {
            "password_hash": "",  # No password for Google users
            "created_at": datetime.now().isoformat(),
            "full_name": name,
            "google_id": google_id,
            "email": email,
            "auth_method": "google"
        }
        
        self._save_users(users)
        return username
    
    def find_google_user(self, google_id: str) -> Optional[str]:
        """
        Find user by Google ID
        
        Args:
            google_id: Google user ID
            
        Returns:
            Username if found, None otherwise
        """
        users = self._load_users()
        
        for username, user_data in users.items():
            if user_data.get('google_id') == google_id:
                return username
        
        return None


# Global instance
user_manager = UserManager()


if __name__ == "__main__":
    # Test authentication
    print("Testing User Authentication System")
    print("-" * 50)
    
    # Test default user
    if user_manager.authenticate("demo", "demo123"):
        print("✅ Default user 'demo' authenticated successfully")
    else:
        print("❌ Default user authentication failed")
    
    # Test invalid credentials
    if not user_manager.authenticate("demo", "wrongpassword"):
        print("✅ Invalid password correctly rejected")
    else:
        print("❌ Invalid password was accepted")
    
    # Test user creation
    if user_manager.create_user("testuser", "test123", "Test User"):
        print("✅ Test user created successfully")
        if user_manager.authenticate("testuser", "test123"):
            print("✅ Test user authenticated successfully")
        else:
            print("❌ Test user authentication failed")
    else:
        print("❌ Test user creation failed")
    
    print("\nUser info for 'demo':")
    print(user_manager.get_user_info("demo"))
