from setuptools import setup, find_packages
from homo.lab.__main__ import version

with open('README.md') as f:
    long_description = f.read()

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
    install_requires=['blinker==1.6.2',
                      'bottle==0.12.25',
                      'certifi>=2023.07.22',
                      'cffi==1.15.1',
                      'charset-normalizer==3.2.0',
                      'click==8.1.4',
                      'clr-loader==0.2.5',
                      'colorama==0.4.6',
                      'dominate==2.8.0',
                      'Flask==2.3.2',
                      'idna==3.4',
                      'itsdangerous==2.1.2',
                      'Jinja2==3.1.2',
                      'MarkupSafe==2.1.3',
                      'proxy-tools==0.1.0',
                      'pycparser==2.21',
                      'pythonnet==3.0.1',
                      'pywebview==4.2.2',
                      'requests==2.31.0',
                      'typing_extensions==4.7.1',
                      'ua-parser==0.18.0',
                      'urllib3==2.0.3',
                      'user-agents==2.2.0',
                      'Werkzeug==2.3.6']
)
