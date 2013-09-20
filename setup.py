from setuptools import setup


setup(name='werewolf',
      version='0.1',
      description='Jinro backend and CLI',
      packages = ['werewolf'],
      license='MIT',
      author='Junya Hayashi',
      install_requires=[
          "Twisted>=13.1.0",
          "Django>=1.5.4",
          "Flask",
          "google-api-python-client",
          "pyOpenSSL",
      ]
)
