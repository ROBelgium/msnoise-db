from setuptools import setup, find_packages
import os
import sys
import inspect


SETUP_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

UTIL_PATH = os.path.join(SETUP_DIRECTORY, "msnoise_db")
sys.path.insert(0, UTIL_PATH)

if UTIL_PATH:   # To avoid PEP8 E402
    from _version import get_git_version  # @UnresolvedImport

sys.path.pop(0)


setup(version=get_git_version(),
      name='msnoise_db',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'click'
      ],
      extras_require={ },
      entry_points='''
          [console_scripts]
          msnoisedb=msnoise_db.cli:run
      ''',
      author="Thomas Lecocq & MSNoise dev team",
      author_email="Thomas.Lecocq@seismology.be",
      description="The database module for MSNoise",
      license="EUPL-1.1",
      url="http://www.msnoise.org",
      keywords="noise monitoring seismic velocity change dvv dtt doublet"
               " stretching cross-correlation acoustics seismology",
      zip_safe=False,
      platforms='OS Independent',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics'],
      )
