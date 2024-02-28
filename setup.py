from setuptools import setup, find_packages

setup(
    name='stemplot',
    version='0.1.0',
    author='Jiadong Dan',
    author_email='jiadong.dan@u.nus.edu',
    description='A Python library for scientific plot',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jiadongdan/stemplot',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.18.0',
        'matplotlib>=3.1.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    python_requires='>=3.6',
    keywords='stemplot, visualization, STEM, microscopy',
)
