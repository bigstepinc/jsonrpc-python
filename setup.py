from distutils.core import setup

version = '0.2'
name = 'jsonrpc2base'

setup(
    name=name,
    packages=[name],
    version=version,
    description='JSONRPC 2.0 client over HTTP',
    author='Bigstep inc',
    author_email='adrian.ciausu@bigstep.com',
    url='https://github.com/bigstepinc/jsonrpc-python',
    download_url='https://github.com/bigstepinc/jsonrpc-python/tarball/' + version,
    keywords=['jsonrpc2', 'client', 'server', 'base'],
    classifiers=[],
)
