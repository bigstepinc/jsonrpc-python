from distutils.core import setup
from setuptools import find_packages

version = '0.11'
name = 'jsonrpc2-base'

setup(
    name=name,
    packages=find_packages(),
    version=version,
    description='JSONRPC 2.0 client over HTTP',
    author='Bigstep inc',
    author_email='adrian.ciausu@bigstep.com',
    url='https://github.com/bigstepinc/jsonrpc-python',
    download_url='https://github.com/bigstepinc/jsonrpc-python/tarball/' + version,
    keywords=['jsonrpc2', 'client', 'server', 'base'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
