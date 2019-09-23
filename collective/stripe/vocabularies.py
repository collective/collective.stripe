from collective.stripe.utils import IStripeUtility
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class StripePlansVocabulary(object):

    def __call__(self, context):
        return self.get_plans(context)

    def get_plans(self, context):
        api = getUtility(IStripeUtility).get_stripe_api(context)
        terms = []

        for info in api.Plan.all()['data']:
            name = '%s (per %s)' % (info['name'], info['interval'])
            terms.append(SimpleVocabulary.createTerm(info['id'], info['id'], name))

        return SimpleVocabulary(terms)


StripePlansVocabularyFactory = StripePlansVocabulary()
