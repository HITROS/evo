# 建图精度评估 by EVO

EVO是一个开源的评估SLAM建图精度的软件包

[官方网址](https://github.com/MichaelGrupp/evo/wiki/Formats)

其用来建立对轨迹的评估,从而验证SLAM算法的精度

通常用来评估slam建图中的轨迹误差.

## 支持的数据类型整理

evo支持多种数据包:KITTI,rosbag,Euroc,tum.

### rosbag格式与基本使用命令

存储rosbag

```
rosbag record -O ~/Downloads/cartotest /tf /clock   //-O是指定存储文件名称
roslaunch cartographer_ros demo_backpack_2d.launch bag_filename:=${HOME}/Downloads/b0-2014-07-21-12-42-53.bag
```

### evo-bag信息支持

对于ros_msgs支持以下几个格式的数据

```
geometry_msgs/PoseStamped
geometry_msgs/TransformStamped, geometry_msgs/PoseWithCovarianceStamped
nav_msgs/Odometry
```

另外对于第2,3数据,covariance和twist部分并未在程序中使用,但也支持

在ros环境下查看相应数据的格式

```
rosmsg show message_name ##rosmsg show geometry_msgs/PoseStamped
```

对于bag命令,通常只要包含里程计topic或者其他posestamped即可

### 一个简单例子:

```
rosbag info bagname  //查询rosbag包内的数据类型
//假设存在上述的信息
evo_traj bag room_z_m100.bag --all_topics -p --plot_mode xy //当然mode也可以为xyz
```

### 对于实际SLAM过程

​       对于大多数SLAM建图过程而言,其输出的map frame通常会链接 odom 然后指向机器人的base_link或者base_footprint之类,那么通过对TF数的读取和转换就可以得到其各点的pose.

这个想法在evo的issue里面也有人提到了

[关于TF引用](https://github.com/MichaelGrupp/evo/issues/222)    

这个如果能够引用,那么起码可以提供里程计和tf的两组轨迹进行对比.效果就会较为明显.

要解决tf内信息转换,首先查看TF树与具体坐标变换:

```
rosrun rqt_tf_tree rqt_tf_tree
rosrun tf tf_echo [reference_frame] [target_frame]
rosrun tf tf_echo /robot1/map /robot1/base_footprint  //针对my_package
```

在了解该过程后,就是录制rosbag的过程.

在evo/contrib的目录下有一个 record_tf_as_posestamped_bag.py 脚本,使用方式:在运行slam或者rosbag的情况下

```
./record_tf_as_posestamped_bag.py  --lookup_frequency 15 --output_topic run_1_pose --bagfile run_1.bag map base_link
./record_tf_as_posestamped_bag.py  --lookup_frequency 15 --output_topic odom_to_foot --bagfile 233.bag robot1/map robot1/base_footprint
```

注意事项:  1.保证  use_sim_time = true

​                  2. rosbag play的时候要有 --clock

​                  3.最好打开rviz判断

之后就可以愉快地输出PoseStamped图片了

找一个merge rosbag的[脚本](https://github.com/biomotion/rosbag-operations)

```
./merge_bag.py merge.bag  goodnight.bag 2223_filtered.bag
```

即可得到合并的数据包,从而评价其相对误差之类的.

```
evo_traj bag merge.bag --all_topics -p --plot_mode xy
```

不过还有一点不确定的就是odom在gazebo中是否可以看作groundtruth呢,另外如果是真实场景,那么groundtruth应该如何去测定呢.

## EVO-LOAM

首先LOAM在omtb中运行的时候发布了一些包含位姿的数据

```
/aft_mapped_to_init        nav_msgs/Odometry 
/integrated_to_init        nav_msgs/Odometry
/laser_odom_to_init        nav_msgs/Odometry  
/robot1/odom               nav_msgs/Odometry
/projected_map             nav_msgs/OccupancyGrid
/tf                        tf2_msgs/TFMessage
```

另外loam的tf树也相对不同 reference: loam_map  byLOAM组



## 其他

这一块为目前参考过的一些相关资料,理论上也可以有空根据自己的

### evo的issue中关于loam的一个参考回答

通过kitti数据集转换rostopic为kitti格式的txt文件

[链接](https://github.com/MichaelGrupp/evo/issues/155)

loam官方提供的bag里面只有laser msg,故实际测试需要自己在gazebo中测试.

另外提一句,loam论文里面精度是根据对比gps和

### 关于两组数据时间不同步的问题

通过sim_time解决timestamp不同步问题

[链接](https://github.com/MichaelGrupp/evo/issues/243)

### 关于一个依赖geometry_msg的package的编写过程参考

[链接](https://www.jianshu.com/p/5c75c24f0fe6)

### 不同依赖数据格式的详细内容,包含转换

[链接](https://github.com/MichaelGrupp/evo/wiki/Formats#kitti---kitti-dataset-pose-format)

### 在gazebo中发布groundtruth的pose

由于不清楚odom和里程计的具体差别(gazebo中是否打滑),所以暂时没有测试

[链接](https://blog.csdn.net/osgoodwu/article/details/85072122)

### 通过gazebo中set_model_state/get_model_state获取模型状态(可能有用)

[链接](https://blog.csdn.net/lxlong89940101/article/details/100132221)