This scipt connects to routers defined in a hosts file and takes incremental backups of the config
while saving also the DIFFS between versions.
As it is now it has very verbose output that can be reduced ofurse. I have it as it is for debug purposes.
Also it very easy to hardcode the hosts file or make it run continuously every hour.

The first time we run the script asks for a file with hostnames or ip addresses on it
then it connects to the routers, create the necessary folder structure for our backups and takes the first backup

```
root@farm:~/python/netbackup# python backup_cisco.py 
	Enter IP addresses file name 
	# non_existent
	There is no such file
	Enter IP addresses file name 
	# hosts
	File successfully loaded
	Successfully created the directory r2
	Successfully created the directory r3
	Successfully created the directory r4
	Connecting to:  r2
	first back up!
	Connecting to:  r3
	first back up!
	Connecting to:  r4
	first back up!
root@farm:~/python/netbackup# 
root@farm:~/python/netbackup# ls
backup_cisco.py  hosts  r2  r3  r4

```
The second time we run the script it connects and checks for any differences in the configs , assuming we made no change this is the output now

```
root@farm:~/python/netbackup# python backup_cisco.py 
	Enter IP addresses file name 
	# hosts
	File successfully loaded
	directory r2 exists!
	directory r3 exists!
	directory r4 exists!
	Connecting to:  r2
	no diffs yet!
	Connecting to:  r3
	no diffs yet!
	Connecting to:  r4
	no diffs yet!
root@farm:~/python/netbackup# 
```

Lets  make some change now in R2

```
root@farm:~/python/netbackup# ssh renos@r2 
Password: 

office-sw>en
Password: 
office-sw#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
office-sw(config)#int loop 22
office-sw(config-if)#ip add 22.22.22.22 255.255.255.255
office-sw(config-if)#description test change!
office-sw(config-if)#end
office-sw#exit
Connection to r2 closed.
root@farm:~/python/netbackup# 

```

Running the script now will print the differences in config , save the new config in a new file , and save also the differences in a separate file

```
root@farm:~/python/netbackup# python backup_cisco.py 
	Enter IP addresses file name 
	# hosts
	File successfully loaded
	directory r2 exists!
	directory r3 exists!
	directory r4 exists!
	Connecting to:  r2
	'-' signal indicates new lines
	'+' signal indicates removed lines
--- 
+++ 
@@ -1,3 +1,4 @@
+
 office-sw>en
 Password: 
 office-sw#term len 0
@@ -5,9 +6,9 @@
 Building configuration...
 
   
-Current configuration : 1676 bytes
+Current configuration : 1587 bytes
 !
-! Last configuration change at 14:32:09 EET Thu Apr 9 2020 by renos
+! Last configuration change at 14:26:06 EET Thu Apr 9 2020 by renos
 !
 version 15.2
 service timestamps debug datetime msec
@@ -76,10 +77,6 @@
 interface Loopback0
  ip address 192.168.50.2 255.255.255.0
 !
-interface Loopback22
- description test change!
- ip address 22.22.22.22 255.255.255.255
-!
 interface Ethernet0/0
  switchport access vlan 100
 !

	Connecting to:  r3
	no diffs yet!
	Connecting to:  r4
	no diffs yet!
root@farm:~/python/netbackup# 

```

Inside folder r2 we now have the new config , and the DIFF file saved

```
root@farm:~/python/netbackup# cd r2
root@farm:~/python/netbackup/r2# ls -hal
total 20K
drwxr-xr-x 2 root root 4.0K Apr  9 15:33 .
drwxr-xr-x 5 root root 4.0K Apr  9 15:27 ..
-rw-r--r-- 1 root root 1.9K Apr  9 15:27 r2_2020-04-09_15:27:10
-rw-r--r-- 1 root root 2.0K Apr  9 15:33 r2_2020-04-09_15:33:38
-rw-r--r-- 1 root root  651 Apr  9 15:33 r2_2020-04-09_15:33:38_DIFF
root@farm:~/python/netbackup/r2# cat r2_2020-04-09_15:33:38_DIFF
--- 
+++ 
@@ -1,3 +1,4 @@
+
 office-sw>en
 Password: 
 office-sw#term len 0
@@ -5,9 +6,9 @@
 Building configuration...
 
   
-Current configuration : 1676 bytes
+Current configuration : 1587 bytes
 !
-! Last configuration change at 14:32:09 EET Thu Apr 9 2020 by renos
+! Last configuration change at 14:26:06 EET Thu Apr 9 2020 by renos
 !
 version 15.2
 service timestamps debug datetime msec
@@ -76,10 +77,6 @@
 interface Loopback0
  ip address 192.168.50.2 255.255.255.0
 !
-interface Loopback22
- description test change!
- ip address 22.22.22.22 255.255.255.255
-!
 interface Ethernet0/0
  switchport access vlan 100
 !
root@farm:~/python/netbackup/r2# 
```
