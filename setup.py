from distutils.core import setup
import sys

setup(
    name='BukGet',
    version='0.2.2',
    description='DBO Parser and web API for Minecraft Plugins',
    author='Steven McGrath',
    author_email='steve@chigeek.com',
    url='https://github.com/SteveMcGrath/bukget',
    packages=['bukget', 'bukget.parsers'],
    entry_points = {
        'console_scripts': [
            'bukget-web = bukget.svc:website',
            'bukget-updater = bukget.svc:updater',
            ]
    },
    data_files=[
        ('/etc', ['bukget.conf']),
    ],
    install_requires=[
        'bottle', 
        'markdown >= 2.0',
        'sqlalchemy',
        'bottle-sqlalchemy',
        'beautifulsoup',
        'pyyaml',
        'bleach',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)