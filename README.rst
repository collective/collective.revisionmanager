.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide_addons.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
collective.revisionmanager
==============================================================================

.. image:: https://travis-ci.org/collective/collective.revisionmanager.svg?branch=master
    :target: https://travis-ci.org/collective/collective.revisionmanager

collective.revisionmanager is a Plone add-on that lets you manage Products.CMFEditions histories. It can be used with Plone 5.0 and Plone 4.3. You will need Products.CMFEditions version >= 2.2.16.

Features
--------

- Sorted listing of histories storage (portal_historiesstorage) contents. Sort by: history id, number of versions, history size, size state, portal type or path
- Purge revisions or delete entire histories
- Maintain a cache for the statistics
- Plone controlpanel interface for portal_purgepolicy

Translations
------------

So far only the settings page has been translated to german.

Installation
------------

Install collective.revisionmanager by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.revisionmanager


and then running ``bin/buildout``. During installation, ``collective.revisionmanager`` will check wether the ``cmf_uid`` catalog index is there - if not, the index will be added and indexed. Also, a cache for the statistics will be created and the statistics will be calculated initially. Both these steps may require a considerable amount of time depending on the number of objects and object revisions in your database.

**Dealing with catalog inconsistencies**

If the installation fails with an ``AttributeError`` in ``Products.ZCatalog.CatalogBrains``, your ``portal_catalog`` is inconsistent and you need to `rebuild <http://docs.plone.org/develop/plone/searching_and_indexing/catalog.html>`_ it. As a quick workaround, you can also simply clear (or even delete) the `cmf_uid` catalog index - `collective.revisionmanager` will rebuild it during installation. But be aware that your `portal_catalog` is still inconsistent and needs rebuilding.

Contribute
----------

- Issue Tracker: https://github.com/collective/collective.revisionmanager/issues
- Source Code: https://github.com/collective/collective.revisionmanager
- Documentation: tbd

License
-------

The project is licensed under the GPLv2.
