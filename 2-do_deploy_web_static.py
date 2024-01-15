#!/usr/bin/python3
# Fabfile to distribute an archive to a web server.

import os.path
from fabric.api import env, put, run, abort

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
        abort("Error: Specified archive file does not exist.")

    full_file = os.path.basename(archive_path)
    folder = os.path.splitext(full_file)[0]

    try:
        upload_archive(archive_path, full_file)
        cleanup_existing_folder(folder)
        create_new_archive_folder(folder)
        uncompress_archive(full_file, folder)
        delete_uploaded_archive(full_file)
        move_content_to_archive_folder(folder)
        delete_empty_web_static_folder(folder)
        delete_current_folder()
        create_new_symbolic_link(folder)

        print("New version deployed!")
        return True

    except Exception as e:
        abort("Error: {}".format(e))


def upload_archive(archive_path, full_file):
    if put(archive_path, "/tmp/{}".format(full_file)).return_code != 0:
        raise Exception("Uploading archive to /tmp/ failed")


def cleanup_existing_folder(folder):
    if run("rm -rf /data/web_static/releases/{}/".format(folder)).return_code != 0:
        raise Exception("Deleting existing folder failed")


def create_new_archive_folder(folder):
    if run("mkdir -p /data/web_static/releases/{}/".format(folder)).return_code != 0:
        raise Exception("Creating new archive folder failed")


def uncompress_archive(full_file, folder):
    if run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(full_file, folder)).return_code != 0:
        raise Exception("Uncompressing archive failed")


def delete_uploaded_archive(full_file):
    if run("rm /tmp/{}".format(full_file)).return_code != 0:
        raise Exception("Deleting archive from /tmp/ directory failed")


def move_content_to_archive_folder(folder):
    if run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/".format(folder, folder)).return_code != 0:
        raise Exception("Moving content to archive folder failed")


def delete_empty_web_static_folder(folder):
    if run("rm -rf /data/web_static/releases/{}/web_static".format(folder)).return_code != 0:
        raise Exception("Deleting web_static folder failed")


def delete_current_folder():
    if run("rm -rf /data/web_static/current").return_code != 0:
        raise Exception("Deleting 'current' folder failed")


def create_new_symbolic_link(folder):
    if run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(folder)).return_code != 0:
        raise Exception("Creating new symbolic link to new code version failed")
