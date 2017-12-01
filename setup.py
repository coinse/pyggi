from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='pyggi',
    version='0.1',
    description='Python General Framework for Genetic Improvement',
    long_description=readme(),
    classifiers=[],
    keywords='GI SE',
    url='',
    author='Coinse',
    author_email='',
    license='MIT',
    packages=['pyggi'],
    install_requires=[],
    dependency_links=[],
    zip_safe=False)
