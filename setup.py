from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

setup(name='werewolf',
      version='0.1',
      description='Jinro backend and CLI',
      packages=['werewolf'],
      license='MIT',
      author='Junya Hayashi',
      install_requires=[
          "tornado",
          "Django>=1.6",
          "django-extensions",
          "Flask",
          "google-api-python-client",
          "pyOpenSSL",
          "mysql-python",
          "PIL",
          "PyYAML",
      ],
      tests_require=["pytest"],
      cmdclass = {'test': PyTest},
)
