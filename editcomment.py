import re
import hmac

import webapp2

from google.appengine.ext import db

from user import User
from post import Post
from comment import Comment
from like import Like
import myHelper

class EditComment(BlogHandler):
    def get(self, post_id, comment_id):
        if self.user:
            key = db.Key.from_path('Comment', int(comment_id),
                                   parent=blog_key())
            c = db.get(key)
            if c.user_id == self.user.key().id():
                self.render("editcomment.html", comment=c.comment)
            else:
                self.redirect("/blog/" + post_id +
                              "?error=You don't have access to edit this " +
                              "comment.")
        else:
            self.redirect("/login?error=You need to be logged, in order to" +
                          " edit your post!!")

    def post(self, post_id, comment_id):
        """
            Updates post.
        """
        if not self.user:
            self.redirect('/blog')

        comment = self.request.get('comment')

        if comment:
            key = db.Key.from_path('Comment',
                                   int(comment_id), parent=blog_key())
            c = db.get(key)
            c.comment = comment
            c.put()
            self.redirect('/blog/%s' % post_id)
        else:
            error = "subject and content, please!"
            self.render("editpost.html", subject=subject,
                        content=content, error=error)