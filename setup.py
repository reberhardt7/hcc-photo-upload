import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'python-magic',
    'google-api-python-client',
    ]

setup(name='hcc-photo-upload',
      version='0.0',
      description='hcc-photo-upload',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='hccphotoupload',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = hccphotoupload:main
      [console_scripts]
      initialize_hcc-photo-upload_db = hccphotoupload.scripts.initializedb:main
      hcc-upload-gdrive = hccphotoupload.scripts.gdrive_upload:main
      """,
      )
