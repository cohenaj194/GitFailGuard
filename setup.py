from setuptools import setup, find_packages

setup(
    name='GitFailGuard',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'Flask',
        'requests',
        'openai'
    ],
    entry_points={
        'console_scripts': [
            'gitfailguard=main:app.run'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
