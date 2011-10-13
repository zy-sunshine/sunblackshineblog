from google.appengine.ext import db

class User(db.Model):
	user = db.UserProperty(required = False)
	dispname = db.StringProperty()
	email=db.StringProperty()
	website = db.LinkProperty()
	isadmin=db.BooleanProperty(default=False)
	isAuthor=db.BooleanProperty(default=True)
	#rpcpwd=db.StringProperty()

	def __unicode__(self):
		#if self.dispname:
			return self.dispname
		#else:
		#	return self.user.nickname()

	def __str__(self):
		return self.__unicode__().encode('utf-8')
