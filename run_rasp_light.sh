apt-get update

## configure vnc-server (optional)
# sudo apt-get install realvnc-vnc-server
# sudo raspi-confi

## install python 3."6"
apt-get install python3-dev libffi-dev libssl-dev -y
wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
tar xJf Python-3.6.3.tar.xz
cd Python-3.6.3
./configure
make
make install
pip3 install --upgrade pip
cd ..
rm Python-3.6.3.tar.xz

## installing and setting up "nmcli" is a bit tricky
apt-get install network-manager
# and some configs...

## easier way to connect to wifi 
nano /etc/wpa_supplicant/wpa_supplicant.conf
# add this to the bottom:
network={
    ssid="testing"
    psk="testingPassword"
}

## install python dependencies
pip install --upgrade setuptools
apt-get install python3-pygame libsqlite3-dev
pip3 install -r requirements.txt
cd Python-3.6.3
make altinstall
