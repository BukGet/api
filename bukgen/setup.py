from distutils.core import setup
import sys

setup(
    name='BukGen',
    version='0.1.1',
    description='BukGet Parsing Engines',
    author='Steven McGrath',
    author_email='steve@chigeek.com',
    url='https://github.com/BukGet/bukget',
    packages=['bukgen'],
    entry_points = {
        'console_scripts': [
            'bukgen_bukkit = bukgen.bukkit:run',
            'bukgen_manual = bukgen.manual:manual_update',
            ]
    },
    data_files=[
        ('/etc/bukget', ['bukgen.conf']),
    ],
    install_requires=[
        'pymongo',
        'beautifulsoup',
        'PyYAML',
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