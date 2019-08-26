from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='pyggi',
    version='1.1',
    description='Python General Framework for Genetic Improvement',
    long_description=readme(),
    classifiers=[],
    keywords='GI SE',
    url='',
    author='Coinse',
    author_email='',
    license='MIT',
    packages=find_packages(),
    install_requires=['argparse', 'astor'],
    dependency_links=[],
    zip_safe=False)
