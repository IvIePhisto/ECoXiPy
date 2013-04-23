from setuptools import setup, find_packages
import sys, os

version = '0.2.0'

setup(name='ECoXiPy',
      version=version,
      description="Easy Creation of XML in Python",
      long_description="""\
This Python project allows for easy creation of XML. The hierarchical
structure of XML is easy to spot and the code to create XML is much shorter
than using SAX, DOM or similar APIs.
""",
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing :: Markup :: XML',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='XML',
      author='Michael Pohl',
      author_email='pohl-michael@gmx.biz',
      url='https://github.com/IvIePhisto/ECoXiPy',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'doc', 'tests']),
      include_package_data=False,
      zip_safe=True,
      install_requires=[
          'TinkerPy'
      ],
      test_suite='tests.test_suite'
)
