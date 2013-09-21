from setuptools import setup


setup(name='werewolf',
      version='0.1',
      description='Jinro backend and CLI',
      packages = ['werewolf'],
      license='MIT',
      author='Junya Hayashi',
      install_requires=[
          "Twisted>=13.1.0",
          "Django>=1.6b4",
          "django-extensions",
          "Flask",
          "google-api-python-client",
          "pyOpenSSL",
          "mysql-python",
          "PIL",
          "PyYAML",
      ],
      dependency_links=[
          "https://github.com/django/django/archive/1.6b4.zip#egg=Django-1.6b4",
      ]
)
