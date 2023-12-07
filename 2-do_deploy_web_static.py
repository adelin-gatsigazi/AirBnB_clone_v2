#!/usr/bin/python3
"""
Fabric script that distributes an archive to your web servers
"""

from fabric.api import env, put, run, local
from os.path import exists
from datetime import datetime

env.hosts = ['<IP web-01>', '<IP web-02>']
env.user = '<your_username>'
env.key_filename = ['<path_to_your_private_key>']


def do_pack():
    """
    Generate a .tgz archive from the contents of the web_static folder
    """
    try:
        local("mkdir -p versions")
        timestr = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = "versions/web_static_{}.tgz".format(timestr)
        local("tar -cvzf {} web_static".format(filename))
        return filename
    except Exception:
        return None


def do_deploy(archive_path):
    """
    Distribute an archive to your web servers
    """
    if not exists(archive_path):
        return False

    try:
        # Upload the archive
        put(archive_path, "/tmp/")

        # Extract the archive to the web server
        filename = archive_path.split("/")[-1]
        foldername = "/data/web_static/releases/{}".format(filename.split(".")[0])
        run("mkdir -p {}".format(foldername))
        run("tar -xzf /tmp/{} -C {}".format(filename, foldername))

        # Delete the archive from the web server
        run("rm /tmp/{}".format(filename))

        # Move contents out of web_static and clean up
        run("mv {}/web_static/* {}".format(foldername, foldername))
        run("rm -rf {}/web_static".format(foldername))

        # Update symbolic link
        run("rm -rf /data/web_static/current")
        run("ln -s {} /data/web_static/current".format(foldername))

        print("New version deployed!")

        return True
    except Exception:
        return False
        

