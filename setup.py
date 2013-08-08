from setuptools import setup


setup(name='unga',
      version='0.1',
      description='Twisted based messaging service',
      packages = ['unga'],
      license='MIT',
      author='Junya Hayashi',
      install_requires=[
          "Twisted>=13.1.0",
          "cql>=1.4.0",
      ]
)
