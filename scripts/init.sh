#!/bin/bash

#====================Setting directories==========================

if [[ ! -e /ecom/config ]]; then
    mkdir -p /ecom/config
fi

if [[ ! -e /ecom/log ]]; then
    mkdir -p /ecom/log
fi

#=========================Running startup script=================================

echo "export ECOM_IP=$ECOM_IP" >> /etc/profile
source /etc/profile

#============================Configuring IP tables============================================

### ONLY INSERT IF NOT EXIST ###
#=== For localhost allow all =====
if iptables -L -n | grep -q "ACCEPT     all  --  127.0.0.1            0.0.0.0/0"
then
    echo "$rule --> [+] exists..!!"
else
    echo "$rule --> [+] does not exist, Inserting...!!"
    iptables -v -I INPUT -s 127.0.0.1 -j ACCEPT
fi
#===== API TCP 443 from Outside [CentOS/RHEL required] as Default is block all ===
if iptables -L -n | grep -q "ACCEPT     tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:443 ctstate NEW,ESTABLISHED"
then
    echo "$rule --> [+] exists..!!"
else
    echo "$rule --> [+] does not exist, Inserting...!!"
    iptables -I INPUT -p tcp --dport 443 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
fi


#=======================Configuring postgres==================================
cp /usr/ecom-v1/scripts/db_creds.json /ecom/config/db_creds.json

if [[ ! -e /ecom/postgres ]]; then
    mkdir -p /ecom/postgres
    chown -R postgres:postgres /ecom/postgres
    chmod -R 775 /ecom/postgres

    rsync -a /var/lib/postgresql /ecom/postgres
    sed -i "s/data_directory = '\/var\/lib\/postgresql\/12\/main'/data_directory = '\/ecom\/postgres\/postgresql\/12\/main'/g" /etc/postgresql/12/main/postgresql.conf
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost, "$ECOM_IP"'/g" /etc/postgresql/12/main/postgresql.conf
    sed -i "s/max_connections = 100/max_connections = 500/g" /etc/postgresql/12/main/postgresql.conf
    sed -i "s/#deadlock_timeout = 1s/deadlock_timeout = 5s/g" /etc/postgresql/12/main/postgresql.conf

    START_POSTGRES=$(/etc/init.d/postgresql start)
    echo $START_POSTGRES

    CREATE_DB="$(su - postgres -c "psql -U postgres -c \"CREATE DATABASE demo_db;\"")"
    echo $CREATE_DB

    UPDATE_USER="$(su - postgres -c "psql -U postgres -d demo_db -c \"alter user postgres with password 'demo';\"")"
    echo $UPDATE_USER

    sed -i "s/local   all             postgres                                peer/local   all             postgres                                password/g" /etc/postgresql/12/main/pg_hba.conf
    echo "host    all     all             0.0.0.0/0          password" >> /etc/postgresql/12/main/pg_hba.conf
    RESTART_POSTGRES=$(/etc/init.d/postgresql restart)
    echo $RESTART_POSTGRES

    /usr/bin/python3 /usr/ecom-v1/scripts/initialize_tables.py

else
    chown -R postgres:postgres /ecom/postgres
    chmod -R 700 /ecom/postgres/postgresql/12/main
    sed -i "s/data_directory = '\/var\/lib\/postgresql\/12\/main'/data_directory = '\/ecom\/postgres\/postgresql\/12\/main'/g" /etc/postgresql/12/main/postgresql.conf
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost, "$ECOM_IP"'/g" /etc/postgresql/12/main/postgresql.conf
    sed -i "s/max_connections = 100/max_connections = 500/g" /etc/postgresql/12/main/postgresql.conf
    sed -i "s/#deadlock_timeout = 1s/deadlock_timeout = 5s/g" /etc/postgresql/12/main/postgresql.conf
    START_POSTGRES=$(/etc/init.d/postgresql start)
    echo $START_POSTGRES
    sed -i "s/local   all             postgres                                peer/local   all             postgres                                password/g" /etc/postgresql/12/main/pg_hba.conf
    echo "host    all     all             0.0.0.0/0          password" >> /etc/postgresql/12/main/pg_hba.conf
    RESTART_POSTGRES=$(/etc/init.d/postgresql restart)
    echo $RESTART_POSTGRES
fi


#==============================START MESSAGE=======================================
figlet "ECOM > >"
echo "Server is now running..."
echo "To test the API Endpoints using Swagger"
echo "Go to http://127.0.0.1:8086"

supervisord
