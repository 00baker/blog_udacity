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

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        """
            Creates new post and redirect to new post page.
        """
        if not self.user:
            return self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent=blog_key(), user_id=self.user.key().id(),
                     subject=subject, content=content)
            p.put()
            return self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
                        content=(content, error=error)