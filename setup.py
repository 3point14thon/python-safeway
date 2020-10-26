import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
        name='python-safeway',
        version='0.0.0',
        author='3point14thon',
        author_email='chris.alan.bowers@gmail.com',
        description='a safeway.com python API',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/3point14thon/python-safeway',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Topic :: Utilities'
        ],
        python_requires='>=3.6',
)
