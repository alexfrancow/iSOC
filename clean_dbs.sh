# Script to remove all persistent data of the containers.

read -p 'Are you sure [y/N]? ' sure
if [ $sure = 'y' -o $sure = 'Y' ]
	then
	echo 'Removing DBs..'
	rm -rf volumes/openvas/*
	rm -rf volumes/zabbix/mysql/*
	rm -rf volumes/elk-data/nodes/*
	rm -rf volumes/mongodb/data
fi
