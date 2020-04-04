# backup-mc-worlds
My backup script for my Minecraft server! 🤓

This script uses `rsync` to compress and backup Minecraft worlds.

## Configuration

Requires a configuration YAML file 'backup-mc-worlds_params.yaml' to be in the same directory as the script.

Example:
```yaml
Root: "/home/minecraft/"
Backup:
  Path: "backup/"
  ArchivePath: "archive/"
Parallels:
  - "_nether"
  - "_the_end"
Servers:
  - Path: "paper-server/"
    Worlds:
      - Name: "world"
        TotalBackups: 10
      - Name: "skyblock"
        TotalBackups: 5
      - Name: "ilyana"
        TotalBackups: 3
  - Path: "snapshot-server/"
    Worlds:
      - Name: "world"
        TotalBackups: 3

```
## Explanation of config parameters: 
### Root
The directory that contains all of your minecraft server files
### Backup
#### Path
Target directory for Minecraft world backups
#### ArchivePath
A directory inside `Backup.Path` directory where `rsync` will store "archived" backups
### Parallels
Suffixed worlds such as the Nether and The End that should be kept up to date with the world that they are linked to.
### Servers
#### Path
Path to and individual server directory
#### Worlds
##### Name
Name of a main world. Don't include `*_nether`, `*_the_end` etc.
##### TotalBackups
Number of backups of this world that should be kept. Oldest backups beyond this limit are deleted. This total is _supposed to_ include the backup in `backup/<Server.Path>/` plus those in `backup/archive/<Server.Path>/`
