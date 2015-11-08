from distutils.core import setup

setup(name='usace_public_notices',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='United States Army Corps of Engineers Public Notices',
      url='http://scott.dada.pink',
      packages=['usace_public_notices'],
      entry_points = {'console_scripts': ['usace-public-notices = usace_public_notices:cli']},
      install_requires = ['requests', 'vlermv>=1.3.0'],
      tests_require = ['pytest>=2.6.4'],
      version='0.2.1',
      license='AGPL',
)
