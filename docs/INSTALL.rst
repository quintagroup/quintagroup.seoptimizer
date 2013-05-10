Installation
============

Buildout
--------

If you are using zc.buildout and the plone.recipe.zope2instance recipe to manage your project:

* Add ``quintagroup.seoptimizer`` to the list of eggs to install, e.g.:

  For Plone 4.x - in your buildout.cfg file write::

   [buildout]
   ....
   eggs =
        ...
        quintagroup.seoptimizer >=4.0


  For Plone 3 - in your buildout.cfg file write::

   [buildout]
   ....
   eggs =
        ...
        quintagroup.seoptimizer >3.0,<4.0


* Tell the plone.recipe.zope2instance recipe to install a ZCML slug::

   [instance]
   ...
   zcml =
       quintagroup.seoptimizer

* Re-run buildout, e.g. with::

   $ ./bin/buildout

* Restart the Zope server, e.g with the following command in the terminal::

   $ ./bin/instance restart


Install quintagroup.seoptimizer via ZMI portal_setup  -> *Import* tab. Select ``quintagroup.seoptimizer`` from the list of available profiles and press *Import all steps*.

Uninstallation
==============

To uninstall quintagroup.seoptimizer - go to ZMI portal_setup  -> *Import* tab. Select ``quintagroup.seoptimizer uninstall`` profile from the list of available profiles and press *Import all steps*.

Package Upgrade / Reinstall
===========================

In case you want to upgrate quintagroup.seoptimizer to a newer version in your buildout:

* Remove ``quintagroup.seoptimizer-overrides`` from ``buildout.cfg`` file's ZCML area if it is there (starting from 3.0 release - quintagroup.seoptimizer package does not use overrides.zcml file any longer)

* Upgrade quintagroup.seoptimizer to the newer version using buildout (rerun the buildout to replace old package with a new one in your instance)

* Run the reinstall procedure: visit "Site Setup" -> "Add-ons" control panel in your Plone site, where you have to press quintagroup.seoptimizer button next to Upgrade. (The same can be done with quickinstaller via ZMI: at /portal_quickinstaller/manage_installProductsForm: check the seoptimizer box and press Reinstall button.) This is an essential step as new version of product introduces new persistent settings and ways to migrate settings/content from old to new version. 

