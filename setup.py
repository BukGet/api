from distutils.core import setup
import sys

setup(
    name='BukGet',
    version='0.3',
    description='DBO Parser and web API for Minecraft Plugins',
    author='Steven McGrath',
    author_email='steve@chigeek.com',
    url='https://github.com/SteveMcGrath/bukget',
    packages=['bukget', 'bukget.parsers'],
    entry_points = {
        'console_scripts': [
            'bukget_api = bukget.api:start',
            'bukget_bukkit = bukget.parsers.bukkit:speedy',
            'bukget_bukkit-full = bukget.parsers.bukkit:full',
            'bukget_bukkit-status = bukget.parsers.bukkit:stage_update',
            ]
    },
    data_files=[
        ('/etc', ['bukget.conf']),
    ],
    install_requires=[
        'bottle', 
        'Markdown >= 2.0',
        'pymongo',
        'beautifulsoup',
        'PyYAML',
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