from collective.stripe.interfaces import IStripeEnabledView
from collective.stripe.interfaces import IStripeModeChooser
from collective.stripe.utils import get_settings
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.interfaces import IHtmlHead
from zope.interface import Interface


STRIPE_JS_HTML = """
    <script type="text/javascript" src="https://js.stripe.com/v1/"></script>
    <script type="text/javascript">
        (function ($) {
            $(document).ready(function() {
                Stripe.setPublishableKey('%s');
            });
        })(jQuery);
    </script>
"""


class StripeJs(ViewletBase):
    """ Inject the Stripe.js script tag and configuration if relevant"""

    def render(self):
        # Only run on views marked with IStripeEnabledView
        if not IStripeEnabledView.providedBy(self.view):
            return ""

        key = self.get_key()
        return STRIPE_JS_HTML % key

    def get_key(self):
        settings = get_settings()

        if IStripeModeChooser.providedBy(self.context):
            mode = self.context.get_stripe_mode()
        else:
            mode = settings.mode

        if mode == 'live':
            return settings.live_publishable_key

        if mode == 'test':
            return settings.test_publishable_key
