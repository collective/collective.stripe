import transaction
import unittest
from zope.interface import Interface, implements
from zope.component import getSiteManager, getUtility
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from Products.Five.utilities.marker import mark
from collective.stripe.interfaces import IStripeModeChooser
from collective.stripe.utils import get_settings, IStripeUtility
from collective.stripe.testing import FUNCTIONAL_TESTING

class UtilsFunctionalTest(unittest.TestCase):
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

    def test_global_utility(self):
        portal = self.layer['portal']
        util = getUtility(IStripeUtility)
        self.assertEqual(util.__class__.__name__, 'StripeUtility')

    def test_mode(self):
        portal = self.layer['portal']
        util = getUtility(IStripeUtility)
        settings = get_settings()

        settings.mode = 'test'
        mode = util.get_mode_for_context(portal)
        self.assertEqual(mode, 'test')

        settings.mode = 'live'
        mode = util.get_mode_for_context(portal)
        self.assertEqual(mode, 'live')

        # Now mark with IStripeModeChooser and test overriding the mode by context
        mark(portal, IStripeModeChooser)

        portal.stripe_mode = 'test'
        portal.get_stripe_mode = lambda: 'test'
        mode = util.get_mode_for_context(portal)
        self.assertEqual(mode, 'test')

        settings.mode = 'test'
        portal.get_stripe_mode = lambda: 'live'
        mode = util.get_mode_for_context(portal)
        self.assertEqual(mode, 'live')
