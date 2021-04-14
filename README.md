# docker_dedup
deduplication in docker

**该分支特性：**
1. 加入了overlap的实验
2. 加入了并行拉取镜像层的锁（每次pull只拉取1个layer）

**依赖：**
1. 本地docker私有registry
2. dragonfly（只用到了dfdaemon的proxy功能）https://github.com/zhang2639/Dragonfly


**使用方法：**
1. 启动该项目，一共两个模块，先启动net模块，在启动storage模块，并配置服务地址在yaml里面的ws_address_connect
2. 在host上面拉起一个registry镜像，将镜像仓库的存储目录挂载到本地，修改docker的源码（push未经压缩的镜像层，未压缩的镜像才有去重空间），把镜像push到仓库里面，去本地仓库目录里面把所有layer存储到storage模块（redis数据库），使用python api.py add file 去重处理layer
3. 此时镜像已经被去重以block的方式存储到数据库，数据库存储了数据块的key-value、layer的key（镜像层sha256，方便docker pull索引layer）-value（layer里面所有数据块的key）
4. 启动dragonfaly的dfdaemon，配置docs/config/dfdaemon_config_template.yml的registry_mirror里面的remote为私有仓库的ip，配置supernodes为该项目的ws_address_connect地址（在dragonfly里面配置）
5. 配置docker的registry-mirrors为 http://127.0.0.1:65001
6. docker pull http://127.0.0.1:65001/imagexxx

**ip之间的关系**
1. 该项目有一个服务ip，根据该ip去去重、重构镜像；
2. 私有镜像仓库有一个服务ip；
3. dfdaemon配置前面的两个ip，并且把http://127.0.0.1:65001 配置成docker的registry_mirror ip；
4. docker pull http://127.0.0.1:65001/imagexxx 时，dfdaemon截获到这个请求，发给私有仓库，获取私有仓库里面关于该镜像manifest，从里面获取到所需的layer，然后向该项目的服务ip发送重构该layer的请求。获取到所有layer之后，dfdaemon将layer传给docker，docker重构出镜像


**一些增强的建议**
1. 该项目是单线程拉取，所以pull镜像只能一层一层的来，改成多线程符合现在docker pull镜像的流程
2. dfdaemon将layer重构出来，然后docker会在把该layer读到内存里面，这中间会有一个等待时间（等待时间约等于最后1层layer的重构时间），``边重构边读，或者直接将镜像重构到docker读取镜像的一个cache里面可以进一步优化pull时间``。我做实验的时候，只是把重构的layer放到了内存文件系统里面，读layer的时候相当于从内存读到内存
3. python效率很低，用go重写效果也会更好
4. 使用的cdc算法效果很差，可以自己实现论文上面的高效率cdc算法
5. 论文方面，可以根据镜像的类型缩小数据查找范围，加速数据块的查找。这样的话使用数据库（redis）效果不太好，可以自己实现一个存储索引数据块的部分


**相关的配置参数配置方法**
![image](https://user-images.githubusercontent.com/20706317/114715172-5fd53c80-9d65-11eb-9676-b90a2fb2a79b.png)
https://github.com/DarLiner/Dragonfly/blob/master/docs/en/usage.md



**原始项目论文，里面包含最初版本的配置使用说明**
Nitro: Network-Aware Virtual Machine Image Management in Geo-Distributed Clouds.

**安装方式：**

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
