#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to web servers
"""
from fabric.api import run, env, local, put, sudo
from os.path import exists
from datetime import datetime

env.hosts = ['52.3.247.21', '34.207.237.255']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/school'


def do_pack():
    """
    Create a compressed archive of the web_static folder
    """
    local("mkdir -p versions")
    time_format = "%Y%m%d%H%M%S"
    archive_path = "versions/web_static_{}.tgz".format(datetime.now().strftime(time_format))

    # Include my_index.html if it exists
    index_html_path = "web_static/my_index.html"
    index_html_flag = "-C web_static/ {}".format(index_html_path) if exists(index_html_path) else ""

    result = local("tar -cvzf {} {} web_static".format(archive_path, index_html_flag))

    if result.failed:
        return None
    return archive_path

def do_deploy(archive_path):
    """
    Distribute an archive to web servers and deploy the code
    """
    if not exists(archive_path):
        return False

    filename = archive_path.split("/")[-1]
    path_no_ext = "/data/web_static/releases/{}".format(filename[:-4])

    put(archive_path, '/tmp/')
    run("mkdir -p {}".format(path_no_ext))
    run("tar -xzf /tmp/{} -C {}".format(filename, path_no_ext))
    run("rm /tmp/{}".format(filename))
    
    # Explicitly move my_index.html to the correct location
    run("mv {}/web_static/my_index.html {}".format(path_no_ext, path_no_ext))
    
    run("mv {}/web_static/* {}".format(path_no_ext, path_no_ext))
    run("rm -rf {}/web_static".format(path_no_ext))

    # Use sudo for chmod
    sudo("chmod -R u+w /data/web_static")

    # Change ownership to www-data
    sudo("chown -R www-data:www-data {}".format(path_no_ext))

    # Remove the symbolic link and create a new one
    sudo("rm -rf /data/web_static/current")
    sudo("ln -s {} /data/web_static/current".format(path_no_ext))

    return True

def deploy():
    """
    Create and distribute an archive to web servers
    """
    archive_path = do_pack()
    if not archive_path:
        return False

    return do_deploy(archive_path)
