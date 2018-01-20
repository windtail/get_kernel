# coding: utf-8


from setuptools import setup


setup(
    name="get_kernel",
    version="1.0",
    description="Get linux kernel by version number, such as 4.14.14",
    license="MIT",
    author="Luo Jiejun",
    author_email="6020100326ljj@163.com",
    install_requires=["click"],
    py_modules=["get_kernel"],
    url="https://github.com/windtail/get_kernel",
    entry_points={
        "console_scripts": [
            "get_kernel = get_kernel:cli"
        ]
    }
)
