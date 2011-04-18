import unittest
import doctest

from base import *


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.FunctionalDocFileSuite(
            'seo_migration.txt', package='quintagroup.seoptimizer.tests',
            test_class=FunctionalTestCaseNotInstalled, globs=globals(),
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ztc.FunctionalDocFileSuite(
            'seo_properties.txt', package='quintagroup.seoptimizer.tests',
            test_class=FunctionalTestCase, globs=globals(),
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
