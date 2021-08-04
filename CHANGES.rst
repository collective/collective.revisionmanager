Changelog
=========

1.0.1 (unreleased)
------------------

- Fixes a bug in Plone 5.2 ('RequestContainer' object has no attribute
  'translate')
  [pysailor]


1.0.0 (2020-08-18)
------------------

- Add support for Python 3.
  [pbauer,maurits,tschorr]


0.9 (2019-10-07)
----------------

- Fixed deleting orphans in Plone 5.1+ (CMFEditions 3).
  Fixes `issue #19 <https://github.com/collective/collective.revisionmanager/issues/19>`_.  [maurits]

- Fixed startup error by loading the CMFCore zcml.  [maurits]


0.8 (2017-08-31)
----------------

- Do not fail on ``BrokenModified`` while calculating storage statistics.
  [pbauer]

- UX-Improvements: Display size in a human-readable format, allow to increase the batch-size with a query-string, allow selecting all items.
  [pbauer]

- In addition to the overall number of revisions, also display the number of purged revisions (fixes `#14 <https://github.com/collective/collective.revisionmanager/issues/14>`_).
  [tschorr]

- Decrease log level for logging processing of each history (fixes `#15 <https://github.com/collective/collective.revisionmanager/issues/15>`_).
  [tschorr]

- Add script to rebuild i18n stuff and update translations.
  [hvelarde]


0.7 (2016-11-29)
----------------

- Do not fail on ``POSKeyError`` while calculating storage statistics (fixes `#9 <https://github.com/collective/collective.revisionmanager/issues/9>`_).
  [tschorr]

- Storage statistics calculation now works behind a proxy (fixes `#8 <https://github.com/collective/collective.revisionmanager/issues/8>`_).
  [tschorr]

- Fix a typo. This requires to run an update step (see `#10 <https://github.com/collective/collective.revisionmanager/issues/10>`_).
  [tschorr]


0.6 (2016-11-04)
----------------

- Add Brazilian Portuguese and Spanish translations.
  [hvelarde]

- Fix package uninstall.
  [hvelarde]

- Fix package dependencies.
  Remove needless dependency on z3c.jbot.
  [hvelarde]


0.5 (2016-04-29)
----------------

- do not calculate statistics during installation. This allows to
  configure subtransactions (and thereby memory consumption) before
  calculating statistics initially
- add more german translations
- more work on i18n
- fix KeyError when sorting by portal_type
- add button to delete all histories without working copy at once

0.4 (2016-04-19)
----------------

- introducing subtransactions to save memory
- more work on german translations

0.3 (2016-04-06)
----------------

- add some german translations
- handle POSKeyError when accessing inconsistent histories storage

0.2 (2016-03-02)
----------------

- revisions controlpanel now works in Plone 5
- Replace Update Statistics View by a button in controlpanel
- Travis testing for Plone 4.3.x and 5.0.x
- check for marker file in post install step

0.1 (2016-03-01)
----------------

- Initial release.
