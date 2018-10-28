from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="lenuga-sub",
    version="0.2.11",
    description="Download yify subtitle using only one command and compare the subtitles with lengua.",
    license="MIT",
    author="Yonimdo",
    install_requires=[
        'html2text==2014.12.29',
        'requests==2.5.1',
        'click==7.0',
    ],
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'lengua=yify:lengua'
        ]
    },
)
