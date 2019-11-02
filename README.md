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

# for factorio, run the ./factorio/create.sh
# do the manual stuff at the bottom`
```
