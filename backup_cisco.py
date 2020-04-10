import threading
import paramiko
import subprocess
import getpass
import sys
import time
import glob
import os
import getopt
import socket
import difflib
from datetime import datetime
from sys import argv
import argparse

global ips
global cmds
prompt = '\t# '


global username
global production_password
global secret
username = "renos"
production_password = "cisco"
secret= "cisco"

def get_ip_addresses_file():
	global ips
	try:
		print "\tEnter IP addresses file name "
		ips = raw_input(prompt)
		f = open(ips,'r')
	except IOError:
		print "\tThere is no such file"
		get_ip_addresses_file()
	else:
		print "\tFile successfully loaded"
		f.close()
		#pause()

def make_dir(file):
        path = os.path.join(file)

        try:
                os.makedirs(path)
        except OSError:
                print ("\tdirectory %s exists!" % path)
        else:
                print ("\tSuccessfully created the directory %s" % path)


def create_file_name():
	global path
	global filename
	global filename_diffs
	###prefix files for backup
        path = (os.getcwd() + '/' + ip + '/' )
	os.chdir(path)
        time_now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        filename = ip + "_" + time_now
	filename_diffs = ip + "_" + time_now + "_DIFF"

def check_folders():
	get_ip_addresses_file()
	f = open(ips,'r')
	for ip in f.readlines():
		ip = ip.strip('\n')
		make_dir(ip)

def ssh_connect(ip):
	global output
	global shell
	try:
		print ("\tConnecting to: ") , ip
        	ssh_client = paramiko.SSHClient()
        	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        	ssh_client.connect(ip, username=username, password=production_password, allow_agent=False, look_for_keys=False)
        	shell = ssh_client.invoke_shell(height=1240)
        	time.sleep(1)
        	shell.send('en\n')
        	time.sleep(1)
        	shell.send(secret)
        	time.sleep(1)
        	shell.send('\n')
        	time.sleep(1)
        	###terminal length for no paging
        	shell.send('term len 0\n')
        	time.sleep(1)
        	###show config and write output
        	shell.send('sh run\n')
        	time.sleep(5)
        	output = shell.recv(999999)
	except paramiko.SSHException:
                print '\tAuthenctication Failure'
        except socket.error:
                print '\tUnable to connect to: ', ip


def find_diffs():
	global list_of_files
	global files
	###check files that exist in directory
	list_of_files = glob.glob(path + "/*[!DIFF]")
	files = sorted(list_of_files, key=os.path.getmtime) 
	if len(files) == 1:
		print("\tfirst back up!")
		shell.close
	#compare files
	else:
		newest_config = files[-1]
		previous_config = files[-2]
		f1 = open(newest_config).readlines()
		f2 = open(previous_config).readlines()

		output1 = ''
		for line in difflib.unified_diff(f1, f2):
			output1 +=line
		if output1 == '':
			print('\tno diffs yet!')
			shell.close()
			#no diffs with previous config we can remote that one
			os.remove(newest_config)
		else:
			print("\t'-' signal indicates new lines")
			print("\t'+' signal indicates removed lines")
			print(output1)
			#save diffs in file
			ff = open(filename_diffs, 'a')
		        ff.write(output1.decode("utf-8") )
        		ff.close()
			shell.close()

check_folders()
f = open(ips,'r')
for ip in f.readlines():
	ip = ip.strip('\n')
	###prefix files for backup
	create_file_name()
	os.chdir(path)
	###session start
	ssh_connect(ip)
	###write current conf in file 
	ff = open(filename, 'a')
	ff.write(output.decode("utf-8") )
	ff.close()
	###check for diffs
	find_diffs()
	path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)

f.close()

