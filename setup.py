from setuptools import setup

setup(
    name="stdio_proxy",
    version="0.0.1",
    description="Thread safe stdio proxy",
    long_description="",
    author="Yuki Igarashi",
    author_email="me@bonprosoft.com",
    url="https://github.com/bonprosoft/stdio_proxy",
    license="MIT License",
    packages=["stdio_proxy"],
    tests_require=["pytest", "pytest-runner"],
    test_suite="tests",
)
