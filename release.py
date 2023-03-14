#!/usr/bin/python3 -u

'''Release both LRTE and crosstool by building them inside docker
container'''

import argparse
import os
import os.path
import subprocess
import tempfile

def start_container(docker_image, command,
                    container_name = None,
                    attach_stdin = False,
                    attach_stderr = False,
                    attach_stdout = False,
                    privileged = False,
                    workdir = None,
                    mounts = [],
                    portmap = {},
                    environment = {},
                    start_subprocess = True):
    '''Start a docker container with the given image and command.

    If the container_name is not None, the container will be forcibly removed
    first.

    Mounts is a list of tuple (host_file, container_file), which means
    a "host_file"(or directory) on host should be mounted as
    "container_file" inside the container.

    portmap is map from container_port to host_port, these ports
    insider container will be exposed by docker as host_port on the
    host side.

    If start_subprocess is True, docker run will run as a subprocess,
    otherwise os.exec will be used to replace the current process.
    '''
    if container_name:
        subprocess.call(['/usr/bin/docker', 'rm', '-f', container_name],
                        stderr = subprocess.DEVNULL)
    cmd = ['/usr/bin/docker', 'run', '-i', '-t',
           '--net=bridge', '--rm']
    if privileged:
        cmd.append('--privileged')
    if container_name:
        cmd.append('--name=' + container_name)
    # Attach stderr and stdout
    if attach_stdin:
        cmd += ['-a', 'stdin']
    if attach_stdout:
        cmd += ['-a', 'stdout']
    if attach_stderr:
        cmd += ['-a', 'stderr']
    if workdir:
        cmd += ['-w', workdir]
    for env_name, env_value in environment.items():
        cmd += ['-e', '%s=%s' %(env_name, env_value)]
    for c_port, h_port in portmap.items():
        cmd.append('--publish=%d:%d' % (h_port, c_port))
    # mount what we need
    for host_fname, container_fname in mounts:
        cmd += ['-v', '%s:%s' % (host_fname, container_fname)]
    cmd.append(docker_image)
    if type(command) == str:
        cmd.append(command)
    else:
        cmd += command
    print("=== Running %s" % (str(cmd)))
    if start_subprocess:
        subprocess.check_call(cmd)
    else:
        os.execv(cmd[0], cmd)


def get_svn_revision(svn_directory, svn_url):
    try:
        svn_version = subprocess.check_output(
            ['svn info |grep Revision:'],
            shell=True, universal_newlines=True,
            cwd=svn_directory)
        return svn_version.split(': ')[1].strip()
    except subprocess.CalledProcessError:
        print('Please checkout code from ' + svn_url)
        raise


def build_lrte(args, topdir, mounts, env, lrte_output, lrte_output_in_docker):
    with tempfile.NamedTemporaryFile(mode='w+') as tfile:
        tfile.write('''#!/bin/bash
# This runs inside docker container as root to build GRTE

set -x

GRTE_PREFIX=$1
GRTE_TMPDIR=$2
mkdir ${GRTE_PREFIX}

rm -rf grte/sources/*
./grte/prepare-sources.sh
./grte/grte-build ${GRTE_PREFIX} ${GRTE_TMPDIR}
bash
./grte/grte-package ${GRTE_PREFIX} ${GRTE_TMPDIR}
''')
        tfile.flush()
        start_container(args.docker_image,
                        ['/bin/bash', tfile.name, args.lrte_prefix, lrte_output_in_docker],
                        workdir = topdir,
                        attach_stdin = True,
                        attach_stdout = True,
                        attach_stderr = True,
                        mounts = mounts + [(tfile.name, tfile.name)],
                        environment = env)
    print('deb packages: %s' % (os.path.join(lrte_output, 'results/debs')))
    print('rpm packages: %s' % (os.path.join(lrte_output, 'results/rpms')))

        
