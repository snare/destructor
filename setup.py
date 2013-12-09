from setuptools import setup

setup(
    name = "destructor",
    version = "0.1",
    author = "snare",
    author_email = "snare@ho.ax",
    description = ("The gismo from Pismo (Beach)"),
    license = "Buy snare a beer",
    keywords = "struct binary parsing",
    url = "https://github.com/snarez/destructor",
    packages=['destructor'],
    install_requires = ['pycparser'],
)
