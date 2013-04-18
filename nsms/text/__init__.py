from django.contrib.auth.models import User
from django.template.base import Template
from django.template.context import Context
from nsms.text.models import Text

class LazyText(object):
    
    def __init__(self, text, variables):
        self.text = text
        self.variables = variables

    def __mod__(self, b):
        return unicode(self).__mod__(b)

    def __eq__(self, b):
        return unicode(self) == b

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        # get the actual string from our Text object, at this point the currently
        # activated language will be used to get the string
        text = self.text.text

        if self.variables is None:
            return text
        else:
            try:
                # our text is a template, perform substitutions on it
                template = Template("%s" % text)
                return template.render(Context(self.variables))
            except Exception as e:
                # if we throw an error, display the raw template
                return text

def gettext(slug, default_string, variables=None):
    text = Text.objects.filter(slug=slug)

    if text:
        text = text[0]
    else:
        text = Text.objects.create(slug=slug,
                                   text=default_string,
                                   created_by=User.objects.get(id=-1),
                                   modified_by=User.objects.get(id=-1))

    return LazyText(text, variables)

