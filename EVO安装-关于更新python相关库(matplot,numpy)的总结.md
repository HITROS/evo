# 关于更新python相关库(matplot,numpy)的总结

## 相关配置

ubuntu16.04 

ros kinetic 

内置python2.7 , 3.5版本

## 情况说明

问题一开始在于要安装一个软件只支持较高版本的latplotlib和numpy.

已知ubuntu可以支持多个python版本存在,在我的ubuntu16.04中python2.7作为默认最高优先级的版本.然而现在该版本使用apt-get upgrade 会存在不能更新到最新版本的问题(因为不再支持python2版本)

### 尝试办法1(危险)

通过修改python版本的最高优先级

这个方法非常危险,看过有让卸载python2或者修改版本指针的博客,直接卸载最高优先级的版本会导致ubuntu直接崩溃,如果修改指针则会使其他依赖python的软件无法打开.

这这种情况的根本原因在于/usr/local/python内会存放运行程序的相关文件,直接修改会导致系统无法正常运行.如果你删了.....那基本上要重装.

### 尝试办法2

通过更换软件源

```
sudo pip3 install matplotlib -i https://pypi.douban.com/simple/ 
```

并且写为 matplotlib==版本号 可以控制相关版本