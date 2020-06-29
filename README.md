# docker_dedup
deduplication in docker

主要开发分支


centos:
yum install redis
yum install epel-release
yum install epel-release
service redis start
#开机启动
chkconfig redis on

yum install python-devel
yum install openssl
yum install openssl-devel
pip install docopt pyyaml xxhash pyzmq requests cherrypy==17.4.2 redis networkx==2.2 bitarray
pip install contextlib2==0.5.5
pip install more-itertools==5.0.0
pip install PyRabin


安装Cassandra
tar -zxvf jdk-8u221-linux-x64.tar.gz
sudo mv jdk1.8.0_221  /usr/local/jdk1.8
sudo vim /etc/profile
	export JAVA_HOME=/usr/local/jdk1.8
	export JRE_HOME=${JAVA_HOME}/jre
	export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib
	export PATH=.:${JAVA_HOME}/bin:$PATH
source /etc/profile

sudo pip install cassandra-driver


https://www.cnblogs.com/rslai/p/8249812.html

ubuntu:
apt-get install -y software-properties-common
apt-get update && apt-get install -y redis-server
apt-get install openssl
apt-get install libssl-dev
pip install docopt pyyaml xxhash pyzmq requests cherrypy==17.4.2 redis networkx==2.2 bitarray contextlib2==0.5.5 more-itertools==5.0.0 
pip install PyRabin
