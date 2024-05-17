#!/usr/bin/env python
"""Usage: clone_oca_dependencies [<checkout_dir> <build_dir>]

Arguments:

deps_checkout_dir: the directory in which the dependency repositories
will be cloned
build_dir: the directory in which the tested repositories have been cloned

If no arguments are provided, default to the layout used in the OCA travis
configuration.

The program will process the file oca_dependencies.txt at the root of the
tested repository, and clone the dependency repositories in checkout_dir,
before recursively processing the oca_dependencies.txt files of the
dependencies.

The expected format for oca_dependencies.txt:

* comment lines start with # and are ignored
* a dependency line contains:
  - the name of the OCA project
  - (optional) the URL to the git repository (defaulting to the OCA repository)
  - (optional) the name of the branch to use (defaulting to ${VERSION}). It is
    required if you want to select a commit SHA in the next parameter.
  - (optional) the commit SHA1 to use. If you set this option you MUST specify
    the branch
"""
from __future__ import print_function
import sys
import os
import os.path as osp
import subprocess
import logging
import shutil

_logger = logging.getLogger()
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


def parse_depfile(depfile, owner='OCA'):
    deps = []
    for line in depfile:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        num_parts = len(parts)
        repo, url, branch, commit = [
            num_parts > i and parts[i] for i in range(4)]
        if not branch:
            branch = os.environ.get('VERSION', '8.0')
        if not url:
            url = 'https://github.com/%s/%s.git' % (owner, repo)
        deps.append((repo, url, branch, commit))
    return deps


def git_checkout(deps_checkout_dir, reponame, url, branch, commit=False):
    checkout_dir = osp.join(deps_checkout_dir, reponame)
    if not osp.isdir(checkout_dir):
        command = ['git', 'clone', '-q', url, '-b', branch,
                   '--single-branch', '--depth=1', checkout_dir]
    else:
        command = ['git', '--git-dir=' + os.path.join(checkout_dir, '.git'),
                   '--work-tree=' + checkout_dir, 'pull', '--ff-only',
                   url, branch]
    if commit:
        try:
            command.remove('--depth=1')
            command.remove('--ff-only')
        except ValueError:
            pass
    _logger.info('Calling %s', ' '.join(command))
    subprocess.check_call(command)
    if commit:
        command = ['git',  '--git-dir=' + os.path.join(checkout_dir, '.git'),
                   '--work-tree=' + checkout_dir, 'reset', '--hard', commit]
        _logger.info('Calling %s', ' '.join(command))
        subprocess.check_call(command)
    return checkout_dir


def move_module_to_dir(checkout_dir, dest_dir):
    if not osp.isdir(checkout_dir):
        return
    for addon in os.listdir(checkout_dir):
        if addon.startswith("."):
            continue
        src_path = osp.join(checkout_dir, addon)
        if osp.isdir(src_path):
            dst_path = osp.join(dest_dir, addon)
            if osp.isdir(dst_path):
                _logger.error('%s already exists', dst_path)
            else:
                _logger.info('Moving %s to %s', src_path, dst_path)
                shutil.move(src_path, dst_path)


def run(deps_checkout_dir, build_dir):
    dependencies = []
    processed = set()
    depfilename = osp.join(build_dir, 'oca_dependencies.txt')
    dependencies.append(depfilename)
    reqfilenames = []
    checkout_dirs = []
    if osp.isfile(osp.join(build_dir, 'requirements.txt')):
        reqfilenames.append(osp.join(build_dir, 'requirements.txt'))
    for repo in os.listdir(deps_checkout_dir):
        _logger.info('examining %s', repo)
        processed.add(repo)
        depfilename = osp.join(deps_checkout_dir, repo, 'oca_dependencies.txt')
        dependencies.append(depfilename)
        reqfilename = osp.join(deps_checkout_dir, repo, 'requirements.txt')
        if osp.isfile(reqfilename):
            reqfilenames.append(reqfilename)
    for depfilename in dependencies:
        try:
            with open(depfilename) as depfile:
                deps = parse_depfile(depfile)
        except IOError:
            deps = []
        for depname, url, branch, commit in deps:
            _logger.info('* processing %s', depname)
            if depname in processed:
                continue
            processed.add(depname)
            checkout_dir = git_checkout(deps_checkout_dir, depname,
                                        url, branch, commit)
            checkout_dirs.append(checkout_dir)
            new_dep_filename = osp.join(checkout_dir, 'oca_dependencies.txt')
            reqfilename = osp.join(checkout_dir, 'requirements.txt')
            if osp.isfile(reqfilename):
                reqfilenames.append(reqfilename)
            if new_dep_filename not in dependencies:
                dependencies.append(new_dep_filename)
    for reqfilename in reqfilenames:
        command = ['pip', 'install', '-Ur', reqfilename]
        _logger.info('Calling %s', ' '.join(command))
        subprocess.check_call(command)
    for checkout_dir in checkout_dirs:
        move_module_to_dir(checkout_dir, os.environ["ADDONS_PATH"])


if __name__ == '__main__':
    if len(sys.argv) == 1:
        deps_checkout_dir = osp.join(os.environ['HOME'], 'dependencies')
        if not osp.exists(deps_checkout_dir):
            os.makedirs(deps_checkout_dir)
        build_dir = os.environ['CI_PROJECT_DIR']
    elif len(sys.argv) == 2 or len(sys.argv) > 3:
        print(__doc__)
        sys.exit(1)
    else:
        deps_checkout_dir = sys.argv[1]
        build_dir = sys.argv[2]
    run(deps_checkout_dir, build_dir)
