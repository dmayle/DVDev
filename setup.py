#   DVDev - Distributed Versioned Development - tools for Open Source Software
#   Copyright (C) 2009  Douglas Mayle

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='DVDev',
    version='0.1.2',
    description='',
    author='Douglas Mayle',
    author_email='douglas@mayle.org',
    license='GNU Affero General Public License v3',
    url='http://dvdev.org',
    install_requires=[
        "Pylons>=0.9.7",
        "Genshi>=0.4",
        "Pygments",
        "repoze.who",
        "repoze.who.plugins.openid",
        "docutils",
        "yamltrak",
        "Meritocracy",
        "filesafe",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'dvdev': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'dvdev': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
        [paste.app_factory]
        main = dvdev.config.middleware:make_app

        [paste.app_install]
        main = pylons.util:PylonsInstaller

        [console_scripts]
        dvdev=dvdev.commands:main
    """,
    classifiers=['License :: OSI Approved :: GNU Affero General Public License v3'
    ]
)
