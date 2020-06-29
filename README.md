# docker_dedup
deduplication in docker

cdc测试镜像内冗余数据


centos:
yum install redis
yum install epel-release
yum install epel-release
service redis start
#开机启动
chkconfig redis on

yum install python-devel
pip install docopt pyyaml xxhash pyzmq requests cherrypy redis networkx==2.2 bitarray
pip install contextlib2==0.5.5
pip install more-itertools==5.0.0


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
