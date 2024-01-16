from fabric.api import *
from datetime import datetime
from os.path import exists

env.hosts = ['52.3.247.21', '34.207.237.255']
env.key_filename = "~/.ssh/school"  # Add this line to specify the private key file

def do_deploy(archive_path):
    """Distributes an archive to my web servers"""
    if not exists(archive_path):
        return False

    filename = archive_path.split('/')[-1]
    no_tgz = '/data/web_static/releases/' + "{}".format(filename.split('.')[0])
    tmp = "/tmp/" + filename

    try:
        put(archive_path, "/tmp/")
        run("mkdir -p {}/".format(no_tgz))
        run("tar -xzf {} -C {}/".format(tmp, no_tgz))
        run("rm {}".format(tmp))
        run("mv {}/web_static/* {}/".format(no_tgz, no_tgz))
        run("rm -rf {}/web_static".format(no_tgz))
        run("rm -rf /data/web_static/current")
        run("ln -s {}/ /data/web_static/current".format(no_tgz))

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
