"""User view tests."""

import os
from unittest import TestCase
from models import db, User, Follows
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = 'curr_user'

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app
app.config['WTF_CSRF_ENABLED'] = False

db.create_all()


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        Follows.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u6 = User.signup("u6", "u6@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u6_id = u6.id

        self.client = app.test_client()

        follow = Follows(
                          user_being_followed_id=self.u1_id,
                          user_following_id=self.u6_id,
                          )

        db.session.add(follow)
        db.session.commit()


    def tearDown(self):
        db.session.rollback()

class UserAddViewTestCase(UserBaseViewTestCase):
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


class UserAuthenticationTestCase(UserBaseViewTestCase):
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

class UsersViewTestCase(UserBaseViewTestCase):
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

class UserProfileViewTestCase(UserBaseViewTestCase):
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
                sess['curr_user'] = self.u6_id

            resp = c.get(f"/users/{self.u6_id}/following")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for user details!!!!! :D-->", html)
            self.assertIn("<!--Test string for following page-->", html)
            self.assertIn("@u1", html)
            self.assertIn("@u6", html)
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

    def test_show_followers_in_session(self):
        """Test that show_following route works properly"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/followers")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for user details!!!!! :D-->", html)
            self.assertIn("<!--Test string for followers page-->", html)
            self.assertIn("@u1", html)
            self.assertIn("@u6", html)
            self.assertNotIn("@u2", html)

    def test_show_followers_not_in_session(self):
        """Test that show_following route
        redirects to register page if user not logged in
        and flashes unauthorized"""

        with self.client as c:

            resp = c.get(f"/users/{self.u1_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

class UsersModifyFollowTestCase(UserBaseViewTestCase):
    def test_start_following_in_session(self):
        """Test that start_following route follows a user and redirects to
        following page """

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.post(f"/users/follow/{self.u2_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for user details!!!!! :D-->", html)
            self.assertIn("<!--Test string for following page-->", html)
            self.assertIn("@u1", html)
            self.assertIn("@u2", html)
            self.assertNotIn("@u6", html)
            self.assertEqual(Follows.query.filter_by(user_being_followed_id =
                                                     self.u2_id).count(), 1)

    def test_start_following_not_in_session(self):
        """Test that start_following redirects to register
        page if user not logged in and flashes unauthorized"""

        with self.client as c:

            resp = c.post(f"/users/follow/{self.u2_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

    def test_stop_following_in_session(self):
        """Test that stop_following route stops following a user and
        redirects to the following page """

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u6_id

            resp = c.post(f"/users/stop-following/{self.u1_id}",
                                                   follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for user details!!!!! :D-->", html)
            self.assertIn("<!--Test string for following page-->", html)
            self.assertIn("@u6", html)
            self.assertNotIn("@u2", html)
            self.assertNotIn("@u1", html)
            self.assertEqual(Follows.query.filter_by(user_being_followed_id =
                                                     self.u1_id).count(), 0)

    def test_stop_following_not_in_session(self):
        """Test that stop_following redirects to register
        page if user not logged in and flashes unauthorized"""

        with self.client as c:

            resp = c.post(f"/users/stop-following/{self.u1_id}",
                                                   follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

class UserViewEditProfileTestCase(UserBaseViewTestCase):
    def test_show_user_edit_profile_in_session(self):
        """Test user profile route renders correctly when in session"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.get("/users/profile")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for edit profile page-->", html)
            self.assertIn("u1", html)

    def test_show_user_edit_profile_not_in_session(self):
        """Test that stop_following redirects to register
        page if user not logged in and flashes unauthorized"""

        with self.client as c:

            resp = c.post(f"/users/profile", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

    def test_update_profile_in_session(self):
        """Test user profile updates successfully and redirects
        to users profile page and flashes success message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.post("/users/profile",
                          data={
                                "username": "u7",
                                "password": "password",
                                "email": "u7@email.com",
                                "bio": "Hey there unique testing bio!",
                                }, follow_redirects=True,)
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for user details!!!!! :D-->", html)
            self.assertIn("<!--Test string for show page-->", html)
            self.assertIn("@u7", html)
            self.assertIn("Hey there unique testing bio!", html)
            self.assertEqual(User.query.filter_by(username='u7').count(), 1)

    def test_update_profile_in_session_bad_credentials(self):
        """Test user profile flashes alert re-renders update form"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.post("/users/profile",
                          data={
                                "username": "u7",
                                "password": "BADpassword",
                                "email": "u7@email.com",
                                "bio": "Hey there unique testing bio!",
                                })
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Test string for edit profile page-->", html)
            self.assertIn("Invalid password", html)
            self.assertIn("u7", html)
            self.assertIn("Hey there unique testing bio!", html)

class UserViewDeleteUserCase(UserBaseViewTestCase):
    def test_delete_user_in_session(self):
        """Test user profile flashes alert re-renders update form"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.u1_id

            resp = c.post("/users/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!--Testing string for signup!!!!!! :)-->", html)
            self.assertEqual(User.query.filter_by(id=self.u1_id).count(), 0)


    def test_delete_user_not_session(self):
        """Test user profile flashes alert re-renders update form"""

        with self.client as c:

            resp = c.post("/users/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)
















