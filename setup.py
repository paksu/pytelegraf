from setuptools import find_packages, setup

setup(
    name='pytelegraf',
    version='0.2.0',
    description='Telegraf client',
    author='paksu',
    url='https://github.com/paksu/pytelegraf',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    extras_require={
        'http': ['requests-futures==0.9.7']
    },
    test_suite='telegraf.tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
