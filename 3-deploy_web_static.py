#!/usr/bin/python3
"""Fabric script (based on the file 2-do_deploy_web_static.py) that creates and
distributes an archive to your web servers, using the function deploy"""
import os
from datetime import datetime
from fabric.api import *


env.hosts = ['52.3.247.21', '34.207.237.255']


def do_pack():
    """Creates archive from web_static directory"""
    local("mkdir -p versions")
    file = 'versions/web_static_{}.tgz'\
        .format(datetime.strftime(datetime.now(), "%Y%m%d%I%M%S"))
    comp = 'tar -cvzf {} web_static'.format(file)
    tar_file = local(comp)
    if tar_file.failed:
        return None
    else:
        return file


def do_deploy(archive_path):
    """Deploys an archive"""
    if not os.path.exists(archive_path):
        return False
    arch = archive_path.split('/')[1]
    name = arch.split('.')[0]
    tar_file = put(archive_path, '/tmp/{}'.format(arch))
    if tar_file.failed:
        return False
    tar_file = run('mkdir -p /data/web_static/releases/{}'.format(name))
    if tar_file.failed:
        return False
    tar_file = run(
        'tar -xzf /tmp/{} -C /data/web_static/releases/{}/'
        .format(arch, name))
    if tar_file.failed:
        return False
    tar_file = run('rm /tmp/{}'.format(arch))
    if tar_file.failed:
        return False

    # Copy or create my_index.html
    index_content = "<html><head></head><body><p>My Index Content</p></body></html>"
    index_path = '/data/web_static/releases/{}/my_index.html'.format(name)
    run("echo '{}' > {}".format(index_content, index_path))

    comp = 'mv /data/web_static/releases/{0}/web_static/*'
    comp += ' /data/web_static/releases/{0}/'
    tar_file = run(comp.format(name))
    if tar_file.failed:
        return False
    tar_file = run(
                'rm -rf /data/web_static/releases/{}/web_static'
                .format(name))
    if tar_file.failed:
        return False
    # Use sudo for the commands that require elevated privileges
    tar_file = sudo('rm -rf /data/web_static/current', user='root')
    if tar_file.failed:
        return False
    tar_file = sudo(
        'ln -s /data/web_static/releases/{}/ /data/web_static/current'
        .format(name), user='root')
    if tar_file.failed:
        return False
    print('New version deployed!')
    return True


def deploy():
    """ Fabric script (based on the file 2-do_deploy_web_static.py)
    that creates and distributes an archive to your web servers,
    using the function deploy"""
    archive = do_pack()
    if archive is None:
        return False
    tar_file = do_deploy(archive)
    return tar_file
