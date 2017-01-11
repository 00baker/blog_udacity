import re
import hmac

import webapp2

from google.appengine.ext import db

from user import User
from post import Post
from comment import Comment
from like import Like
import myHelper

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html', error=self.request.get('error'))

    def post(self):
        """
            Login validation.
        """
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)