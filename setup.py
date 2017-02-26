# -*- coding: utf-8 -*-

#  Copyright 2017 Aaron M. Hosford
# See LICENSE.txt for licensing information.

import os

from setuptools import setup, find_packages


def get_long_description():
    rst_path = os.path.join(os.path.dirname(__file__), 'README.rst')
    md_path = os.path.join(os.path.dirname(__file__), 'README.md')

    try:
        # Imported here to avoid creating a dependency in the setup.py
        # if the .rst file already exists.
        from pypandoc.pandoc_download import download_pandoc
        download_pandoc()
        from pypandoc import convert_file
    except ImportError:
        pass
    else:
        # pandoc, you rock...
        rst_content = convert_file(md_path, 'rst')
        with open(rst_path, 'w') as rst_file:
            rst_file.write(rst_content)

    if os.path.isfile(rst_path):
        with open(rst_path) as rst_file:
            return rst_file.read()
    else:
        # It will be messy, but it's better than nothing...
        with open(md_path) as md_file:
            return md_file.read()


setup(
    name='vert',
    version='0.0.1',
    packages=find_packages(),
    package_data={
        '': ['*.txt', '*.md', '*.rst']
    },
    include_package_data=True,
    url='https://pypi.python.org/pypi/vert',
    license='MIT',
    author='Aaron Hosford',
    author_email='hosford42@gmail.com',
    description='Graphs for Python',
    long_description=get_long_description(),
    keywords='graph vertex edge node link network semantic database',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database :: Front-Ends',  # Graph databases, in particular
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Scientific/Engineering :: Mathematics',
    ]
)
