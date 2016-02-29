# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.revisionmanager


class CollectiveRevisionmanagerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

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


COLLECTIVE_REVISIONMANAGER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_REVISIONMANAGER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveRevisionmanagerLayer:AcceptanceTesting'
)
