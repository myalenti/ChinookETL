# Intro
This project is aimed solely at allowing for an effective demo of MongoDB.
The specific use case is one of migrating data from a relational DB to MongoDB through various means.
This demo is meant to be run from a docker host where this repo has been cloned at which point you simply need to execute the "launch.sh" script.

## Requirements
1. A docker host running in a Linux VM ( I personally use a CentOS 7 Image) - Do not use the Mac or Windows Dockerhost. There is a problem with the networking where you can only communicate from one container to another and not from the host. This is useless for the demo
2. You will the need a few packages beyond the initial install:
  * The latest Docker Host (`https://docs.docker.com/engine/installation/linux/`)
  * Git client (`sudo yum git install`)
  * Add the EPEL repository (`sudo yum install epel-release`)
  * Install python pip utility (`sudo yum install python2-pip`) 
  * Oracle Java JDK  (`http://www.oracle.com/technetwork/java/javase/downloads/index.html`)
3. After you have installed all the necessary requirements just clone the repo:
  * `git clone https://github.com/myalenti/ChinookETL.git`
