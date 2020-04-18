read -p 'Are you sure [y/N]? ' sure

if [ $sure = 'y' -o $sure = 'Y' ]
	then
	echo 'Removing DBs..'
	rm -rf volumes/openvas/*
	rm -rf volumes/zabbix/mysql/*
	rm -rf volumes/elk-data/nodes/*
fi
