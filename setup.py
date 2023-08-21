from setuptools import setup, find_packages
from homo.lab.__main__ import version

with open('README.md') as f:
    long_description = f.read()
with open('./requirements.txt') as f:
    requires = list(map(lambda string: string.strip(), f.readlines()))

setup(
    name='HoMoLab',
    version=version,
    description='基于Pywebview的米游社PC客户端实现',
    author='Error063',
    author_email='admin@error063.work',
    url='https://homolab.error063.work/',
    license='GPL3',
    keywords=['HoYoLab', '米游社'],
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=True,
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
        ],
    python_requires='~=3.10',
    entry_points={
        'console_scripts': [
            'homolab=homo.lab.__main__:enter'
        ]
    },
    package_dir={'homo.resources': 'resources', 'homo.theme': 'theme'},
    package_data={'homo.resources': ['homo/resources/*.*'], 'homo.theme': ['homo/theme/*.*']},
    install_requires=requires
)
