import os
import re
import hmac
import jinja2
import hashlib
import random

from string import letters
from google.appengine.ext import db

#### Jinja2 configuration
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

#### Global functions
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

#### Model keys
def users_key(group = 'default'):
	return db.Key.from_path('users', group)

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)




#### Validates the username, password, and email.
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
	return not email or EMAIL_RE.match(email)

#### For Security ####


#### Change the secret key
secret = 'iosdjfokweqr'

#### User security 

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)

def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def valid_pw(name, pw, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, pw, salt)

	#### Make Secure values
def make_secure_val(val):
	secured_value = hmac.new(secret, val).hexdigest()
	return '%s|%s' % (val, secured_value)

def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val