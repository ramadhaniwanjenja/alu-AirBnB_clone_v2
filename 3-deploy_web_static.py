#!/usr/bin/python3
from fabric import task
from datetime import datetime
from os.path import exists, isdir
import os

# Define the hosts and other Fabric environment details
env = {
    "hosts": ['18.215.176.44', '54.84.75.2'],
    "user": "ubuntu",
    "key_filename": "~/.ssh/id_rsa"
}

@task
def do_pack(c):
    """generates a tgz archive"""
    try:
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        if not isdir("versions"):
            os.makedirs("versions")
        file_name = "versions/web_static_{}.tgz".format(date)
        c.local("tar -cvzf {} web_static".format(file_name))
        return file_name
    except Exception as e:
        print(f"Error in packing: {e}")
        return None

@task
def do_deploy(c, archive_path):
    """distributes an archive to the web servers"""
    if not exists(archive_path):
        return False
    try:
        file_n = archive_path.split("/")[-1]
        no_ext = file_n.split(".")[0]
        path = "/data/web_static/releases/"
        c.put(archive_path, '/tmp/')
        c.run('mkdir -p {}{}/'.format(path, no_ext))
        c.run('tar -xzf /tmp/{} -C {}{}/'.format(file_n, path, no_ext))
        c.run('rm /tmp/{}'.format(file_n))
        c.run('mv {0}{1}/web_static/* {0}{1}/'.format(path, no_ext))
        c.run('rm -rf {}{}/web_static'.format(path, no_ext))
        c.run('rm -rf /data/web_static/current')
        c.run('ln -s {}{}/ /data/web_static/current'.format(path, no_ext))
        return True
    except Exception as e:
        print(f"Error in deployment: {e}")
        return False

@task
def deploy(c):
    """creates and distributes an archive to the web servers"""
    archive_path = do_pack(c)
    if archive_path is None:
        return False
    return do_deploy(c, archive_path)

