import re
from distutils.core import setup


with open('drone-python/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(
    name='drone-python',
    version=version,
    packages=['drone-python', ],
    license='Apache License Version 2.0',
    author="Hamed Zaghaghi",
    author_email="hamed.zaghaghi@gmail.com",
    description="Drone CI/CD HTTP API Client",
    long_description=open('README').read(),
    keywords="drone ci cd http api",
    url="https://github.com/zaghaghi/drone-python",
    package_data={'': ['LICENSE', 'README']},
    classifiers=[
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