def main():
    parser = argparse.ArgumentParser(
        description = __doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--docker_image', default='build',
                        help='Name of the docker image to use')
    parser.add_argument('--email', default=os.getenv('EMAIL', default='foo@bar.io'),
                        help='Email address used as package maintainer')
    parser.add_argument('--output', default=os.path.join(os.path.dirname(__file__), 'output'),
                        help='Directory to store the output')
    parser.add_argument('--debug', action='store_true',
                        help='Start the docker container using bash')
    parser.add_argument('--lrte_prefix', default='/usr/lrte',
                        help='Directory prefix where lrte gets installed')
    parser.add_argument('--lrte_package_prefix', default='',
                        help='Prefix used in names of lrte packages, by default, '
                        'the packages are name like lrtev1-runtime_1.0-3_amd64.deb, '
                        'setting a prefix like xyz will name the package like '
                        'xyzlrtev1-runtime_1.0-3_amd64.deb')
    parser.add_argument('--lrte_skip', choices=['stage1', 'stage2', 'final'], action='append',
                        help='Stage to skip when building LRTE(which could be stage1, stage2, final)')
    parser.add_argument('--upstream_source', default=os.path.join(os.path.dirname(__file__), 'upstream'),
                        help='Directory that stores original downloaded packages, like glibc code')
    parser.add_argument('--actions', choices=['lrte', 'crosstool', 'check'], nargs='+',
                        help='Select the actions to perform')
    parser.add_argument('--crosstool_skip', choices=['gcc'], action='append',
                        help='Steps to skip when building crosstool')

    args = parser.parse_args()

    mounts = []
    topdir = os.path.abspath(os.path.dirname(__file__))
    mounts.append((topdir, topdir))
    # Output dir in docker
    output_dir = '/output'
    sources_dir = '/sources'  # This has to match TAR_DIR in prepare-sources.sh
    mounts.append((os.path.abspath(args.output), output_dir))
    mounts.append((os.path.abspath(args.upstream_source), sources_dir))

    env = {
        'JFLAGS' : '-j8',
        'GRTE_PACKAGE_PREFIX' : args.lrte_package_prefix,
    }
    if args.email:
        env['EMAIL'] = args.email
    if args.lrte_skip:
        for skip in args.lrte_skip:
            env['SKIP_' + skip.upper()] = '1'

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    if args.debug:
        start_container(args.docker_image,
                        ['/bin/bash'],
                        workdir = topdir,
                        attach_stdin = True,
                        attach_stdout = True,
                        attach_stderr = True,
                        mounts = mounts,
                        start_subprocess=False,
                        environment = env)

    lrte_output = os.path.join(args.output, 'lrte')
    lrte_output_in_docker = os.path.join(output_dir, 'lrte')

    if 'lrte' in args.actions:
        build_lrte(args, topdir, mounts, env, lrte_output, lrte_output_in_docker)

    if 'crosstool' in args.actions:
        if not os.path.isdir(os.path.join(lrte_output, 'results/debs')):
            raise Exception(os.path.join(lrte_output, 'results/debs') + ' does not exit, please build LRTE packages first')
        env['GCC_SVN_VERSION'] = get_svn_revision(
            os.path.join(args.upstream_source, 'gcc-4_9'),
            'svn://gcc.gnu.org/svn/gcc/branches/google/gcc-4_9')
        env['CLANG_SVN_VERSION'] = get_svn_revision(
            os.path.join(args.upstream_source, 'llvm/tools/clang'),
            'http://clang.llvm.org/get_started.html')
        if args.crosstool_skip:
            for skip in args.crosstool_skip:
                env['SKIP_CROSSTOOL_' + skip.upper()] = '1'
        start_container(args.docker_image,
                        ['./build_crosstool.sh', args.lrte_prefix,
                         lrte_output_in_docker,
                         sources_dir],
                        workdir = topdir,
                        attach_stdin = True,
                        attach_stdout = True,
                        attach_stderr = True,
                        mounts = mounts,
                        environment = env)

    if 'check' in args.actions:
        if not os.path.isdir(os.path.join(lrte_output, 'results/debs')):
            raise Exception(os.path.join(lrte_output, 'results/debs') + ' does not exit, please build LRTE packages first')
        start_container(args.docker_image,
                        ['./check.sh', args.lrte_prefix,
                         lrte_output_in_docker],
                        workdir = topdir,
                        attach_stdin = True,
                        attach_stdout = True,
                        attach_stderr = True,
                        mounts = mounts,
                        environment = env)



if __name__ == '__main__':
    main()
