import setuptools
from setuptools import setup

setup(
    name='birdcall',
    version='1.0.6',
    packages=setuptools.find_packages(),
    url='https://github.com/lukehollenback/birdcall',
    license='Apache License 2.0',
    author='Luke Hollenback',
    author_email='luke.hollenback+birdcall@gmail.com',
    description='Module for serverless Twitter bots.',
    install_requires=['python-dotenv', 'tweepy'],
    python_requires='>=3.8'
)
