# -*- coding: utf-8 -*-
"""
This module contains the tool of quintagroup.seoptimizer
"""
import os
from setuptools import setup, find_packages

version = '4.2.0'

setup(name='quintagroup.seoptimizer',
      version=version,
      description="Quintagroup Search Engine Optimization Tool",
      long_description=open("README.txt").read() + "\n" +
      open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
      open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.2",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: GNU General Public License (GPL)",
      ],
      keywords='web zope plone seo search optimization',
      author='Myroslav Opyr, Volodymyr Romaniuk, Mykola Kharechko, '
             'Vitaliy Podoba, Volodymyr Cherepanyak, Taras Melnychuk, '
             'Vitaliy Stepanov, Andriy Mylenkyy',
      author_email='support@quintagroup.com',
      url='http://quintagroup.com/services/'
          'plone-development/products/qSEOptimizer/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.browserlayer',
          'quintagroup.canonicalpath>=0.6',
          'collective.monkeypatcher',
          #'Plone >= 4.0a',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
