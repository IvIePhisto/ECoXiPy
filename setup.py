from setuptools import setup, find_packages
import sys, os

version = '0.3.0'

setup(name='ECoXiPy',
      version=version,
      description="Easy Creation of XML in Python",
      long_description="""\
      This Python 2 and 3 project (tested with CPython 2.7 and 3.3 as well as
      PyPy 2.0) allows for easy creation of XML. The hierarchical structure of
      XML is easy to spot and the code to create XML is much shorter than
      using SAX, DOM or similar APIs.
      """,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
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
          'TinkerPy>=0.2.1'
      ],
      test_suite='tests.test_suite'
)
