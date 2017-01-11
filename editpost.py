import re
import hmac

import webapp2

from google.appengine.ext import db

from user import User
from post import Post
from comment import Comment
from like import Like
import myHelper

class EditPost(BlogHandler):
    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            if post.user_id == self.user.key().id():
                self.render("editpost.html", subject=post.subject,
                            content=post.content)
            else:
                self.redirect("/blog/" + post_id + "?error=You don't have " +
                              "access to edit this record.")
        else:
            self.redirect("/login?error=You need to be logged, " +
                          "in order to edit your post!!")

    def post(self, post_id):
        """
            Updates post.
        """
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % post_id)
        else:
            error = "subject and content, please!"
            self.render("editpost.html", subject=subject,
                        content=content, error=error)
