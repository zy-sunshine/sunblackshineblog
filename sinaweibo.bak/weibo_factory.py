#encoding=utf8
#file:weibo_factory.py
#@author:carlos
#@date:2011-2-13
#@link:tieniuzai.com
from weibopy.auth import BasicAuthHandler
from weibopy.api import API
class SinaWeibo:

	def __init__(self,username,password):
		self.username = username
		self.password = password
		self.source ="app key" #在申请新浪微博开发者帐号并创建应用后获得

	def getAtt(self, key):
		try:
			return self.obj.__getattribute__(key)
		except Exception, e:
			print e
			return ''
		
	def getAttValue(self, obj, key):
		try:
			return obj.__getattribute__(key)
		except Exception, e:
			print e
			return ''

	def basicAuth(self):
		source = self.source
		self.auth = BasicAuthHandler(self.username, self.password)
		self.api = API(self.auth,source=source)

	def parse_timeline(self,timeline):
		result = []
		for line in timeline:
			self.obj = line
			item ={}
			user = self.getAtt("user")
			item['mid'] = self.getAtt("id")
			item['text'] = self.getAtt("text")
			item['pic'] = self.getAtt("thumbnail_pic")
			item['author_name']= user.screen_name
			item['author_id'] = user.id
			item['author_domain'] = user.domain
			item['author_profile_image']= user.profile_image_url
			item['created_at'] = self.getAtt('created_at')
			item['source'] = self.getAtt('source')
			item['retweeted_status'] = self.getAtt('retweeted_status')
			result.append(item)
		return result

	def get_myself(self):
		myself = self.api.get_user(id=1649938837)
		#myself = self.api.get_user(user_id=self.auth.get_username)
		self.obj = myself
		user={}
		user['profile_image_url'] = self.getAtt('profile_image_url')
		user['name']=self.getAtt("screen_name")
		user['description']=self.getAtt("description")
		use = self.auth.get_username()
		return user


			
	def user_timeline(self):
		timeline = self.api.user_timeline(count=10, page=1)
		result = self.parse_timeline(timeline)
		return result
			