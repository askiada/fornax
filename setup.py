from setuptools import setup, find_packages
exec(open("./fornax/version.py").read())

with open('README.md') as fp:
    long_description = fp.read()

setup(
    name='fornax',
    version=__version__,
    license='Apache License 2.0',
    author='Daniel Staff',
    description='Approximate fuzzy subgraph matching in polynomial time',
    install_requires=[
        'psycopg2>=2.7.4',
        'SQLAlchemy>=1.2.8',
        'numpy>-1.14.5'
    ],
    author_email='daniel.staff@digicatapult.org.uk',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ]
)
