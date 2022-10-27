"""Message model tests."""

import os
from unittest import TestCase
from models import db, User, Message

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


class MessageModelTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id

        msg1 = Message(text="test_text", user_id=u1.id)

        db.session.add(msg1)
        db.session.commit()
        self.msg1_id = msg1.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Test message model"""
        msg1 = Message.query.get(self.msg1_id)
        u1 = User.query.get(self.u1_id)

        self.assertEqual(msg1.user, u1)
        #TODO: length of user.messages is 1 & test likes

    def test_message_repr(self):
        """Test that the message repr works properly
        - shows msg1's id, text, timestamp and user_id"""
        msg1 = Message.query.get(self.msg1_id)

        self.assertEqual(repr(msg1),
                         f"<Msg #{self.msg1_id}: test_text, {msg1.timestamp}, {self.u1_id}>")