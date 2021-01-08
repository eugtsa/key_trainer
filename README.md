# Blind key trainer #

### What is this? ###

This repo contains key trainer program for blind typying, originally created by me (https://github.com/eugtsa) in 2015 (https://habr.com/ru/post/266441/). 

This exact edition has been ported to support python3.

It is currently supports only two layouts - english and russian.

Blind key trainer show active keyboard layout in a separate window. It also display the visual color map for finger positions.

It is Linux only, written in python3 and with help of `xargs`,`xinput`,`xset`,`setxkbmap` linux commands. It has been tested on Ubuntu 14.04 and up to 20.04, Linux Mint 17 Quiana and up to Linux Mint 20 Ulyana MATE 64 and 32 bits editions.

### Installation ####

 `sudo apt-get install python-tk`
 
 `pip install -r requirements.txt`
 
 **Important:** this program is python3 only edition, you can find originale python2 edition here: https://bitbucket.org/alien713cea/key_trainer/src/master/


#### Start and stop ####

To start program run `start.sh` from its local directory 
