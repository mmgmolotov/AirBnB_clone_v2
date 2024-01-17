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
    result = local("tar -cvzf {} web_static".format(archive_path))

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
    run("mv {}/web_static/* {}".format(path_no_ext, path_no_ext))
    run("rm -rf {}/web_static".format(path_no_ext))

    # Use sudo for chmod
    sudo("chmod -R u+w /data/web_static")

    # Change ownership to www-data
    sudo("chown -R www-data:www-data {}".format(path_no_ext))

    # Create and deploy my_index.html
    run("echo '<html><head></head><body>My Custom Index</body></html>' > {}/my_index.html".format(path_no_ext))

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
