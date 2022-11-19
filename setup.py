import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pushto',
    version='1.1.1',
    author='PToale',
    author_email='ptoale@gmail.com',
    description='Push-to telescope',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mike-huls/toolbox',
    project_urls = {
        "Bug Tracker": "https://github.com/mike-huls/toolbox/issues"
    },
    license='MIT',
    packages=['pushto'],
    install_requires=['astropy', 'numpy', 'requests', 'serial', 'zmq'],
)
