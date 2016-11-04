# -*- coding: utf-8 -*-
"""Installer for the collective.revisionmanager package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read() +
    '\n' +
    'Contributors\n' +
    '============\n' +
    '\n' +
    open('CONTRIBUTORS.rst').read() +
    '\n' +
    open('CHANGES.rst').read() +
    '\n')


setup(
    name='collective.revisionmanager',
    version='0.6',
    description="Manage CMFEditions Histories",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='tschorr',
    author_email='t_schorr@gmx.de',
    url='https://pypi.python.org/pypi/collective.revisionmanager',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'AccessControl',
        'Acquisition',
        'plone.api',
        'plone.autoform',
        'plone.batching',
        'plone.protect',
        'Products.CMFEditions>=2.2.16',
        'Products.CMFPlone>=4.3',
        'Products.CMFQuickInstallerTool>=3.0.9',  # use uninstall profile
        'Products.CMFUid',
        'Products.GenericSetup',
        'setuptools',
        'transaction',
        'z3c.form',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
    ],
    extras_require={
        'test': [
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
            'plone.app.testing',
            'plone.browserlayer',
            'plone.testing',
            'robotsuite',
            'testfixtures',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
