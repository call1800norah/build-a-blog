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

class Post(db.Model):
    subject = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    content = db.TextProperty(required = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class Handler(webapp2.RequestHandler):
    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("We need both a subject and some contents in blog!")

class MainBlogHandler(handler):
    def get(self):
       posts = db.GqlQuery("SELECT * FROM Post order bt created desc")
       t = jinja_env.get_template("base.html")
       content = t.render(posts=posts,error = self.request.get("error"))
       self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("We need both a subject and some contents in blog!")

    def get(self,id):
        key = Post.get_by_id(int(id))

        if not key:
            self.renderError(400)
            return

        self.response.write("new_blog.html",key = key)

class NewPostHandler(webapp2.RequestHandler):
    def get(self,subject="",blog="",error=""):
        t = jinja_env.get_template("new_posts.html")
        content = t.render(subject=subject,blog=blog,error=error)
        self.response.write(content)

    def post(self):
        subject = self.request.get("subject")
        blog = self.request.get("blog")

        if subject and blog:
            self.response.write("thanks!")
        else:
            error = "We need both a subject and some contents in blog!"
            self.response.write(subject=subject,blog=blog,error=error)





app = webapp2.WSGIApplication([
       webapp2.Route('/', Handler),
       webapp2.Route('/blog', MainBlogHandler),
       webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
       webapp2.Route('/blog/newpost', NewPostHandler),

      ], debug=True)
