from setuptools import setup

setup(
    name="pyGFBot",

    packages=[
        'pyGFBot',
    ],
    version='2',
    install_requires=[
        'requests',
        'Pillow',
        'pywin32'
    ],
    description="Lords Mobile Bot",
    license="MIT",
    python_requires=">=3.6",
)