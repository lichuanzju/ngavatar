#!/bin/bash

# Check whether this script is run as root
if [ `id -u` != "0" ]
then
    echo "Error: Please run this script as root!"
    exit 1
fi

# Usage string
usage="\
Usage:  install.sh [-d root_dir [-l port] [-c config_file] [-H mysql_host]
            [-P mysql_port] [-p mysql_root_passwd]]
options:
  -d    Root directory of this website where All files will be copied to.
  -l    Listening port of this website. Default value is 80.
  -c    Name of the Apache2 site config file, which goes to /etc/apache2/
        sites-enabled/. Default value is \"ngavatar.conf\".
  -H    Host name of MySQL server. Default value is \"localhost\".
  -P    Port of MySQL server. Default value is 3306.
  -p    Password of MySQL root user. Default value is empty.
  -h    Show the help message.

If no options are given, this script will run in interactive mode in which the
user can input these parameters in tty.
There will be no automatic cleaning procedure if something goes wrong in the
middle of the installing process. For manual cleaning instructions please
refer to the README file."

# Get options
interactive=1
while getopts 'd:l:c:H:P:p:h' option
do
    case "$option"
    in
        d)  root_dir=$OPTARG
            interactive=0;;
        l)  port=$OPTARG
            interactive=0;;
        c)  config_file=$OPTARG
            interactive=0;;
        H)  mysql_host=$OPTARG
            interactive=0;;
        P)  mysql_port=$OPTARG
            interactive=0;;
        p)  mysql_passwd=$OPTARG
            interactive=0;;
        h)  echo "$usage"
            exit 0;;
        \?) echo "$usage"
            exit 2;;
    esac
done

# Enter interactive mode if no valid options are given
if [ "$interactive" -eq 1 ]
then
    echo "Please input the following parameters:"
    read -p "Root directory of the site: " root_dir
    read -p "Listening port: " port
    read -p "Apache2 config file name: " config_file
    read -p "Host name of MySQL server: " mysql_host
    read -p "Port of MySQL server: " mysql_port
    read -p "Root password of MYSQL server: " -s mysql_passwd
    echo
fi

# Root directory cannot be empty
if [ -z "$root_dir" ]
then
    echo "Error: root directory of the site cannot be empty."
    exit 2
fi

# Set default values
port=${port:-80}
config_file=${config_file:-ngavatar.conf}
mysql_host=${mysql_host:-localhost}
mysql_port=${mysql_port:-3306}

config_file="/etc/apache2/sites-enabled/$config_file"
root_dir=`readlink -f $root_dir`

# Verify the root directory
[ -d "$root_dir" ] || { echo "Error: $root_dir is not a directory.";exit 2; }

# Check whether the config file already exists
[ -e "$config_file" ] && { echo "Error: $config_file already exists.";exit 2; }

# Verify the listening port
[ "$port" -eq "$port" ] 2>/dev/null || { echo "Error: invalid listening port number $port";exit 2; }

# Verigy the MySQL port
[ "$mysql_port" -eq "$mysql_port" ] 2>/dev/null || { echo "Error: invalid MySQL port number $mysql_port"; exit 2; }


# Copy all files to root directory
echo "Copying files to root directory..."
cp -rp ../src/* $root_dir || exit 3

# Creating pth file
echo "Creating .pth file in python2.7 dist-packages..."
echo "$root_dir/scripts/libs" > /usr/local/lib/python2.7/dist-packages/ngavatar.pth

# Initialize database
echo "Initializing MySQL database..."
mysql -h $mysql_host -P $mysql_port -u root --password="$mysql_passwd" <../src/scripts/sql/create_database.sql || exit 4

# Create apache2 site config file and add listening port
echo "Creating apache2 config file..."
root_dir_t=$(echo $root_dir | sed -e 's/\//\\\//g')
sed -e "s/DOC_ROOT/$root_dir_t/g" -e "s/SITE_PORT/$port/g" \
    ngavatar.conf > $config_file || exit 5
echo "Listen $port" >> /etc/apache2/ports.conf

# Restart apache2 server
echo "Restarting apache2 server..."
service apache2 restart || exit 6

echo "Done."
echo "Please visit http://localhost:$port/ to verify."
