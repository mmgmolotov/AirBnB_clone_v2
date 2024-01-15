#!/usr/bin/python3
""" Compressed archive creation script """

from fabric.api import local
import time

def do_pack():
    """ Creates a compressed archive of web_static folder """
    try:
        current_time = time.strftime('%Y%m%d%H%M%S')
        filename = "web_static_{}.tgz".format(current_time)
        local("mkdir -p versions")
        local("tar -cvzf versions/{} web_static/".format(filename))
        return "versions/{}".format(filename)
    except Exception as e:
        print("An error occurred: {}".format(e))
        return None

# Calling the function
do_pack()
