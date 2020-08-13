from pathlib import Path

from pybuilder.cli import main
from pybuilder.core import use_plugin, init, Author

version = '1.0.0'
url = 'https://github.com/svaningelgem/required_files'
license = 'MIT'
authors = [Author("Steven 'KaReL' Van Ingelgem", 'steven@vaningelgem.be')]
install_requires = Path('requirements.txt').read_text().split('\n')
description = 'Simple but effective checking if required externals are present.'
python_requires = '>=3'


use_plugin('python.core')
use_plugin('python.unittest')
use_plugin('python.install_dependencies')
use_plugin('python.flake8')
use_plugin('python.coverage')
use_plugin('python.distutils')


name = 'required_files'
default_task = ['coverage', 'run_unit_tests']


@init
def set_properties(project):
    project.depends_on_requirements('requirements.txt')
    project.build_depends_on_requirements('requirements-dev.txt')

    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_include_scripts', True)

    project.set_property('distutils_setup_keywords', ['required files', 'github', 'bitbucket', 'zip',])

    project.set_property('distutils_readme_description', True)

    project.set_property(
        'distutils_classifiers',
        [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
    )


if __name__ == '__main__':
    main('-CX')
