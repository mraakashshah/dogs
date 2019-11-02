from pathlib import Path
from itertools import count

import cutie
from appdirs import user_config_dir
from box import Box

from dogs.dogs import DOGS, find_droplets, find_snapshots

user_config_file = Path(
    user_config_dir(appname="DOGS", roaming=True, appauthor=False), "config.yaml"
)
local_config_file = Path("config.yaml")


def find_config_file():
    if user_config_file.exists() and local_config_file.exists():
        print(
            "Config files were found in both local and user directory, which do you want to use?"
        )
        opts = [user_config_file, local_config_file]
        return opts[cutie.select(opts)]
    elif local_config_file.exists():
        print("Using local config file")
        return local_config_file
    elif user_config_file.exists():
        print("Using stored config file")
        return user_config_file
    else:
        raise Exception("No config file found!")


def stats(server_config, general_config, details=False):
    print(f"\nServer: {server_config}")
    tabbed = "\n    "
    si = server_config
    print(f"    region: {si.region}")
    print(f"    size: {si.size}")
    print(f"    maximum snapshots: {si.snapshot_max}\n")
    if details:
        drops = find_droplets(server_config, general_config)
        if drops:
            print(" Droplets:")
            print(f"    {tabbed.join(drops)}")
        snaps = find_snapshots(server_config, general_config)
        if snaps:
            print(" Snapshots:")
            print(f"    {tabbed.join(snaps)}")


def manage(server_config, config_file):
    server_continue = False
    for _ in count():
        if not server_continue:
            print("\nWhich server do you want to manage?")
            opts = list(server_config.servers) + ["Exit"]
            selection = cutie.select(options=opts)
            if selection == len(opts) - 1:
                break
            server_selection = list(server_config.servers)[selection]
            stats(server_selection, server_config, details=False)
        else:
            server_selection = server_continue
        server_continue = False

        dogs = DOGS(server_selection, config_file)
        if dogs.droplet:
            print(f"Running: {dogs.droplet.ip_address}")
        else:
            print("Currently not running")

        actions = [
            "Turn On",
            "Shutdown",
            "View Server Info",
            "Cleanup Old Snapshots",
            "Cancel",
        ]
        print("\nManage:")
        action = actions[cutie.select(actions, selected_index=1 if dogs.droplet else 0)]

        if action == "Turn On":
            print("\nTurning droplet on\n")
            dogs.create()
        elif action == "Shutdown":
            print("\nShutting down droplet\n")
            dogs.destroy()
        elif action == "Cleanup Old Snapshots":
            print("\nRemoving old snapshots\n")
            dogs.cleanup()
        elif action == "View Server Info":
            stats(server_selection, server_config, details=True)
            server_continue = server_selection
            continue

        print("\nWould you like to:")
        selection = cutie.select(["Manage more", "Exit"], selected_index=1)
        if selection == 0:
            continue
        else:
            break


def main():
    config_file = find_config_file()
    server_config = Box.from_yaml(filename=config_file)
    manage(server_config, config_file)


if __name__ == "__main__":
    main()
