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
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def get_posts(limit, offset):
    page = db.GqlQuery("SELECT * FROM Post order by created desc limit 5 offset 5")

class Post(db.Model):
    title = db.StringProperty(required = True)
    created= db.DateTimeProperty(auto_now_add = True)
    post = db.TextProperty(required = True)
    #last_modified = db.DateTimeProperty(auto_now = True)


class MainBlogHandler(webapp2.RequestHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post order by created desc limit 5")
        t = jinja_env.get_template("main_blog.html")
        content = t.render(posts=posts,error = self.request.get("error"))
        self.response.write(content)

class Handler(MainBlogHandler):
   def get(self):
        self.redirect("/blog")

class ViewPostHandler(MainBlogHandler):
    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")
    def get(self,id):
        entity = Post.get_by_id(int(id))
        t = jinja_env.get_template("view.html")
        content = t.render(entity=entity,error = self.request.get("error"))

        if not entity:
            self.renderError(400)
            return

        self.response.write(content)

class NewPostHandler(MainBlogHandler):
    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("We need both a subject and some contents in blog!")

    def get(self, title="", post="", error=""):
        t = jinja_env.get_template("new_posts.html")
        content = t.render(title=title,post=post,error=error)
        self.response.write(content)

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title=title,post=post)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "We need both a title and a body!"
            t = jinja_env.get_template("new_posts.html")
            content = t.render(title=title,post=post,error=error)
            self.response.write(content)





app = webapp2.WSGIApplication([
        webapp2.Route('/',Handler),
        webapp2.Route('/blog', MainBlogHandler),
        webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
        webapp2.Route('/blog/newpost', NewPostHandler),

      ], debug=True)
