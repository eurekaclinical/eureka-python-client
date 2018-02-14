from setuptools import setup, find_packages

setup(description='Eureka! Clinical Python Client',
      author='The Eureka Clinical team',
      url='http://eurekaclinical.org',
      download_url='Where to download it.',
      author_email='help@eurekaclinical.org',
      version='1.0.1.a1',
      license='Apache License 2.0',
      install_requires=['requests'],
      #python_requires='>= 2.7.10',
      packages=find_packages(),
      name='eurekaclinical',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.7'
          'License :: OSI Approved :: Apache Software License'
          'Programming Language :: Python :: Implementation :: CPython'
      ]
)
