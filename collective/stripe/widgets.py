from zope.component import adapter, getMultiAdapter
from zope.interface import implementer, implements, implementsOnly

from z3c.form.interfaces import IField, IFieldWidget, IFormLayer, NOVALUE
from z3c.form.widget import FieldWidget
from z3c.form.browser import text

from Products.Five.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse, NotFound

class StripeTokenWidget(text.TextWidget):
    """A widget for a named file object
    """
    implementsOnly(IFieldWidget)

    klass = u'stripe-token-widget'
    value = None # don't default to a string

    def extract(self, default=NOVALUE):
        value = super(StripeTokenWidget, self).extract(default)
        return value

@implementer(IFieldWidget)
@adapter(IField, IFormLayer)
def StripeTokenWidget(field, request):
    return FieldWidget(field, StripeTokenWidget(request))
