from setuptools import setup, find_packages

setup(
    name='crawler',
    version='0.1',
    author='Indrajith Indraprastham',
    author_email='indr4jith@gmail.com',
    description='A simple web crawler.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/indrajithi/tiny-web-crawler',
    packages=find_packages(),
    install_requires=[
        'validators',
        'beautifulsoup4',
        'lxml',
        'colorama'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'tiny-web-crawler=crawler.crawler:main',
        ],
    },
)
