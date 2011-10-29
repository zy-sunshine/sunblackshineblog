#coding=utf-8
### Extern Django Model adapt to GAE

from django.db import models

from django.contrib.auth.models import User
#from djangotoolbox.fields import ListField, EmbeddedModelField, BlobField
from djangotoolbox import fields
from djangotoolbox.fields import EmbeddedModelField

#class GaeManager(db.Manager):
#        # 用 manager 去解决这样的 object filter 问题
#        
#        #cls.objects._filter = cls.objects.filter
#        #cls.objects.filter = filter_v2
#        #return cls.objects
#    #@classmethod
#    #def order(cls, *args):
#    #    t = type(cls)
#    #    return cls.order_by(*args)
#    def order(self, *args):
#        return self.order_by(*args)
#        
#    @classmethod    
#    def fetch(cls, limit):
#        return cls[0:limit]
#        
#    def filter(self, __arg1 = None, __arg2 = None, *args, **kwds):
#        if type(__arg1) == str and __arg1[-1] in ('=', '<', '>'):
#            if __arg1[-1] == '=':
#                if __arg1[-2] == '<':
#                    # <=
#                    field = __arg1[:-3].strip()
#                    kwds[field + '__lte'] = __arg2
#                elif __arg1[-2] == '>':
#                    # >=
#                    field = __arg1[:-3].strip()
#                    kwds[field + '__gte'] = __arg2
#                else:
#                    # =
#                    field = __arg1[:-2].strip()
#                    kwds[field] = __arg2
#            elif __arg1[-1] == '<':
#                # '<'
#                field = __arg1[:-2].strip()
#                kwds[field + '__lt'] = __arg2
#            else:
#                # '>'
#                field = __arg1[:-2].strip()
#                kwds[field + '__gt'] = __arg2
#        else:
#            if __arg1 is not None:
#                kwds['__arg1'] = __arg1
#            if __arg2 is not None:
#                kwds['__arg2'] = __arg2
#        return super(GaeManager, self).filter(*args, **kwds)
#class SeparatedStringField(models.TextField):
#    __metaclass__ = db.SubfieldBase
#
#    def __init__(self, *args, **kwargs):
#        self.token = kwargs.pop('token', ',')
#        super(SeparatedStringField, self).__init__(*args, **kwargs)
#
#    def to_python(self, value):
#        if not value: return
#        if isinstance(value, list):
#            return value
#        return value.split(self.token)
#
#    def get_db_prep_value(self, value):
#        if not value: return
#        assert(isinstance(value, list) or isinstance(value, tuple))
#        return self.token.join([unicode(s) for s in value])
#
#    def value_to_string(self, obj):
#        value = self._get_val_from_obj(obj)

#class SeparatedListField(db.TextField):
#    __metaclass__ = db.SubfieldBase
#
#    def __init__(self, *args, **kwargs):
#        super(SeparatedListField, self).__init__(*args, **kwargs)
#
#    def to_python(self, value):
#        if not value: return
#        if isinstance(value, list):
#            return value
#        return pickle.loads(value)
#
#    def get_db_prep_value(self, value):
#        if not value: return
#        assert(isinstance(value, list) or isinstance(value, tuple))
#        return pickle.dumps(value)
#
#    def value_to_string(self, obj):
#        value = self._get_val_from_obj(obj)

def externdbModel(models):
    def StringProperty(max_length=500, verbose_name=None, multiline=False, choices = None, *args, **kwds):
        kwds['max_length'] = max_length
        kwds['verbose_name'] = verbose_name
        return models.CharField(*args, **kwds)
    def TextProperty(required = True, *args, **kwds):
        if not required:
            kwds['blank'] = True
            kwds['null'] = True
        return models.TextField(*args, **kwds)
    def FloatProperty(*args, **kwds):
        return models.FloatField(*args, **kwds)
    def IntegerProperty(*args, **kwds):
        return models.IntegerField(*args, **kwds)
    def BooleanProperty(*args, **kwds):
        return models.BooleanField(*args, **kwds)
    def SelfReferenceProperty(*args, **kwds):
        #return models.ForeignKey('self', *args, **kwds)
        return EmbeddedModelField('self')
    def DateTimeProperty(*args, **kwds):
        return models.DateTimeField(*args, **kwds)
    def UserProperty(required = True, *args, **kwds):
        if not required:
            kwds['blank'] = True
            kwds['null'] = True
        #return models.ForeignKey(User, *args, **kwds)
        EmbeddedModelField('User')
        #OneToOneField
    def StringListProperty(*args, **kwds):
        #return SeparatedStringField(*args, **kwds)
        return fields.ListField(*args, **kwds)
    def ListProperty(*args, **kwds):
        #return SeparatedListField(*args, **kwds)
        return fields.ListField(*args, **kwds)
    def LinkProperty(*args, **kwds):
        return models.TextField(*args, **kwds)
    def ReferenceProperty(reference_class = None, **kwds):
        #return models.ForeignKey(reference_class, **kwds)
        return EmbeddedModelField(reference_class)
    def EmailProperty(*args, **kwds):
        return models.EmailField(*args, **kwds)
    def URLProperty(*args, **kwds):
        return models.TextField(*args, **kwds)
    def BlobProperty(*args, **kwds):
        return fields.BlobField(*args, **kwds)
        
    models.StringProperty = StringProperty
    models.TextProperty = TextProperty
    models.FloatProperty = FloatProperty
    models.IntegerProperty = IntegerProperty
    #models.BooleanProperty = lambda *args, **kwds: models.BooleanField(*args, **kwds)
    models.BooleanProperty = BooleanProperty
    models.SelfReferenceProperty = SelfReferenceProperty
    models.DateTimeProperty = DateTimeProperty
    models.UserProperty = UserProperty
    models.StringListProperty = StringListProperty
    models.ListProperty = ListProperty
    models.LinkProperty = LinkProperty
    models.URLProperty = URLProperty
    models.ReferenceProperty = ReferenceProperty
    models.EmailProperty = EmailProperty
    models.BlobProperty = BlobProperty
    
externdbModel(models)

#class Model(db.Model):
#    key_name = db.StringProperty(max_length = 255, unique=True)
#    #objects = GaeManager()
#    def __init__(self, key_name=None, *args, **kwds):
#        super(Model, self).__init__(*args, **kwds)
#        if key_name is not None:
#            self.key_name = key_name
#    class Meta:
#        abstract=True
#    @classmethod
#    def get_by_key_name(cls, key_name):
#        #import pdb; pdb.set_trace()
#        try:
#            ret = cls.objects.get(key_name = key_name)
#        except cls.DoesNotExist:
#            return None
#        return ret
#    @classmethod
#    def get_or_insert(cls, key_name):
#        try:
#            ret = cls.objects.get(key_name = key_name)
#        except cls.DoesNotExist:
#            ret = cls()
#            ret.key_name = key_name
#        return ret
#
#    @classmethod
#    def all(cls):
#        return cls.objects
#        
#    def put(self):
#        self.save()
#        
#    def key(self):
#        return self.id