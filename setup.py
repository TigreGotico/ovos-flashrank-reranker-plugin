#!/usr/bin/env python3
import os

from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))

with open(f"{BASEDIR}/README.md", "r") as fh:
    long_desc = fh.read()


def get_version():
    """ Find the version of the package"""
    version_file = os.path.join(BASEDIR, 'ovos_flashrank_solver', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


PLUGIN_ENTRY_POINT = [
    'ovos-flashrank-reranker-plugin=ovos_flashrank_solver:FlashRankMultipleChoiceSolver'
]
EVIDENCE_ENTRY_POINT = 'ovos-evidence-solver-flashrank=ovos_flashrank_solver:BM25SolverPlugin'
SUMMARIZER_ENTRY_POINT = (
    'ovos-summarizer-solver-flashrank=ovos_flashrank_solver:FlashRankSummarizer'
)

setup(
    name='ovos-flashrank-reranker-plugin',
    version=get_version(),
    description='A question solver plugin for OVOS',
    url='https://github.com/TigreGotico/ovos-flashrank-reranker-plugin',
    author='jarbasai',
    author_email='jarbasai@mailfence.com',
    license='MIT',
    packages=['ovos_flashrank_solver'],
    zip_safe=True,
    keywords='OVOS openvoiceos plugin utterance fallback query',
    entry_points={
        "opm.solver.reading_comprehension": EVIDENCE_ENTRY_POINT,
        'opm.solver.summarization': SUMMARIZER_ENTRY_POINT,
        "opm.solver.multiple_choice": PLUGIN_ENTRY_POINT},
    install_requires=required("requirements.txt"),
    long_description=long_desc,
    long_description_content_type='text/markdown'
)
