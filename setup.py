from setuptools import find_packages, setup

setup(
    name='painterbot',
    packages=find_packages(where="src"),
    use_scm_version={"write_to": "src/painter/_version.py"},
    url='',
    license='Apache-2.0',
    author='Marcelo Duarte Trevisani',
    author_email='marceloduartetrevisani@gmail.com',
    description='Bot example',
    python_requires=">=3.7",
    install_requires=["gidgethub", "cachetools", "aiohttp"],
    setup_requires=["setuptools_scm"],
    extras_require={"testing": ["pytest", "mock", "pytest-cov"]},
)
