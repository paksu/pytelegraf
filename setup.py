from setuptools import find_packages, setup

setup(
    name='pygraf',
    version='0.1.0',
    description='Telegraf client',
    author='paksu',
    url='https://github.com/paksu/pygraf',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    test_suite='telegraf.tests',
    classifiers=[
        'foo'
    ],
)
