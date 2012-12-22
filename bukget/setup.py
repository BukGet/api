from distutils.core import setup
import sys

setup(
    name='BukGet',
    version='1.0',
    description='BukGet JSON API for Minecraft Plugins',
    author='Steven McGrath',
    author_email='steve@chigeek.com',
    url='https://github.com/BukGet/bukget',
    packages=['bukget'],
    entry_points = {
        'console_scripts': [
            'bukget = bukget:start',
            ]
    },
    data_files=[
        ('/etc/bukget', ['bukget.conf']),
    ],
    install_requires=[
        'bottle', 
        'pymongo',
        'bleach',
        'paste',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)