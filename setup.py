#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))


def read(filename):
    """Get the long description from a file."""
    fname = os.path.join(here, filename)
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


test_deps = ['pytest']
install_deps = ['boto3', 'click']


setup(
    name='r53up',
    version='0.0.1',
    description='Dynamic DNS updates for Amazon Route 53',
    long_description=read('README.md'),
    author='Ben Ransford',
    author_email='ben@ransford.org',
    url='https://github.com/ransford/r53up',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='route53 dynamic dns',
    packages=find_packages(),
    install_requires=install_deps,
    tests_require=test_deps,
    extras_require={'test': test_deps},
    setup_requires=['pytest-runner'],
    entry_points={
        'console_scripts': [
            'r53up=r53up.r53up:main',
        ],
    },
)
