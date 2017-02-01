# Intro
This project is aimed solely at allowing for an effective demo of MongoDB.
The specific use case is one of migrating data from a relational DB to MongoDB through various means.
This demo is meant to be run from a docker host where this repo has been cloned at which point you simply need to execute the "launch.sh" script.
This demo will launch three containers:
 * One runs MySQL with the Chinook DB loaded into it (https://github.com/lerocha/chinook-database)
 * One runs MongoDB 3.4.1 with no data in it
 * One run the Bi connector

## Requirements
1. A docker host running in a Linux VM ( I personally use a CentOS 7 Image) - Do not use the Mac or Windows Dockerhost. There is a problem with the networking where you can only communicate from one container to another and not from the host. This is useless for the demo
2. You will the need a few packages beyond the initial install:
  * The latest Docker Host (`https://docs.docker.com/engine/installation/linux/`)
  * Git client (`sudo yum git install`)
  * Add the EPEL repository - its needed to install python pip utility (`sudo yum install epel-release`)
  * Install python pip utility (`sudo yum install python2-pip`) 
  * Oracle Java JDK  (`http://www.oracle.com/technetwork/java/javase/downloads/index.html`)
3. After you have installed all the necessary requirements just clone the repo:
  * `git clone https://github.com/myalenti/ChinookETL.git`
4. After cloning give execution rights to both launch.sh and ETLtoMongo.py
 * `chmod 754 launch.sh ETLtoMongo.py`
5. Finally execute launch.sh and follow the on-screen output.

## Customization
The demo environment supports customizations.
You can use external volumes with data in them to load a custom datasetin the MySQL db and the same can be affected with the drdl files.
At this time such instructions need to be added to this Readme.

