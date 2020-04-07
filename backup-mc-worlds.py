#!/usr/bin/python3

# TODO: Set date in archive name to date of backup, not date of archive
# TODO: Ensure number of concurrent backups reflects the setting in YAML

import yaml
from subprocess import call
import glob
import os
import datetime

with open(os.path.join(os.path.dirname(__file__), "backup-mc-worlds_params.yaml"), 'r') as stream:
    params = yaml.safe_load(stream)

root = params["Root"]
backup_path = params["Backup"]["Path"]
archive_path = params["Backup"]["ArchivePath"]
servers = params["Servers"]
parallels = params["Parallels"]

os.chdir(root)

datetime_string = str(datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"))


def backup_world(server_path, name):
    print(f"   Creating new backup of '{name}' worlds")
    main_world_path = os.path.join(server_path, name)

    compress_command, compressed_path = generate_world_compression(
        server_path, name)

    print(f"      Backing up '{name}' worlds at: {server_path}")
    if os.path.exists(main_world_path):
        print(f"         Compressing '{name}' worlds")
        call(compress_command)
        print(f"         Rsyncing compressed '{name}' worlds")
        call([
            "rsync",
            "-a",
            "-b",
            "-R",
            f"--backup-dir={archive_path}",
            f"--suffix=.{datetime_string}",
            compressed_path,
            backup_path
        ])
        print(f"         Cleaning away compressed '{name}' worlds file")
        call([
            "rm",
            compressed_path
        ])
    else:
        print(f"         Did not find world at: {main_world_path}")


def generate_world_compression(server_path, name):
    compressed_name = f"{name}.tar.gz"
    compressed_path = os.path.join(server_path, compressed_name)
    compress_command = [
        "tar",
        "-zcf",
        compressed_path,
    ]
    main_world_path = os.path.join(server_path, name)
    if os.path.exists(main_world_path):
        compress_command.append(main_world_path)

    for parallel in parallels:
        parallel_name = f"{name}{parallel}"
        parallel_path = os.path.join(server_path, parallel_name)
        if os.path.exists(parallel_path):
            compress_command.append(parallel_path)
    return [compress_command, compressed_path]


def get_world_archives(server_path, world_name):
    return glob.glob(os.path.join(backup_path, archive_path, server_path, f"{world_name}.*"))


def keep_first_n_files(files, n):
    deleted_count = 0
    for i in range(n, len(files)):
        print(f"      Deleting file {i} since {n} at: {files[i]}")
        call([
            "rm",
            files[i]
        ])
        deleted_count += 1
    return deleted_count


def manage_world_backups(server_path, world_name, total_backups):
    print(f"Now managing world backups of world '{world_name}'")
    print(f"   Deleting expired '{world_name}' archives:")
    deleted_count = keep_first_n_files(
        sorted(get_world_archives(server_path, world_name)), total_backups - 1)
    if deleted_count:
        print(
            f"      Deleted {deleted_count} expired '{world_name}' archives.")
    else:
        print(f"      Did not find any expired '{world_name}' archives")
    backup_world(server_path, world_name)
    print()


def main():
    for server in servers:
        server_path = server["Path"]
        server_worlds = server["Worlds"]
        for world in server_worlds:
            manage_world_backups(
                server_path, world["Name"], world["TotalBackups"])


if __name__ == "__main__":
    main()
