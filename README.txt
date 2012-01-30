Introduction
============

Quintagroup Search Engine Optimization Tool (quintagroup.seoptimizer)
was created to enhance SE visibility of Plone sites.

.. figure:: http://quintagroup.com/services/plone-development/products/qSEOptimizer/plone-seo.png

quintagroup.seoptimizer allows per document editing of:

* HTML Title tag
* META description tag
* META keywords tag
* HTML comment into page header
* META robots tag
* META Disposition tag
* Canonical URl http://projects.quintagroup.com/products/wiki/qSEOptimizer#CanonicalURL

For Title, description keywords and comment you have statistics (total/stop/used words, field length counter).

IMPORTANT
---------

**Starting from 3.0 release - quintagroup.seoptimizer package does not need 'overrides.zcml' file. So please remove 'quintagroup.seoptimizer-overrides' line from your buildout's ZCML area.**
  
Usage
-----

* Go to Plone Control Panel, enable Plone SEO for desired content types

* Go to a document (Blog entry, news item, event, etc)

* Switch to *SEO Properties* tab

* Select *Override* checkboxes of features you want to override

* Type-in your SEO values

* Save changes

* Do this for all documents that need enhanced SEO properties


Requirements
------------

* Plone 3.x, Plone 4.x

quintagroup.seoptimizer requires plone.browserlayer package to be installed in your site. plone.browserlayer package is shipped with Plone >= 3.1 and thus you don't need anything extra when you have that version of Plone.

But for Plone 3.0.x < 3.1 the process looks like this:

    * if you are creating a new Plone site and want it to support Quintagroup Search Engine Optimization Tool, just select 2 extension profiles Local browser layer support and quintagroup.seoptimizer profile in 'Extension Profiles' when adding a new Plone site;
    * if you want to add quintagroup.seoptimizer to already-existing Plone site, you need to apply Local browser layer support extension profile and then quintagroup.seoptimizer profile. You can do it either in  portal_setup/Import or in portal_quickinstaller by simple installation procedure.

In Plone 3.1 you can simply install quintagroup.seoptimizer profile in portal_quickinstaller without need of prior installation of Local browser layer support (that is not available for installation anyway, since it is a part of core system).

IMPORTANT! For Plone 3.0.x you should use plone.browserlayer 1.0.rc3. Be sure to define the right version of plone.browserlayer in your buildout.cfg. For Plone 3.1.x just use the version you have.


Notes
-----

* For Plone 4 versions - use Plone SEO 4.0 release and up http://plone.org/products/plone-seo/releases/4.0. In your buildout.cfg file's egg section set product version::

   [buildout]
   ....
   eggs =
        ...
        quintagroup.seoptimizer >=4.0

* For Plone 3 versions - use the latest Plone SEO 3.x release http://plone.org/products/plone-seo/releases/3.0.5. In your buildout.cfg file's egg section set product version::

   [buildout]
   ....
   eggs =
        ...
        quintagroup.seoptimizer >3.0,<4.0


* For Plone 2.x versions - use Plone SEO 1.7.1  release http://plone.org/products/plone-seo/releases/1.7.1


Links
-----

Watch Plone SEO screencast http://quintagroup.com/cms/screencasts/plone-seo to learn how to install and set up Plone SEO on a buildout-based Plone instance for Plone 3.2 or above.


Authors
-------

* Myroslav Opyr
* Andriy Mylenkyy
* Volodymyr Cherepanyak
* Vitaliy Podoba
* Taras Melnychuk
* Mykola Kharechko
* Vitaliy Stepanov
* Volodymyr Romaniuk
* Volodymyr Maksymiv

Contributors
------------
 * Michael Krishtopa (Theo) testing bug reporting
 * Craig Russell
  
