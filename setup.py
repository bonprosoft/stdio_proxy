from setuptools import setup

__version__ = "0.1.2"

setup(
    name="stdio_proxy",
    version=__version__,
    description="Thread safe stdio proxy",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yuki Igarashi",
    author_email="me@bonprosoft.com",
    url="https://github.com/bonprosoft/stdio_proxy",
    license="MIT License",
    packages=["stdio_proxy"],
    tests_require=["pytest", "pytest-runner"],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["futures; python_version == '2.7'"],
    extras_require={"develop": ["typing; python_version == '2.7'"]},
    package_data={"stdio_proxy": ["py.typed"]},
)
