# -*- coding: utf-8 -*-
import unittest
import time
from flask import current_app
from app import create_app, DB
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        DB.create_all()

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        DB.session.add(u)
        DB.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        DB.session.add(u1)
        DB.session.add(u2)
        DB.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='cat')
        DB.session.add(u)
        DB.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='cat')
        DB.session.add(u)
        DB.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u = User(password='cat')
        DB.session.add(u)
        DB.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    def test_valid_email_change_token(self):
        u = User(email='test@example.com', password='cat')
        DB.session.add(u)
        DB.session.commit()
        token = u.generate_email_change_token('hello@example.com')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'hello@example.com')

    def test_invalid_email_change_token(self):
        u1 = User(email='hello@example.com', password='cat')
        u2 = User(email='world@example.com', password='dog')
        DB.session.add(u1)
        DB.session.add(u2)
        DB.session.commit()
        token = u1.generate_email_change_token('test@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'world@example.com')

    def test_duplicate_email_change_token(self):
        u1 = User(email='hello@example.com', password='cat')
        u2 = User(email='world@example.com', password='dog')
        DB.session.add(u1)
        DB.session.add(u2)
        DB.session.commit()
        token = u2.generate_email_change_token('hello@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'world@example.com')