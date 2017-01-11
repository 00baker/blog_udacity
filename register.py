import re
import hmac

import webapp2

from google.appengine.ext import db

from user import User
from post import Post
from comment import Comment
from like import Like
from login import lo
import myHelper

class Register(Signup):
    def done(self):
        # Make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')