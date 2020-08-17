# -*- coding: utf-8 -*-
import collective.revisionmanager
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import (FunctionalTesting, IntegrationTesting,
                               PloneSandboxLayer, applyProfile)
from plone.testing import z2


class CollectiveRevisionmanagerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.revisionmanager)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.revisionmanager:default')


COLLECTIVE_REVISIONMANAGER_FIXTURE = CollectiveRevisionmanagerLayer()


COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_REVISIONMANAGER_FIXTURE,),
    name='CollectiveRevisionmanagerLayer:IntegrationTesting'
)


COLLECTIVE_REVISIONMANAGER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_REVISIONMANAGER_FIXTURE,),
    name='CollectiveRevisionmanagerLayer:FunctionalTesting'
)
