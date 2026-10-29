from setuptools import setup, find_packages

setup(
    name="uamc",
    version="1.0.0",
    description="Autonomous Vehicle Software Stack for UAMC at Techfest, IIT Bombay",
    author="Autonomous Mobility Lab",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "opencv-python>=4.8.0",
        "scipy>=1.10.0",
        "pyserial>=3.5",
    ],
    python_requires=">=3.8",
)
