#!/usr/bin/python3

# TODO: Have world parallels compressed together under main world name?
# TODO: Set date in archive name to date of backup, not date of archive
# TODO: Ensure number of concurrent backups reflects the setting in YAML

import yaml
from subprocess import call
import glob, os, datetime

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
  world_path = os.path.join(server_path, name)
  compressed_name = f"{name}.tar.gz"
  compressed_path = os.path.join(server_path, compressed_name)
  print(f"      Backing up world at: {world_path}")
  if os.path.exists(world_path):
    print(f"         Compressing world '{name}'")
    call([
      "tar",
      "-zcf",
      compressed_path,
      world_path
    ])
    print(f"         Rsyncing compressed world '{name}'")
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
    print(f"         Deleting compressed world '{name}'")
    call([
      "rm",
      compressed_path
    ])
  else:
    print(f"         Did not find world at: {world_path}")
    
def get_world_archives(server_path, world_name):
  return glob.glob(os.path.join(backup_path, archive_path, server_path, f"{world_name}.*"))

def keep_first_n_files(files, n):
  deleted_count = 0;
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
  deleted_count = keep_first_n_files(sorted(get_world_archives(server_path, world_name)), total_backups - 1)
  if deleted_count:
    print(f"      Deleted {deleted_count} expired '{world_name}' archives.")
  else:
    print(f"      Did not find any expired '{world_name}' archives")
  print(f"   Creating new backup of world '{world_name}'")
  backup_world(server_path, world_name)
  print()

for server in servers:
  server_path = server["Path"]
  server_worlds = server["Worlds"]
  for world in server_worlds:
    manage_world_backups(server_path, world["Name"], world["TotalBackups"])
    for parallel in parallels:
      main_world_name = world["Name"]
      world_name = f"{main_world_name}{parallel}"
      manage_world_backups(server_path, world_name, world["TotalBackups"])
