"""
tests/test_auth.py — Unit tests for authentication and role-based access control.
"""

import unittest
import os
import shutil
from src.auth import (
    authenticate_user,
    register_user,
    get_demo_account,
    load_users,
    ROLES,
    hash_password
)

class TestAuthModule(unittest.TestCase):

    def test_01_roles_defined(self):
        """Verify all 4 required personas are defined in ROLES."""
        expected_roles = {"cooperative", "bank_officer", "researcher", "admin"}
        self.assertTrue(expected_roles.issubset(set(ROLES.keys())))
        for r_key, r_data in ROLES.items():
            self.assertIn("name", r_data)
            self.assertIn("icon", r_data)
            self.assertIn("default_view", r_data)

    def test_02_demo_accounts_authentication(self):
        """Verify all 4 demo accounts authenticate with their default credentials."""
        # 1. Cooperative member
        coop_user = authenticate_user("coop_user", "kilimo2025")
        self.assertIsNotNone(coop_user)
        self.assertEqual(coop_user["role"], "cooperative")
        self.assertNotIn("password_hash", coop_user)

        # 2. Bank officer
        bank_user = authenticate_user("bank_officer", "sacco2025")
        self.assertIsNotNone(bank_user)
        self.assertEqual(bank_user["role"], "bank_officer")

        # 3. Researcher
        res_user = authenticate_user("researcher", "tahmo2025")
        self.assertIsNotNone(res_user)
        self.assertEqual(res_user["role"], "researcher")

        # 4. Admin
        admin_user = authenticate_user("admin", "admin2025")
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user["role"], "admin")

    def test_03_invalid_credentials(self):
        """Verify invalid passwords or non-existent usernames fail authentication."""
        self.assertIsNone(authenticate_user("coop_user", "wrong_password"))
        self.assertIsNone(authenticate_user("non_existent_user_123", "some_pass"))

    def test_04_user_registration(self):
        """Verify registering a new user succeeds and allows subsequent login."""
        import uuid
        test_username = f"farmer_{uuid.uuid4().hex[:8]}"
        test_pass = "securepass123"
        
        success, msg = register_user(
            username=test_username,
            password=test_pass,
            full_name="John Doe",
            role="cooperative",
            organization="Eldoret Farmers Sacco",
            email="johndoe@test.com",
            county="Uasin Gishu"
        )
        self.assertTrue(success, f"Registration failed with: {msg}")
        
        # Test authenticating the newly registered user
        user = authenticate_user(test_username, test_pass)
        self.assertIsNotNone(user)
        self.assertEqual(user["full_name"], "John Doe")
        self.assertEqual(user["role"], "cooperative")
        self.assertEqual(user["organization"], "Eldoret Farmers Sacco")

    def test_05_get_demo_account_helper(self):
        """Verify get_demo_account returns safe user profiles for quick login."""
        demo_coop = get_demo_account("cooperative")
        self.assertIsNotNone(demo_coop)
        self.assertEqual(demo_coop["username"], "coop_user")
        self.assertNotIn("password_hash", demo_coop)

if __name__ == "__main__":
    unittest.main()
