from setuptools import setup, find_packages

setup(
    name='aula-f87pro-cli',
    version='0.1.0',
    author='Ahorts',
    author_email='godswayahorts@gmail.com',
    description='CLI tool for controlling RGB of Aula F87 Pro keyboard',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'hidapi', 
    ],
    entry_points={
        'console_scripts': [
            'aula-f87pro-cli=aula_f87pro.cli:main',  # Fixed import path
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Linux',
    ],
    python_requires='>=3.9', 
)