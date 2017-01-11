import re
import hmac

import webapp2

from google.appengine.ext import db

from user import User
from post import Post
from comment import Comment
from like import Like
from login import Login
from signup import Signup
from editcomment import EditComment
from editpost import EditPost
from deletepost import DeletePost
from deletecomment import DeleteComment
from newpost import NewPost
import myHelper

secret = 'secured_secured'


def make_secure_val(val):
    """
        Creates secure value using secret.
    """
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    """
        Verifies secure value against secret.
    """
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


class BlogHandler(webapp2.RequestHandler):
    """
        This is a BlogHandler Class, inherits webapp2.RequestHandler,
        and provides helper methods.
    """
    def write(self, *a, **kw):
        """
            This methods write output to client browser.
        """
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """
            This methods renders html using template.
        """
        params['user'] = self.user
        return myHelper.jinja_render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        """
            Sets secure cookie to browser.
        """
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        """
            Reads secure cookie to browser.
        """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        """
            Verifies user existance.
        """
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """
            Removes login information from cookies.
        """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """
            This methods gets executed for each page and
            verfies user login status, using oookie information.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class BlogFront(BlogHandler):
    def get(self):
        """
            This renders home page with all posts, sorted by date.
        """
        deleted_post_id = self.request.get('deleted_post_id')
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts, deleted_post_id=deleted_post_id)


class PostPage(BlogHandler):
    def get(self, post_id):
        """
            This renders home post page with content, comments and likes.
        """
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        comments = db.GqlQuery("select * from Comment where post_id = " +
                               post_id + " order by created desc")

        likes = db.GqlQuery("select * from Like where post_id="+post_id)

        if not post:
            self.error(404)
            return

        error = self.request.get('error')

        self.render("permalink.html", post=post, noOfLikes=likes.count(),
                    comments=comments, error=error)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        """
            On posting comment, new comment tuple is created and stored,
            with relationship data of user and post.
        """
        c = ""
        if(self.user):
            # On clicking like, post-like value increases.
            if(self.request.get('like') and
               self.request.get('like') == "update"):
                likes = db.GqlQuery("select * from Like where post_id = " +
                                    post_id + " and user_id = " +
                                    str(self.user.key().id()))

                if self.user.key().id() == post.user_id:
                    self.redirect("/blog/" + post_id +
                                  "?error=You cannot like your " +
                                  "post.!!")
                    return
                elif likes.count() == 0:
                    l = Like(parent=blog_key(), user_id=self.user.key().id(),
                             post_id=int(post_id))
                    l.put()

            # On commenting, it creates new comment tuple
            if(self.request.get('comment')):
                c = Comment(parent=blog_key(), user_id=self.user.key().id(),
                            post_id=int(post_id),
                            comment=self.request.get('comment'))
                c.put()
        else:
            self.redirect("/login?error=You need to login before " +
                          "performing edit, like or commenting.!!")
            return

        comments = db.GqlQuery("select * from Comment where post_id = " +
                               post_id + "order by created desc")

        likes = db.GqlQuery("select * from Like where post_id="+post_id)

        self.render("permalink.html", post=post,
                    comments=comments, noOfLikes=likes.count(),
                    new=c)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')


app = webapp2.WSGIApplication([
                               ('/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/deletepost/([0-9]+)', DeletePost),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/deletecomment/([0-9]+)/([0-9]+)',
                                DeleteComment),
                               ('/blog/editcomment/([0-9]+)/([0-9]+)',
                                EditComment),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)
