Running Pymavlink on the Sibiu Pro ROV
======================================

NOTE: This guide is based on BMeu's gist for Python 3.5, available at:
https://gist.github.com/BMeu/af107b1f3d7cf1a2507c9c6429367a3b
which was in turn taken from this tutorial:
https://liudr.wordpress.com/2016/02/04/install-python-on-raspberry-pi-or-debian/

As of July 2021, the defacto ArduSub Companion image for the RaspberryPi is
based on Raspbian Jessie, whose repositories are limited to Python 3.4 and
older. However, to use Pymavllink, a Python library that implements the
MAVLink protocol, we need Python 3.5 or later. This guide will explain how
to update your Sibiu ROV in case you want to run custom Python scripts on it.



## Pre-setup

Because we will compile lots of code from scratch on the RaspberryPi (for
convenience, we will avoid cross-compilation in this tutorial) you will have
to increase the available swap space on it since the available RAM might not
be sufficient or lead to extreme compilation times. To proceed, we will first
check if there is enough space on the SD card to create a swap file, and if not,
we will resort to a (temporary) external USB drive.

### Check disk space
1. Remove old logs to make room. Be adviced, **this will delete your ROV's logs**.

        sudo rm -rf ~/telemetry/logs/*

2. Check available disk space, look under the *Avail* column for `/`.

        df -h

### Create a swap file: on the SD card
If there are at least 3 GB of free storage on your SD card, it is possible
to create a swap file and compile everything right away. If not, please consider
using an external USB drive as explained in the next section.

1. Temporarily stop your system's swap.

        sudo dphys-swapfile swapoff


2. Increase the swap to 2GB. To do so, edit the file `/etc/dphys-swapfile`
and modify the variable `CONF_swapSIZE` to `2048`. You can use nano to do so
as follows (to save and exit, hit CTRL+o and then CTRL+x).

        sudo nano /etc/dphys-swapfile


3. Setup the new swap file.

        sudo dphys-swapfile setup

4. Start the swap.

        sudo dphys-swapfile swapon


5. Check that it worked. You should see that you have 2GB of swap available.

        free -mh


### Create a swap file: on an external USB drive
If you have already created a swap file on the SD card, skip this section. Note
that once you finish this guide, you may reboot the Raspberry Pi and remove
the drive for normal operation.

1. Insert an USB drive with at least 2GB of storage into the Raspberry.

2. Check that USB appears as /dev/sda, it might be sdb instead, so adjust
the next steps accordingly.

3. Tell the kernel to use the drive as extra swap (with high priority)

        sudo swapon -p 25000 /dev/sda1


4. Check that it worked. You should see that you have 2GB of swap available
(or more deppending on your drive)

        free -mh




## Setup

This section will describe how to update Python and how to install Pymavlink

## Python

We will install python 3.6.4. We have tested this version and it works fine
for applications that require Pymavlink

1. Install the required build-tools (some might already be installed on your system).

        sudo apt-get update
        sudo apt-get install build-essential tk-dev
        sudo apt-get install libncurses5-dev libncursesw5-dev libreadline6-dev
        sudo apt-get install libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev
        sudo apt-get install libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev


   If one of the packages cannot be found, try a newer version number (e.g. ``libdb5.4-dev`` instead of ``libdb5.3-dev``).

2. Download and install Python 3.6. When downloading the source code, select the most recent release of Python 3.6, available
   on the `official site <https://www.python.org/downloads/source/>`_. Adjust the file names accordingly.

        wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
        tar zxvf Python-3.6.4.tgz
        cd Python-3.6.4
        ./configure --prefix=/usr/local/opt/python-3.6.4
        make -j 2
        sudo make install

3. Make the compiled binaries globally available.

        sudo ln -s /usr/local/opt/python-3.6.4/bin/pydoc3.6 /usr/bin/pydoc3.6
        sudo ln -s /usr/local/opt/python-3.6.4/bin/python3.6 /usr/bin/python3.6
        sudo ln -s /usr/local/opt/python-3.6.4/bin/python3.6m /usr/bin/python3.6m
        sudo ln -s /usr/local/opt/python-3.6.4/bin/pyvenv-3.6 /usr/bin/pyvenv-3.6
        sudo ln -s /usr/local/opt/python-3.6.4/bin/pip3.6 /usr/bin/pip3.6

   You should now have a fully working Python 3.6 installation on your Raspberry Pi!

## Pymavlink

This step will be relatively slow. First, install all required Python libraries
(and some that will come in handy down the road), then, install lxml without
optimizations so that it is as fast to compile as possible, and finally, install
pymavlink.

```
sudo pip3.6 install future Cython numpy pyserial
CFLAGS="-O0" sudo pip3.6 install lxml
sudo pip3.6 install pymavlink
```

## MAVLink proxy

Now that Pymavlink is installed, you might also want to edit Ardusub's Companion
MAVProxy so that any future script you write may talk to the Pixhawk.

1. Go to http://192.168.2.2:2770/mavproxy .

2. Add new inbound connection to the proxy. Pymavlink will then be able to
connect over UDP to the chosen port (9003 in this example) and talk to the board.
Simply append at the bottom of the configuration the following and hit
`Restart MAVlink Proxy`.

        --out udpout:localhost:9003

