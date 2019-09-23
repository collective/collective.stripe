from collective.stripe.controlpanel import IStripeSettings
from collective.stripe.interfaces import IStripeModeChooser
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.site.hooks import getSite

import stripe


def get_settings():
    registry = getUtility(IRegistry)
    return registry.forInterface(IStripeSettings, False)


class IStripeUtility(Interface):
    """ A global utility providing methods to access the Stripe API """

    def get_stripe_api():
        """ returns the stripe api module with the api_key set from the control panel """

    def charge_card(token, amount, description, **kwargs):
        """ charges a card (represented by a Stripe.js card token) """

    def charge_customer(customer_id, amount, description, **kwargs):
        """ charges a customer looked up by customer_id.  customer must already exist """

    def create_customer(token, description, **kwargs):
        """ creates a customer using a card token from Stripe.js """

    def subscribe_customer(customer_id, plan, quantity, **kwargs):
        """ subscribe and existing customer to a plan.  if subscription
            already exists for the plan, the subscription is updated """


@implementer(IStripeUtility)
class StripeUtility(object):

    def get_stripe_api(self, context=None, mode=None):
        active_mode = 'live'
        settings = get_settings()

        if mode is not None:
            active_mode = mode
        else:
            active_mode = 'live'
            if settings.mode is not None:
                active_mode == settings.mode

            if active_mode != 'test' and context is not None:
                active_mode = self.get_mode_for_context(context)

        stripe.api_key = getattr(settings, '%s_secret_key' % active_mode)
        return stripe

    def get_mode_for_context(self, context):
        if IStripeModeChooser.providedBy(context):
            return context.get_stripe_mode()
        return get_settings().mode

    def charge_card(self, token, amount, description, context=None, **kwargs):
        settings = get_settings()
        stripe = self.get_stripe_api(context=context)

        res = stripe.Charge.create(
            amount = amount,
            currency = settings.currency,
            card = token,
            description = description,
            **kwargs
        )
        return res

    def charge_customer(self, customer_id, amount, description, context=None, **kwargs):
        settings = get_settings()
        stripe = self.get_stripe_api(context=context)

        res = stripe.Charge.create(
            amount = amount,
            currency = settings.currency,
            card = token,
            description = description,
            **kwargs
        )
        return res

    def create_customer(self, token, description, context=None, **kwargs):
        settings = get_settings()
        stripe = self.get_stripe_api(context=context)

        res = stripe.Customer.create(
            card = token,
            description = description,
            **kwargs
        )
        return res

    def subscribe_customer(self, customer_id, plan, quantity, context=None, **kwargs):
        settings = get_settings()
        stripe = self.get_stripe_api(context=context)

        cu = stripe.Customer.retrieve(customer_id)
        res = cu.update_subscription(
            plan=plan,
            quantity=quantity,
            **kwargs
        )
        return res


StripeUtilityFactory = StripeUtility()
