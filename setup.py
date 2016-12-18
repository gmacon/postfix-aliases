from setuptools import setup, find_packages


with open('requirements.in', 'r') as req_file:
      requirements = [l.strip() for l in req_file]


setup(name='postfix_aliases',
      version='0.1',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requirements)
