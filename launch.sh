#!/usr/bin/sh
#set -x
mysqlPassword='password123'
#lauch Chinook DB and get IP address/port
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=$mysqlPassword -p 3306:3306 myalenti/chinookdemo
mysql=$(docker inspect mysql | python -c "import sys, json; print json.load(sys.stdin)[0]['NetworkSettings']['IPAddress']; exit()")
mysqlPort=3306

#print chinook DB and IP address/port
echo "Chinook ip address is $mysql:$mysqlPort"

#launch Mongo DB and get IP address/port
docker run -d -m 512m --name mongodb -h mongohost -p=27017:27017 myalenti/mongod:3.4
mongoIP=$(docker inspect mongodb | python -c "import sys, json; print json.load(sys.stdin)[0]['NetworkSettings']['IPAddress']; exit()")
mongoPort=27017
#print it
echo "Mongodb ip address is $mongoIP:$mongoPort"

#launch BI and pass MongoDB address port
docker run -it --name bi -d -p=3307:3307 myalenti/bidocker:latest "--mongo-uri=mongodb://$mongoIP:$mongoPort"
biIP=$(docker inspect bi | python -c "import sys, json; print json.load(sys.stdin)[0]['NetworkSettings']['IPAddress']; exit()")
biPort=3307
#print it
echo "BI connector ip is $biIP:$biPort"

read -p "Ready to run ETL... press enter " done
echo "running"
./ETLtoMongo.py --mysqlIP=$mysql --mongoUri=mongodb://$mongoIP:$mongoPort --mysqlPassword=$mysqlPassword

read -p "Press Enter to terminate demo" done
read -p "Just Making sure... Press Enter to terminate demo" done

docker kill mongodb bi mysql
docker rm mongodb bi mysql
