import os
from setuptools import setup

def read(fname):
    return open(
        os.path.join(os.path.dirname(__file__), fname)
    ).read()

setup(
    name = "models",
    version = "0.0.1",
    author = "Arush Goyal",
    author_email = "arushgyl@gmail.com",
    description = ("Models for complaintResolution"),
    license = "BSD",
    keywords = "model complaintResolution",
    packages=['models', 'tests'],
    long_description=read('Readme.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)