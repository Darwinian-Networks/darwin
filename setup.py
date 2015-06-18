from distutils.core import setup

setup(
    name="darwin",
    version="0.1",
    description="A Python library for Bayesiannetwork modelling and exact inference",
    author="Jhonatan Oliveira",
    author_email="jhonatanoliveira@gmail.com",
    packages=['darwin', 'darwin.inference', 'darwin.modelling', 'darwin.utils'],
    url="www2.cs.uregina.ca/~desouzjh/"
)
