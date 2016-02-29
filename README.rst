.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide_addons.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
collective.revisionmanager
==============================================================================

collective.revisionmanager is a Plone Add-On that lets you manage Products.CMFEditions histories.

Features
--------

- Sorted listing of histories storage (portal_historiesstorage) contents. Sort by: history id, number of versions, history size, size state, portal type or path
- Purge revisions or delete entire histories
- Maintain a cache for the statistics
- Plone controlpanel interface for portal_purgepolicy

Translations
------------

This product has not yet been translated.

Installation
------------

Install collective.revisionmanager by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.revisionmanager


and then running ``bin/buildout``

Contribute
----------

- Issue Tracker: https://github.com/collective/collective.revisionmanager/issues
- Source Code: https://github.com/collective/collective.revisionmanager
- Documentation: tbd

License
-------

The project is licensed under the GPLv2.
