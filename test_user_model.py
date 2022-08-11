"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

app.config['WTF_CSRF_ENABLED'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
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

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_user_repr(self):
        """Test that the user repr works properly
        - shows u1's id, username, email"""
        u1 = User.query.get(self.u1_id)

        self.assertEqual(repr(u1), f"<User #{self.u1_id}: u1, u1@email.com>")


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
            self.assertIn("Username already taken", html)
            self.assertIn("<!--Testing string for signup!!!!!! :)-->", html)

#     def test_user_authenticate(self):
#         """Test that the authenticate route works properly
#         - successful login given valid username and password
#         - fails if username not found
#         - fails if username and password do not match"""
#         ...

#     def test_user_logout(self):
#         """Test that the logout route works properly
#         - cannot logout without an existing user
#         - successful logs out previously logged in user and erases the session"""
#         ...


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



