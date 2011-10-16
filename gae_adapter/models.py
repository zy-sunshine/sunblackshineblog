### Extern Django Model adapt to GAE

from django.db import models as db
from django.contrib.auth.models import User

class SeparatedStringField(db.TextField):
    __metaclass__ = db.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedStringField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value):
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)

class SeparatedListField(db.TextField):
    __metaclass__ = db.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(SeparatedListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return pickle.loads(value)

    def get_db_prep_value(self, value):
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return pickle.dumps(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)


def externdbModel(models):
    def StringProperty(max_length=500, verbose_name=None, multiline=False, **kwds):
        return models.CharField(max_length=max_length, verbose_name=verbose_name, db_index=True, **kwds)
    def TextProperty(*args, **kwds):
        return models.TextField(*args, **kwds)
    def FloatProperty(*args, **kwds):
        return models.FloatField(*args, **kwds)
    def IntegerProperty(*args, **kwds):
        return models.IntegerField(*args, **kwds)
    def BooleanProperty(*args, **kwds):
        return models.BooleanField(*args, **kwds)
    def SelfReferenceProperty(*args, **kwds):
        return models.ForeignKey('self')
    def DateTimeProperty(*args, **kwds):
        return models.DateTimeField(*args, **kwds)
    def UserProperty(*args, **kwds):
        return models.ForeignKey(User)
        #OneToOneField
    def StringListProperty(*args, **kwds):
        return SeparatedStringField(*args, **kwds)
    def ListProperty(*args, **kwds):
        return SeparatedListField(*args, **kwds)

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
    
externdbModel(db)

class Model(db.Model):
    key_name = db.StringProperty(max_length = 255, unique=True)
    def __init__(self, key_name=None, *args, **kwds):
        super(Model, self).__init__(*args, **kwds)
        if key_name is not None:
            self.key_name = key_name
    class Meta:
        abstract=True
    @classmethod
    def get_by_key_name(cls, key_name):
        #import pdb; pdb.set_trace()
        try:
            ret = cls.objects.get(key_name = key_name)
        except cls.DoesNotExist:
            return None
        return ret
    @classmethod
    def get_or_insert(cls, key_name):
        try:
            ret = cls.objects.get(key_name = key_name)
        except cls.DoesNotExist:
            ret = cls()
            ret.key_name = key_name
        return ret
        
    def put(self):
        self.save()
