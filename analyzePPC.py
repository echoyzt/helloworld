#! /usr/bin/env python
import os,sys
import telnetlib
list_cmds=["1","2","3","4","5","6","7","8"]
def connect_telnet(PPCIP,userName,passwd,finish,COMMAND):
	tn=telnetlib.Telnet(PPCIP,port=23,timeout=10)
	tn.set_debuglevel(5)
	tn.read_until("login: ")
	tn.write(userName+'\n')
	tn.read_until("Password: ")
	tn.write(passwd+'\n')
	for command in COMMAND:
		tn.read_until(finish)
		tn.write(str(command)+'\n')
	tn.write('exit\n')
	print tn.read_all()
	
	
	'''
	while True:
		init()
		tn.read_until(finish)
		input=raw_input('please input:')
		
		if input == "1":
			sys_cmd("i")
		if input == "2":
			sys_cmd("checkStack")
		if input == "3":
			sys_cmd("memShow")
		if input == "4":
			sys_cmd("devs")
		if input == "5":
			sys_cmd("0xe0f30000")
		if input == "6":
			sys_cmd("tt")
		if input == "7":
			addr=input('input the address:')
			sys_cmd("d"+addr)
			sys_cmd("d ")
		if input == "8":
			sys_cmd("pwd")
		if input == "88":
			tn.write("exit\n")
	'''
	tn.write("exit\n")
def log(str1):
	f=open('Executehistory.log','a+')
	f.write(str1+'\n')
	f.close()
def sys_cmd(cmd):
	log(cmd)
	print "cmd:%s"%cmd
	return os.system(cmd)
def init():
	print '********************************************************'
	print '	command list:'
	print '		1.   i'
	print '		2.   checkStack'
	print '		3.   memShow'
	print '		4.   devs'
	print '		5.   0xe0f30000'
	print '		6.   tt'
	print '		7.   d' 
	print '		8.   ls'
	print '*********************************************************'
def package():
	pass
if __name__ == "__main__":
	PPCIP=raw_input('please input PPCIP:')
	userName=raw_input('please input userName:')
	passwd=raw_input('please input passwd:')
	cmd=raw_input("other commamds(split with ','):")
	listcmd=list(cmd.split(','))
	#PPCIP="172.16.42.76"
	#userName="publiccfg"
	#passwd="x86x86"
	finish=" ~]$ "
	print 'PPCIP=%s userName=%s passwd=%s\n'%(PPCIP, userName, passwd)
	init()
	COMMAND=['i','checkStack','memShow','devs','0xe0f30000','tt','d 0xE1000000']
	COMMAND.append(listcmd)
	connect_telnet(PPCIP,userName,passwd,finish,COMMAND)
	
	