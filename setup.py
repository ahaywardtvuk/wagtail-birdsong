#!/usr/bin/env python
"""
Install wagtail-birdsong using setuptools
"""
from setuptools import find_namespace_packages, setup

with open('birdsong/version.py', 'r') as f:
    version = None
    exec(f.read())

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='wagtail-birdsong',
    version=version,
    description='Create and send email campaigns from Wagtail',
    long_description=readme,
    author='Neon Jungle',
    author_email='developers@neonjungle.studio',

    install_requires=[
        'wagtail>=2.15',
        'django-mjml',
    ],
    setup_requires=[
        'wheel',
        'setuptools==67.4.0'
    ],
    zip_safe=False,
    license='BSD License',

    packages=find_namespace_packages(include=['birdsong.*']),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
