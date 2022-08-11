"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from models import db, User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = 'curr_user'

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

    def test_user_signup(self):
        """Test that the user signup works properly"""

        # valid username and email
        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.commit()
        self.assertEqual(User.query.get(u3.id).username, "u3")

        # invalid username
        User.signup("u2", "u4@email.com", "password", None)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # invalid email
        User.signup("u5", "u2@email.com", "password", None)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_user_authenticate(self):
        """Test that the classmethod authenticate()"""

        # valid username and email
        u2 = User.authenticate("u2", "password")
        self.assertEqual(User.query.get(self.u2_id), u2)

        # invalid username
        self.assertFalse(User.authenticate("u3", "password"))

        # invalid username and password combination
        self.assertFalse(User.authenticate("u1", "BADpassword"))

