#!/usr/bin/python3
"""
Fabric script that distributes an archive to your web servers
"""

from datetime import datetime
from fabric.api import *
import os

env.hosts = ['52.3.247.21', '34.207.237.255']
env.user = "ubuntu"


def do_pack():
    """
        return the archive path if archive has generated correctly.
    """

    local("mkdir -p versions")
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    archived_f_path = "versions/web_static_{}.tgz".format(date)
    t_gzip_archive = local("tar -cvzf {} web_static".format(archived_f_path))

    if t_gzip_archive.succeeded:
        return archived_f_path
    else:
        return None


def do_deploy(archive_path):
    """
    Distribute archive.
    """
    if not os.path.exists(archive_path):
        print(f"Error: Archive {archive_path} not found.")
        return False

    try:
        # Extract version from the archive path
        version = archive_path.split("/")[-1][:-4]

        # Upload the archive to the server
        put(archive_path, "/tmp/")

        # Create directories and extract files
        with cd("/data/web_static/releases/"):
            run(f"sudo mkdir -p {version}")
            run(f"sudo tar -xzf /tmp/{version}.tgz -C {version}")
            run(f"sudo rm /tmp/{version}.tgz")

            # Move files to the proper location
            run(f"sudo mv {version}/web_static/* {version}")
            run(f"sudo rm -rf {version}/web_static")

            # Update the symbolic link
            run(f"sudo rm -rf /data/web_static/current")
            run(f"sudo ln -s /data/web_static/releases/{version} /data/web_static/current")

        print("New version deployed!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
