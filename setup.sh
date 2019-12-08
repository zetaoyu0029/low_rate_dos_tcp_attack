# install mininet

git clone git://github.com/mininet/mininet

sudo mininet/util/install.sh -a

# install dependencies

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

python get-pip.py

apt-get install -y python-subprocess32

sudo pip install matplotlib

sudo pip install lumpy

sudo pip install termcolor

sudo mininet/util/install.sh -a
