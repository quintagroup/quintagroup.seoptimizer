Quintagroup Search Engine Optimization Tool
===========================================

This product was created to enhance SE visibility of Plone sites.


Features
--------

quintagroup.seoptimizer allows per document editing of:

* HTML Title tag

* META description tag

* META keywords tag

* HTML comment into page header

* META robots tag

* META Disposition tag

* Canonical URl (http://projects.quintagroup.com/products/wiki/qSEOptimizer#CanonicalURL

For Title, description keywords and comment you have statistics
(total/stop/used words, field length counter).
  
  
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

* Plone 3.x, Plone 4.0

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

Watch Plone SEO screencast (http://quintagroup.com/cms/screencasts/plone-seo) to learn how to install and set up Plone SEO on a buildout-based Plone instance for Plone 3.2 or above.


Authors
-------

* Myroslav Opyr

* Volodymyr Romaniuk

* Mykola Kharechko

* Vitaliy Podoba

* Volodymyr Cherepanyak

* Taras Melnychuk

* Vitaliy Stepanov

* Andriy Mylenkyy


