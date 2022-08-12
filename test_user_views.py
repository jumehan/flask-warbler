"""User view tests."""

import os
from unittest import TestCase
from models import db, User, Follows

CURR_USER_KEY = 'curr_user'

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app
app.config['WTF_CSRF_ENABLED'] = False

db.create_all()


class UserViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_signup_success(self):
        """Test that the signup route works properly
        - can create a new u3 user account given valid credentials
        & redirects to home page
        """
        with self.client as c:
            resp = c.post(
                            "/signup",
                            data={
                                "username": "u3",
                                "password": "password",
                                "email": "u3@email.com",
                                "image_url": None,
                            },
                            follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<!--String for testing: Home route!!!!!:)-->", html)
            self.assertIn("@u3", html)

    def test_user_signup_fail_username(self):
        """Test that the signup route works properly
        - fails if u3 provides invalid credentials: invalid username
        & redirects to signup
        """
        with self.client as c:
            resp = c.post(
                            "/signup",
                            data={
                                "username": "u2",
                                "password": "password",
                                "email": "u3@email.com",
                                "image_url": None,
                            },
                            follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Username or Email already taken", html)
            self.assertIn("<!--Testing string for signup!!!!!! :)-->", html)

    def test_user_signup_fail_email(self):
        """Test that the signup route works properly
        - fails if u3 provides invalid credentials: invalid email
        & redirects to signup
        """
        with self.client as c:
            resp = c.post(
                            "/signup",
                            data={
                                "username": "u3",
                                "password": "password",
                                "email": "u2@email.com",
                                "image_url": None,
                            },
                            follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Username or Email already taken", html)
            self.assertIn("<!--Testing string for signup!!!!!! :)-->", html)

    def test_user_authenticate(self):
        """Test that the authenticate route works properly
        - successful login given valid username and password"""

        with self.client as c:
            resp = c.post(
                            "/login",
                            data={
                                "username": "u1",
                                "password": "password",
                            },
                            follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<!--String for testing: Home route!!!!!:)-->", html)
            self.assertIn("@u1", html)

    def test_user_authenticate_fail_username(self):
        """Test that the authenticate route works properly
        - fails if username not found"""

        with self.client as c:
            resp = c.post(
                            "/login",
                            data={
                                "username": "u3",
                                "password": "password",
                            },
                            follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<!--String for testing: Login route!!!!!:(-->", html)
            self.assertIn("Invalid credentials.", html)

    def test_user_authenticate_fail_username_pwd(self):
        """Test that the authenticate route works properly
        - fails if incorrect password/username combination"""

        with self.client as c:
            resp = c.post(
                            "/login",
                            data={
                                "username": "u1",
                                "password": "BADpassword",
                            },
                            follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<!--String for testing: Login route!!!!!:(-->", html)
            self.assertIn("Invalid credentials.", html)

    def test_user_logout(self):
        """Test that the logout route works properly
        -successful logs out previously logged in user and erases the session"""

        with self.client as c:

            resp = c.post(
                            "/logout",
                            follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<!--String for testing: Login route!!!!!:(-->", html)
            self.assertIn("You have been logged out.", html)

    def test_list_users_in_session(self):
        """Test that list_users route works properly"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for index page!!!!! :D-->", html)
            self.assertIn("@u1", html)
            self.assertIn("@u2", html)

    def test_list_users_not_in_session(self):
        """Test that list_users route
        redirects to register page if user not logged in
        and flashes unauthorized"""

        with self.client as c:

            resp = c.get("/users", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

    def test_show_user_profile_in_session(self):
        """Test that show_user_profile route works properly"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for user details!!!!! :D-->", html)
            self.assertIn("<!--Test string for show page-->", html)
            self.assertIn("@u1", html)

    def test_show_user_profile_not_in_session(self):
        """Test that user profile route
        redirects to register page if user not logged in
        and flashes unauthorized"""

        with self.client as c:

            resp = c.get(f"/users/{self.u1_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

    def test_show_following_in_session(self):
        """Test that show_following route works properly"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/following")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for user details!!!!! :D-->", html)
            self.assertIn("<!--Test string for following page-->", html)
            self.assertIn("@u1", html)
            self.assertNotIn("@u2", html)

    def test_show_following_not_in_session(self):
        """Test that show_following route
        redirects to register page if user not logged in
        and flashes unauthorized"""

        with self.client as c:

            resp = c.get(f"/users/{self.u1_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)
            
#TODO: COPY the above 2 tests for user_followers

# class FollowModelTestCase(TestCase):
#     def setUp(self):
#         User.query.delete()

#         u1 = User.signup("u1", "u1@email.com", "password", None)
#         u2 = User.signup("u2", "u2@email.com", "password", None)
#         #TODO: u2 already follows u1 make a instance of follow

#         db.session.commit()
#         self.u1_id = u1.id
#         self.u2_id = u2.id

#         self.client = app.test_client()
#         #TODO: add followers/followings etc. NOT DONE.

#     def tearDown(self):
#         db.session.rollback()

#     def test_follow_repr(self):
#         """Test that the follow repr works properly
#         - shows followed user id and following user id
#         """


#     def test_user_following(self):
#         """Tests that the following route works as expected for follows
#         - detects that u1 does not follow u2
#         - u1 can follow u2
#         - detects u1 following u2
#         - detects u2 followed by u1
#         """
#         ...

#     def test_user_unfollow(self):
#         """Tests that the following route works as expected for unfollows
#         - u2 can unfollow u1
#         - detects that u2 does not follow u1"""
#         ...



