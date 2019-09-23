from collective.stripe.interfaces import IAccountApplicationDeauthorizedEvent
from collective.stripe.interfaces import IAccountUpdatedEvent
from collective.stripe.interfaces import IBalanceAvailableEvent
from collective.stripe.interfaces import IChargeCapturedEvent
from collective.stripe.interfaces import IChargeDisputeClosedEvent
from collective.stripe.interfaces import IChargeDisputeCreatedEvent
from collective.stripe.interfaces import IChargeDisputeUpdatedEvent
from collective.stripe.interfaces import IChargeFailedEvent
from collective.stripe.interfaces import IChargeRefundedEvent
from collective.stripe.interfaces import IChargeSucceededEvent
from collective.stripe.interfaces import ICouponCreatedEvent
from collective.stripe.interfaces import ICouponDeletedEvent
from collective.stripe.interfaces import ICustomerCardCreatedEvent
from collective.stripe.interfaces import ICustomerCardDeletedEvent
from collective.stripe.interfaces import ICustomerCardUpdatedEvent
from collective.stripe.interfaces import ICustomerCreatedEvent
from collective.stripe.interfaces import ICustomerDeletedEvent
from collective.stripe.interfaces import ICustomerDiscountCreatedEvent
from collective.stripe.interfaces import ICustomerDiscountDeletedEvent
from collective.stripe.interfaces import ICustomerDiscountUpdatedEvent
from collective.stripe.interfaces import ICustomerSubscriptionCreatedEvent
from collective.stripe.interfaces import ICustomerSubscriptionDeletedEvent
from collective.stripe.interfaces import ICustomerSubscriptionTrialWillEndEvent
from collective.stripe.interfaces import ICustomerSubscriptionUpdatedEvent
from collective.stripe.interfaces import ICustomerUpdatedEvent
from collective.stripe.interfaces import IInvoiceCreatedEvent
from collective.stripe.interfaces import IInvoiceItemCreatedEvent
from collective.stripe.interfaces import IInvoiceItemDeletedEvent
from collective.stripe.interfaces import IInvoiceItemUpdatedEvent
from collective.stripe.interfaces import IInvoicePaymentFailedEvent
from collective.stripe.interfaces import IInvoicePaymentSucceededEvent
from collective.stripe.interfaces import IInvoiceUpdatedEvent
from collective.stripe.interfaces import IPingEvent
from collective.stripe.interfaces import IPlanCreatedEvent
from collective.stripe.interfaces import IPlanDeletedEvent
from collective.stripe.interfaces import IPlanUpdatedEvent
from collective.stripe.interfaces import ITransferCreatedEvent
from collective.stripe.interfaces import ITransferFailedEvent
from collective.stripe.interfaces import ITransferPaidEvent
from collective.stripe.interfaces import ITransferUpdatedEvent
from collective.stripe.utils import IStripeUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from zope.component import getUtility
from zope.event import notify
import json


EVENTS_MAP = {
    'account.updated': IAccountUpdatedEvent,
    'account.application.deauthorized': IAccountApplicationDeauthorizedEvent,
    'balance.available': IBalanceAvailableEvent,
    'charge.succeeded': IChargeSucceededEvent,
    'charge.failed': IChargeFailedEvent,
    'charge.refunded': IChargeRefundedEvent,
    'charge.captured': IChargeCapturedEvent,
    'charge.dispute.created': IChargeDisputeCreatedEvent,
    'charge.dispute.updated': IChargeDisputeUpdatedEvent,
    'charge.dispute.closed': IChargeDisputeClosedEvent,
    'customer.created': ICustomerCreatedEvent,
    'customer.updated': ICustomerUpdatedEvent,
    'customer.deleted': ICustomerDeletedEvent,
    'customer.card.created': ICustomerCardCreatedEvent,
    'customer.card.updated': ICustomerCardUpdatedEvent,
    'customer.card.deleted': ICustomerCardDeletedEvent,
    'customer.subscription.created': ICustomerSubscriptionCreatedEvent,
    'customer.subscription.updated': ICustomerSubscriptionUpdatedEvent,
    'customer.subscription.deleted': ICustomerSubscriptionDeletedEvent,
    'customer.subscription.trial_will_end': ICustomerSubscriptionTrialWillEndEvent,
    'customer.discount.created': ICustomerDiscountCreatedEvent,
    'customer.discount.updated': ICustomerDiscountUpdatedEvent,
    'customer.discount.deleted': ICustomerDiscountDeletedEvent,
    'invoice.created': IInvoiceCreatedEvent,
    'invoice.updated': IInvoiceUpdatedEvent,
    'invoice.payment_succeeded': IInvoicePaymentSucceededEvent,
    'invoice.payment_failed': IInvoicePaymentFailedEvent,
    'invoiceitem.created': IInvoiceItemCreatedEvent,
    'invoiceitem.updated': IInvoiceItemUpdatedEvent,
    'invoiceitem.deleted': IInvoiceItemDeletedEvent,
    'plan.created': IPlanCreatedEvent,
    'plan.updated': IPlanUpdatedEvent,
    'plan.deleted': IPlanDeletedEvent,
    'coupon.created': ICouponCreatedEvent,
    'coupon.deleted': ICouponDeletedEvent,
    'transfer.created': ITransferCreatedEvent,
    'transfer.updated': ITransferUpdatedEvent,
    'transfer.paid': ITransferPaidEvent,
    'transfer.failed': ITransferFailedEvent,
    'ping': IPingEvent,
}


class StripeWebhooksView(BrowserView):

    # These events will not be verified by an API callback
    unverified = ['ping']

    def render(self):
        event_json = json.loads(self.request.get('BODY'))
        stripe_util = getUtility(IStripeUtility)

        mode = 'live'
        if event_json['livemode'] == False:
            mode = 'test'
        stripe_api = stripe_util.get_stripe_api(mode=mode)

        # Make sure we have a mapping for the event
        event_class = EVENTS_MAP[event_json['type']]

        # Fetch the event to verify authenticity, unless it is in the unverified list
        if event_json['type'] in self.unverified:
            data = event_json
        else:
            data = stripe_api.Event.retrieve(event_json['id'])

            # Verify that the id, type, and created date of the event match
            if data['id'] != event_json['id']:
                raise ValueError('Event id failed verification')
            if data['type'] != event_json['type']:
                raise ValueError('Event type failed verification')
            if data['created'] != event_json['created']:
                raise ValueError('Event creation date failed verification')

        # Send the event with data
        event = event_class(data)
        notify(event)

        return 'OK'
