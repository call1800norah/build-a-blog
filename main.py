#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Post(db.Model):
    title = db.StringProperty(required = True)
    created= db.DateTimeProperty(auto_now_add = True)
    post = db.TextProperty(required = True)

class MainBlogHandler(webapp2.RequestHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post order by created desc limit 5")
        t = jinja_env.get_template("main_blog.html")

        content = t.render(posts=posts)
        self.response.write(content)

class Handler(MainBlogHandler):
   def get(self):

       self.redirect('/blog')

class ViewPostHandler(MainBlogHandler):
    def renderError(self, error_code):
        self.error(error_code)

    def get(self,id):
        post = Post.get_by_id(int(id))
        t = jinja_env.get_template("view.html")
        content = t.render(post=post,error = self.request.get("error"))

        if not post:
           self.renderError(400)
           return
        self.response.write(content)

class NewPostHandler(MainBlogHandler):
    def get(self, title="", post="", error=""):
        t = jinja_env.get_template("new_posts.html")
        content = t.render(title=title,post=post,error=error)
        self.response.write(content)

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            post = Post(title=title,post=post)
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "We need both a title and a body!"
            t = jinja_env.get_template("new_posts.html")
            content = t.render(title=title,post=post,error=error)
            self.response.write(content)

app = webapp2.WSGIApplication([
        ('/',Handler),
        ('/blog', MainBlogHandler),
        webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
        ('/blog/newpost', NewPostHandler),

      ], debug=True)
