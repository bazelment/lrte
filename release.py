#!/usr/bin/python3 -u

'''Release both GRTE and crosstool by building them inside docker
container'''

import argparse
import os
import os.path
import subprocess

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


def main():
    parser = argparse.ArgumentParser(
        description = __doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--docker_image', default='build',
                        help='Name of the docker image to use')
    parser.add_argument('--email', default=os.getenv('EMAIL'),
                        help='Email address used as package maintainer')
    parser.add_argument('--output', default=os.path.join(os.path.dirname(__file__), 'output'),
                        help='Directory to store the output')
    parser.add_argument('--debug', action='store_true',
                        help='Start the docker container using bash')
    parser.add_argument('--build_grte', default=True,
                        help='Whether to build grte or skip it')
    parser.add_argument('--grte_prefix', default='/usr/grte',
                        help='Directory prefix when grte gets installed')
    parser.add_argument('--grte_package_prefix', default='',
                        help='Prefix used in names of  grte packages')
    parser.add_argument('--grte_skip', choices=['step1', 'step2', 'final'], action='append',
                        help='Steps to skip when building GRTE(which could be step1, step2, final)')
    parser.add_argument('--upstream_source', default=os.path.join(os.path.dirname(__file__), 'upstream'),
                        help='Directory that stores original downloaded packages, like glibc code')

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
        'GRTE_PACKAGE_PREFIX' : args.grte_package_prefix,
    }
    if args.email:
        env['EMAIL'] = args.email
    if args.grte_skip:
        for skip in args.grte_skip:
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


    if args.build_grte:
        start_container(args.docker_image,
                        ['./build_grte.sh', args.grte_prefix, os.path.join(output_dir, 'grte')],
                        workdir = topdir,
                        attach_stdin = True,
                        attach_stdout = True,
                        attach_stderr = True,
                        mounts = mounts,
                        environment = env)
        print('deb packages: %s' % (os.path.join(output_dir, 'grte/results/debs')))
        print('rpm packages: %s' % (os.path.join(output_dir, 'grte/results/rpms')))
    


if __name__ == '__main__':
    main()
