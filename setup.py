import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as rq:
    install_requires = rq.read()

setuptools.setup(
    name="iwspp",
    version="1.0.1",
    scripts=["bin/iwspp"],
    author="Chinedu A. Anene",
    author_email="caanenedr@outlook.com",
    description="Preprocessing workflow for pathology slides",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caanene1/iwspp",
    packages=setuptools.find_packages(include=["iwspp", "iwspp.flows", "iwspp.Normalize"]),
    include_package_data=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=install_requires,
    python_requires='>=3.7',
)

# Build this package with >> python3 setup.py sdist bdist_wheel
