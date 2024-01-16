from fabric.api import local, env, put, run, settings, sudo
from datetime import datetime
from os.path import exists, isdir

env.hosts = ['52.3.247.21', '34.207.237.255']


def do_deploy(archive_path):
    """distributes an archive to the web servers"""
    if exists(archive_path) is False:
        return False
    try:
        file_n = archive_path.split("/")[-1]
        no_ext = file_n.split(".")[0]
        path = "/data/web_static/releases/"

        print(f"Remote path: {path}{no_ext}/")  # Debugging output

        put(archive_path, '/tmp/')
        sudo('mkdir -p {}{}/'.format(path, no_ext))
        sudo('tar -xzf /tmp/{} -C {}{}/'.format(file_n, path, no_ext))
        sudo('rm /tmp/{}'.format(file_n))
        sudo('mv {0}{1}/web_static/* {0}{1}/'.format(path, no_ext))
        sudo('rm -rf {}{}/web_static'.format(path, no_ext))
        
        with settings(warn_only=True):
            sudo('rm -rf /data/web_static/current')

        sudo('ln -s {}{}/ /data/web_static/current'.format(path, no_ext))
        return True
    except Exception as e:
        print(f"Error in do_deploy: {e}")
        return False
