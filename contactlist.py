import os
import re
import urllib
from google.appengine.ext import ndb
from google.appengine.api import images
import webapp2
import jinja2
import uuid

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

CONTACTS_LIST = 'contacts_list'

def contacts_key(CONTACTS_LIST):
	return ndb.Key('AddContact', CONTACTS_LIST)

class Contacts(ndb.Model):
	firstname = ndb.StringProperty()
	lastname = ndb.StringProperty()
	email = ndb.StringProperty(indexed=False)
	phone = ndb.StringProperty(indexed=False)
	address = ndb.StringProperty(indexed=False)
	state = ndb.StringProperty()
	photo = ndb.BlobProperty(indexed=False)
	created = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
	def get(self):
		
		contacts = Contacts.query(ancestor=contacts_key(CONTACTS_LIST)).order(Contacts.lastname)

		template_values = {
			'contacts': contacts,
		}

		template = JINJA_ENVIRONMENT.get_template('main.html')
		self.response.write(template.render(template_values))

class AddContact(webapp2.RequestHandler):
	def post(self):
		contact = Contacts(parent=contacts_key(CONTACTS_LIST))

		contact.firstname = self.request.get('fname')
		contact.lastname = self.request.get('lname')
		contact.email = self.request.get('email')
		contact.phone = re.sub("\D", "", self.request.get('phone'))	#strip phone number of all but digits
		contact.address = self.request.get('addr')
		contact.state = self.request.get('state')
		thumb = str(self.request.get('pic'))
		if thumb:
			thumb = str(images.resize(thumb, width=50, height=50))
			contact.photo = thumb
		contact.put()

		self.redirect('/')

class UpdateContact(webapp2.RequestHandler):
	def post(self):
		up_key = ndb.Key(urlsafe=self.request.get('up_id'))
		contact = up_key.get()

		contact.firstname = self.request.get('fname')
		contact.lastname = self.request.get('lname')
		contact.email = self.request.get('email')
		contact.phone = re.sub("\D", "", self.request.get('phone'))	#strip phone number of all but digits
		contact.address = self.request.get('addr')
		contact.state = self.request.get('state')
		thumb = str(self.request.get('pic'))
		if thumb:
			thumb = str(images.resize(thumb, width=50, height=50))
			contact.photo = thumb
		contact.put()

		self.redirect('/')

class DeleteContact(webapp2.RequestHandler):
	def post(self):
		del_key = ndb.Key(urlsafe=self.request.get('del_id'))
		del_key.delete()
		self.redirect('/')

class Image(webapp2.RequestHandler):
	def get(self):
		key = ndb.Key(urlsafe=self.request.get('img_id'))
		contact = key.get()
		if contact.photo:
			self.response.headers['Content-Type'] = 'image/jpeg'
			self.response.out.write(contact.photo)
		else:
			self.response.out.write('No image')	

class Edit(webapp2.RequestHandler):
	def get(self):
		edit_key = ndb.Key(urlsafe=self.request.get('edit_id'))
		contact = edit_key.get()

		template_values = {
			'firstname': contact.firstname,
			'lastname': contact.lastname,
			'email': contact.email,
			'phone': contact.phone,
			'address': contact.address,
			'state': contact.state,
			'photo': contact.photo,
			'edit_key': edit_key
		}

		template = JINJA_ENVIRONMENT.get_template('edit.html')
		self.response.write(template.render(template_values))

class SortState(webapp2.RequestHandler):
	def get(self):
		contacts = Contacts.query(ancestor=contacts_key(CONTACTS_LIST)).order(Contacts.state)

		template_values = {
			'contacts': contacts,
		}

		template = JINJA_ENVIRONMENT.get_template('main.html')
		self.response.write(template.render(template_values))


class Filter(webapp2.RequestHandler):
	def get(self):
		template_values = {}

		template = JINJA_ENVIRONMENT.get_template('filter.html')
		self.response.write(template.render(template_values))

	def post(self):
		filtState = str(self.request.get('filtState'))
		stateContacts = ndb.gql("SELECT * FROM Contacts WHERE state = :1 ORDER BY lastname ASC", filtState)

		template_values = {
			'contacts': stateContacts,
		}

		template = JINJA_ENVIRONMENT.get_template('filter.html')
		self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/img', Image),
    ('/add', AddContact),
    ('/edit', Edit),
    ('/update', UpdateContact),
    ('/delete', DeleteContact),
    ('/sortstate', SortState),
    ('/filter', Filter),
], debug=True)