# JIRA-Monitoring-script
JIRA的版本bug监测脚本

#### 简介
因为开发解决bug后，JIRA没有通知，导致有时回归不及时，所以写了个脚本，监测到bug单状态改变为已解决时，通过钉钉机器人通知相应的测试人员

##### 使用
如果有其他的需要，可以自己手动改jql，改为自己需要的即可
因为代码有部分涉及到公司内部的信息，所以部分变量已经用部分信息替换，使用时把相关的变量替换成自己的信息即可