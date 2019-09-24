from collective.stripe.testing import FUNCTIONAL_TESTING
from collective.stripe.utils import get_settings
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

import transaction
import unittest


class ControlPanelFunctionalTest(unittest.TestCase):
    # The layer's setup will run once before all of these tests run,
    # and its teardown will run once after all these tests run.
    layer = FUNCTIONAL_TESTING

    # setUp is run once before *each* of these tests.
    # This stuff can be moved to the layer's setupPloneSite if you want
    # it for all tests using the layer, not just this test class.
    def setUp(self):
        self.layer['portal'].validate_email = False
        portal = self.layer['portal']

        transaction.commit()

    # tearDown is run once after *each* of these tests.
    def tearDown(self):
        pass

    def test_controlpanel(self):
        portal = self.layer['portal']

        # Now as an admin user, go through the steps in the browser
        browser = Browser(portal)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))
        browser.open('http://nohost/plone/plone_control_panel')

        settings_link = browser.getLink('Stripe Payment Processing')
        settings_link.click()
        self.assertEqual('http://nohost/plone/@@stripe-settings', browser.url)

        # Set the values in the control panel
        browser.getControl(name='form.widgets.mode:list').value = ["test",]
        browser.getControl(name='form.widgets.live_secret_key').value = "1234567890"
        browser.getControl(name='form.widgets.live_publishable_key').value = "9876543210"
        browser.getControl(name='form.widgets.test_secret_key').value = "qwertyuiop"
        browser.getControl(name='form.widgets.test_publishable_key').value = "poiuytrewq"
        browser.getControl(name='form.buttons.save').click()

        # Check that the settings were changed in the registry
        settings = get_settings()
        self.assertEqual(settings.mode, "test")
        self.assertEqual(settings.live_secret_key, "1234567890")
        self.assertEqual(settings.live_publishable_key, "9876543210")
        self.assertEqual(settings.test_secret_key, "qwertyuiop")
        self.assertEqual(settings.test_publishable_key, "poiuytrewq")
