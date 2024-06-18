import setuptools

with open('./requirements.txt') as requirements_file:
    install_requires = requirements_file.readlines()

scripts = ['./crawler.py']

setuptools.setup(
    name='clevervol_test',
    version='0.1.0',
    python_requires='>=3.10',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    entry_points='''
    [console_scripts]
    crawler=crawler:crawler_cli

    ''',
    scripts=scripts
)
