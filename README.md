# DOGS - Digital Ocean Gaming Services

Run short lived servers and save them as snapshots when done to save on \$\$\$.

## Why is this necessary?

Digital Ocean still charges for servers even when powered off, however it only costs
pennies to save snapshots of a server at anytime that can be restored. Perfect for
creating gaming servers for playing with friends at night, while saving cash the rest of the time.

https://codecalamity.com/on-demand-gaming-server-for-pennies/

Requirements:

- Have an active droplet with a name
- Have a DO API Key
- Python 3.7

How to get started:

```
git clone https://github.com/cdgriffith/dogs.git
# Create a venv if you are python savvy
pip install -r requirements.txt
cp config.yaml.example config.yaml
# Update the config file to match your digital ocean settings
python -m dogs

# Once Droplet is running (assuming you've added your public SSH to your account)
ssh root@droplet_ip
# scp -r ./services root@droplet_ip
# find factorio (if you need to)
chmod -R 775 ./services
# for factorio, run the
./factorio/create.sh
# do the manual stuff it tells you to do
```

If you use mods in factorio, I suggest using the [fac-cli](https://github.com/mickael9/fac)

In `~/.config/fac/config.ini` put
```
[paths]
data-path = /opt/factorio/factorio/data
write-path = /opt/factorio/factorio
```

So, all together
```
# install pip3
apt install python3-pip
# install fac
pip3 install -e "git+https://github.com/mickael9/fac.git#egg=fac-cli"
# create ~/.config/fac/config.ini
mkdir ~/.config
mkdir ~/.config/fac
touch ~/.config/fac/config.ini
echo "[paths]" >> ~/.config/fac/config.ini
echo "data-path = /opt/factorio/factorio/data" >> ~/.config/fac/config.ini
echo "write-path = /opt/factorio/factorio" >> ~/.config/fac/config.ini
fac
```

---

Existing bugs:
* document factorio version updating
* update.sh does not work
* document mod updating

see: https://wiki.factorio.com/Multiplayer#Additional_configuration
