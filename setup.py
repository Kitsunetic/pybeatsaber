from setuptools import find_packages, setup

setup(
    name="pybeatsaber",
    version="0.0.2",
    description="BeatSaber beatmap IO library written in pure python",
    author="Kitsunetic",
    author_email="jh.shim.gg@gmail.com",
    url="https://github.com/Kitsunetic/pybeatsaber.git",
    packages=find_packages(),
    install_requires=[],
    extras_require={},
    setup_requires=["Pillow"],
    tests_require=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3",
)
