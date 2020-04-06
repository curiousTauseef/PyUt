"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['src/Pyut.py']
DATA_FILES = ['loggingConfiguration.json']
OPTIONS = {}

setup(
    app=APP,
    data_files=DATA_FILES,
    packages=['org.pyut', 'org.pyut.commands', 'org.pyut.dialogs', 'org.pyut.enums', 'org.pyut.errorcontroller',
              'org.pyut.experimental', 'org.pyut.general', 'org.pyut.general.exceptions', 'org.pyut.history',
              'org.pyut.MiniOgl', 'org.pyut.ogl', 'org.pyut.ogl.sd',
              'org.pyut.persistence',
              'org.pyut.plugins', 'org.pyut.plugins.common', 'org.pyut.plugins.dtd', 'org.pyut.plugins.sugiyama', 'org.pyut.plugins.xsd',
              'org.pyut.resources', 'org.pyut.resources.img',
              'org.pyut.ui', 'org.pyut.ui.tools'
              ],
    include_package_data=True,
    package_dir={'': 'src'},
    package_data={
        'org.pyut.resources': ['Help.txt', 'Kilroy-Pyut.txt', 'Kudos.txt'],
    },
    url='https://github.com/hasii2011/PyUt',
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    description='The Python UML Tool',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['wxPython', 'xmlschema', 'html-testRunner', 'tulip-python', 'pygmlparser']
)
