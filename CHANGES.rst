Changelog
=========

0.8 (unreleased)
----------------

- Nothing changed yet.


0.7 (2016-11-29)
----------------

- Nothing changed yet.


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
