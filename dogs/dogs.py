#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import sys
import digitalocean
from box import Box

_manager = None


class DOGS:
    def __init__(self, server_config, config_file="config.yaml"):
        general_config = Box.from_yaml(filename=config_file)
        self.token = general_config.token
        self.snapshot_max = general_config.snapshot_max
        self.config = server_config
        self.name = server_config.get("name")
        self.droplet_id = server_config.get("droplet_id")
        self.manager = digitalocean.Manager(token=self.token)
        self.droplet = None
        if self.droplet_id:
            try:
                self.droplet = self.manager.get_droplet(self.droplet_id)
            except digitalocean.Error:
                try:
                    for d in self.manager.get_all_droplets():
                        if d.name == self.name:
                            self.droplet = d
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        if self.droplet:
            print("droplet found")
            assert (
                self.droplet.name == self.name
            ), "Droplet name and config name do not match!"

    def create_from_snapshot(self, snapshot):
        account_keys = self.manager.get_all_sshkeys()
        config_keys = self.config.get("ssh_keys")
        if config_keys:
            keys = [key.id for key in account_keys if key.public_key in config_keys]
        else:
            keys = [key.id for key in account_keys]
        my_droplets = self.manager.get_all_droplets()
        for drop in my_droplets:
            assert drop.name != self.name, "Droplet already exists"
        new_droplet = digitalocean.Droplet(
            name=self.name,
            size=self.config.get("size", "s-1vcpu-1gb"),
            image=snapshot.id,
            region=self.config.get("region", "nyc3"),
            ssh_keys=keys,
            monitoring=True,
            token=self.token,
            tags=[self.name],
        )

        print(f"Creating droplet from snapshot {snapshot.id}")
        new_droplet.create()
        self.droplet = new_droplet

    def find_newest_snapshot(self):
        print("Finding newest snapshot")
        snapshots = self.manager.get_all_snapshots()
        newest = 0
        snapshot = None
        for snap in snapshots:
            print(snap)
            if snap.name.startswith(str(self.name)):
                if snap.name.endswith("base") and newest == 0:
                    snapshot = snap
                else:
                    dt = int(snap.name.split("-")[-1])
                    if dt > newest:
                        newest = dt
                        snapshot = snap
        return snapshot

    def wait_for_action(self, action=None, action_name=None):
        if action_name:
            for a in self.droplet.get_actions():
                if a.type == action_name:
                    action = a
                    break
            else:
                raise AssertionError(f"could not find {action_name} action")

        for i in range(20):
            action.load()
            print(f"{action.type}: {action.status}")
            if action.status == "completed":
                break
            elif action.status == "in-progress":
                time.sleep(15)
            else:
                raise Exception(action.status)
        else:
            raise AssertionError(f"Could not {action.type}")

    def create(self):
        snapshot = self.find_newest_snapshot()
        if not snapshot:
            raise AssertionError("No relevant snapshot found")
        self.create_from_snapshot(snapshot)
        self.wait_for_action(action_name="create")
        self.droplet.load()
        print(f"Droplet online: {self.droplet.ip_address}")

        if self.config.get("firewall_id"):
            print("Adding droplet to Firewall")
            firewall = self.manager.get_firewall(self.config.get("firewall_id"))
            firewall.add_droplets([self.droplet.id])

    def destroy(self, cleanup=True):
        shutdown_info = self.droplet.shutdown()
        shutdown_action = self.droplet.get_action(shutdown_info["action"]["id"])
        self.wait_for_action(action=shutdown_action)

        snap_name = f"{self.name}-{int(time.time())}"
        print(f"Creating snapshot: {snap_name}")
        snap_info = self.droplet.take_snapshot(snap_name)
        snap_action = self.droplet.get_action(snap_info["action"]["id"])
        self.wait_for_action(action=snap_action)

        if self.config.get("firewall_id"):
            print("Removing from firewall")
            firewall = self.manager.get_firewall(self.config.get("firewall_id"))
            firewall.remove_droplets([self.droplet.id])

        self.droplet.destroy()

        print("Droplet destroyed")

        if cleanup:
            self.cleanup()

    def cleanup(self):
        all_snapshots = self.manager.get_all_snapshots()
        relevant = []
        for snapshot in all_snapshots:
            if snapshot.name.startswith(str(self.name)):
                relevant.append(snapshot)

        relevant.sort(key=lambda x: int(x.name.split("-")[-1]), reverse=True)

        print(
            f"Deleting all but the newest {self.config.get('snapshot_max', 2)} snapshots"
        )
        for snapshot in relevant[self.config.get("snapshot_max", 2) :]:
            snapshot.destroy()


def find_droplets(prefix, config):
    manager = digitalocean.Manager(token=config.token)
    return [
        f"{x.name} @ {x.ip_address}"
        for x in manager.get_all_droplets()
        if x.name.startswith(str(prefix))
    ]


def find_snapshots(prefix, config):
    manager = digitalocean.Manager(token=config.token)
    return [
        f"{x.name}"
        for x in manager.get_all_snapshots()
        if x.name.startswith(str(prefix))
    ]
