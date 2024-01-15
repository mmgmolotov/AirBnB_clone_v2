#!/usr/bin/python3
# Fabfile to distribute an archive to a web server.

import os.path
from fabric.api import env, put, run

env.user = "ubuntu"
env.hosts = ['52.3.247.21', '34.207.237.255']


def do_deploy(archive_path):
    """Distributes an archive to a web server.

    Args:
        archive_path (str): Local path to the archive to be deployed.

    Returns:
        bool: True if successful, False otherwise.
    """
    if not os.path.isfile(archive_path):
        print("Error: Specified archive file does not exist.")
        return False

    full_file = os.path.basename(archive_path)
    folder = os.path.splitext(full_file)[0]

    try:
        # Uploads archive to /tmp/ directory
        if put(archive_path, "/tmp/{}".format(full_file)).failed:
            raise Exception("Uploading archive to /tmp/ failed")

        # Clean up existing folder with the same name on the server
        if run("rm -rf /data/web_static/releases/{}/".format(folder)).failed:
            raise Exception("Deleting existing folder failed")

        # Create a new archive folder
        if run("mkdir -p /data/web_static/releases/{}/".format(folder)).failed:
            raise Exception("Creating new archive folder failed")

        # Uncompress archive to /data/web_static/releases/{}/ directory
        if run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(full_file, folder)).failed:
            raise Exception("Uncompressing archive failed")

        # Clean up: delete the uploaded archive
        if run("rm /tmp/{}".format(full_file)).failed:
            raise Exception("Deleting archive from /tmp/ directory failed")

        # Move content from web_static to its parent folder
        if run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/".format(folder, folder)).failed:
            raise Exception("Moving content to archive folder failed")

        # Clean up: delete the empty web_static folder
        if run("rm -rf /data/web_static/releases/{}/web_static".format(folder)).failed:
            raise Exception("Deleting web_static folder failed")

        # Clean up: delete current folder (the symbolic link)
        if run("rm -rf /data/web_static/current").failed:
            raise Exception("Deleting 'current' folder failed")

        # Create new symbolic link on the web server linked to the new code version
        if run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(folder)).failed:
            raise Exception("Creating new symbolic link to new code version failed")

        print("New version deployed!")
        return True

    except Exception as e:
        print("Error:", e)
        return False
