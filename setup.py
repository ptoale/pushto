import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pushto',
    version='1.1.1',
    author='ptoale',
    author_email='ptoale@gmail.com',
    description='Push-to telescope',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ptoale/pushto.git',
    project_urls = {
        "Bug Tracker": "https://github.com/ptoale/pushto/issues"
    },
    license='MIT',
    packages=['pushto'],
    scripts=['pushto/ui.py'],
    install_requires=['astropy', 'numpy', 'pyserial', 'requests', 'zmq'],
)
