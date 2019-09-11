#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,pexpect
import telnetlib
import xml.dom.minidom
from PyQt4.QtCore import *
from PyQt4.QtGui import *
FINISH="->"
passwd="root"
PPCcmdList=["i\n","memShow\n","iosFdShow\n"]
localcmdlist=["ss_start",
	"cp homedir+'/data/process/trace/defaultTR.log  ./MonitorLog",
	"cp homedir+'/data/process/error/EH_exception_log  ./MonitorLog",
	"cp homedir+'/data/process/error/logging.dat  ./MonitorLog",
	"cp -r homedir+'/log/OI  ./MonitorLog",
	"cp /var/log/messages ./MonitorLog",
	"top -u USERNAME -bn 1"]
taskNameList=[]
ppcList=[]
homedir=os.environ['HOME']
curDir=os.getcwd()
commandCfg=curDir+'/command.cfg'
print ' homedir=%s\n curDir=%s\n commandCfg=%s\n' %(homedir,curDir,commandCfg)

def PingPPC(hostip):
	pinginfo = os.system("ping -n 2 -w 1 %s" %hostip)
	if pinginfo:
		print "%s lost cannot connect" %(hostip)
		return -1
	return 0
	
class MainWindow(QMainWindow):
	def __init__(self,parent=None):
		super(MainWindow,self).__init__(parent)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.centralwidget = QWidget(self)
		self.output_group = QGroupBox(self.centralwidget)
		self.output_group.setTitle("Out Put")
		self.browser_show=QTextBrowser();
		
		self.local_group = QGroupBox(self.centralwidget)
		self.otherShell_qlw=QListWidget()
		self.otherShell_qlw.setMovement(QListWidget.Static)
		#self.otherShell_qlw.setMovement(QListWidget.Free)
		#self.otherShell_qlw.setMovement(QListWidget.Snap)
		self.otherShell_qlw.setDragEnabled(True)
		self.otherShell_qlw.setSelectionMode(QAbstractItemView.MultiSelection)
		
		self.ppcip_qcb=QComboBox()
		self.otherShell_qle=QLineEdit()
		#self.otherShell_qle.setPlaceholderText("input shell command here:")
		self.pushButtonAdd=QPushButton("Add Command")
		self.pushButtonDel=QPushButton("Delete Command")
		self.pushButton2=QPushButton("Run")
	
		
		grid=QGridLayout()
		VlayoutBrowser=QVBoxLayout()
		VlayoutBrowser.addWidget(self.browser_show)
		self.output_group.setLayout(VlayoutBrowser)
		
		VlayoutRight=QVBoxLayout()
		VlayoutRight.addWidget(self.otherShell_qlw)
		VlayoutRight.addWidget(self.ppcip_qcb)
		VlayoutRight.addWidget(self.otherShell_qle)
		
		hlayout=QHBoxLayout()
		hlayout.addWidget(self.pushButtonAdd)
		hlayout.addWidget(self.pushButtonDel)
		VlayoutRight.addLayout(hlayout)
		VlayoutRight.addWidget(self.pushButton2)
		
		self.local_group.setLayout(VlayoutRight)
		
		grid.addWidget(self.output_group,0,0,2,1)
		grid.addWidget(self.local_group,0,1,2,1)
		self.centralwidget.setLayout(grid)
		self.setCentralWidget(self.centralwidget)
		self.readcmdFile(commandCfg)
		self.parseIPlist()
		
		if not os.path.exists('./MonitorLog'):
			os.mkdir('./MonitorLog')
		else:pass 
		print '=====current dir=%s' %os.getcwd()

		self.connect(self.pushButton2,SIGNAL("clicked()"),self.ExecuteShell)
		self.connect(self.pushButtonAdd,SIGNAL("clicked()"),self.AddShellCmd)
		self.connect(self.pushButtonDel,SIGNAL("clicked()"),self.DelShellCmd)
	
	def AddShellCmd(self):
		cmdstr=self.otherShell_qle.text()
		self.otherShell_qlw.addItem(cmdstr)
		self.otherShell_qlw.setSortingEnabled(True)
		try:
			fd=open(commandCfg,'a+')
			fd.write(cmdstr+'\n')
			fd.close()
		except IOError:
			self.browser_show.append('shell command file open failed!')
			
	def DelShellCmd(self):
		#self.otherShell_qlw.selectedItems()
		self.otherShell_qlw.removeItemWidget(self.otherShell_qlw.currentItem())
		
	def ExecuteShell(self):
		for ppc_ip in ppcList:
			#PPC可达
			iResult=PingPPC(ppc_ip)
			if iResult==0:
				self.browser_show.append('=====connecting to '+ppc_ip+'...')
				tcn=telnetlib.Telnet(ppc_ip)
				resultFile=curDir+'/MonitorLog/'+ppc_ip+'log.txt'
				try:
					f=open(resultFile,'a+')
					f.write("===============================PPC Log start================================\n")
				except IOError:
					self.browser_show.append(resultFile+'file open failed!')
					f.write(resultFile+'file open failed!')
				try:
					tcn.read_until(FINISH)
					for shellcmd in PPCcmdList:
						self.PPC_cmd(FINISH,tcn,shellcmd,f)
					f.close()
					tcn.close()
				except EOFError:
					self.browser_show.append('Error Connect '+ppc_ip+' Failed. Try Again.')
					f.write('=====Error Connect '+ppc_ip+' Failed. Try Again.')
		self.localshell()
		
	def localshell(self):
		print 'run localshell'
		for cmdstr in localcmdlist:
			if cmdstr == 'ss_start':
				os.chdir(homedir+'/SMEE')
				self.browser_show.append('run  '+cmdstr)
				os.system('echo ==========================run '+cmdstr +'>>'+curDir+'/MonitorLog/systemlog.txt')
				os.system(unicode(cmdstr) +'>>'+curDir+'/MonitorLog/systemlog.txt')
				os.system(unicode(cmdstr) +'>>'+curDir+'/tf_ssstart.txt')
				try:
					taskIDlist=[]
					tf=open(curDir+'/tf_ssstart.txt','r')
					next(tf)
					for linestr in tf:
						line = linestr.rstrip('\n')
						if not line:break
						if line:
							tmp_list = line.split()
							taskIDlist.append(tmp_list[0]+','+tmp_list[4])
					print "=====" %(taskIDlist)
					if 0 != len(taskIDlist):
						for taskitem in taskIDlist:
							taskid=taskitem.split(',')
							self.browser_show.append("pstack "+taskid[0]+"----->"+taskid[1]+"\n")
							os.system('echo =====pstack '+taskid[0] +'----->'+taskid[1]+' >>'+curDir+'/MonitorLog/'+taskid[1]+'.txt')
							os.system('pstack '+taskid[0] +' >>'+curDir+'/MonitorLog/'+taskid[1]+'.txt')
						tf.close()
						os.remove(curDir+'/tf_ssstart.txt')
						print 'remove tf_ssstart'
				except IOError:
					self.browser_show.append('tf_ssstart.txt open failed!')
					
			elif cmdstr == 'cp '+homedir+'/SMEE/data/process/trace/defaultTR.log  ./MonitorLog':
				os.system(unicode(cmdstr))
			elif cmdstr == 'cp '+homedir+'/SMEE/data/process/error/EH_exception_log  ./MonitorLog':
				os.system(unicode(cmdstr))
			elif cmdstr == 'cp '+homedir+'/SMEE/data/process/error/logging.dat  ./MonitorLog':
				os.system(unicode(cmdstr))
			elif cmdstr == 'cp -r '+homedir+'/SMEE/log/OI  ./MonitorLog':
				os.system(unicode(cmdstr))
			elif cmdstr == 'cp /var/log/messages ./MonitorLog':
				print 'homedir=%s'  %homedir
				cmdstr1='cp /var/log/messages '+  curDir+'/MonitorLog'
				USERNAME=homedir.split('/')[-1]
				psuper=pexpect.spawn('su')
				psuper.expect('Password:')
				psuper.sendline(unicode(passwd))
				psuper.expect('')
				psuper.sendline(cmdstr1)
				psuper.expect('')
				psuper.sendline('chmod -R 777 '+ curDir+'/MonitorLog/messages')
				psuper.expect('')
				psuper.sendline('chown -R '+USERNAME+':smee '+curDir+'/MonitorLog/messages')
				psuper.expect('')
				psuper.sendcontrol('d')
			elif cmdstr == 'top -u USERNAME -bn 1':
				USERNAME=homedir.split('/')[-1]
				os.system('echo ================\n ')
				cmdstr='top -u '+USERNAME +' -bn 1 >>'+curDir+'/MonitorLog/systemlog.txt'
				print cmdstr
				os.system(cmdstr)
			else:
				self.browser_show.append('NO stcmd string Match!')
				
				
	def readcmdFile(self,commandCfg):
		try:
			fd=open(commandCfg,'r')
			next(fd)
			for shellcmd in fd:
				line = shellcmd.rstrip('\n')
				if not line:break
				item=QListWidgetItem(self.otherShell_qlw)
				item.setText(line)
			fd.close()
			self.otherShell_qlw.setSortingEnabled(True)
		except IOError:
			self.browser_show.append('shell command file open failed!')
	def parseIPlist(self):
		
		DOMTree = xml.dom.minidom.parse(homedir+'/SMEE/SM/SM_HOST_LIST')
		IPInfo = DOMTree.documentElement
		configures=IPInfo.getElementsByTagName("configure")
		for conf in configures:
			stationstr=conf.getElementsByTagName("station")[0].childNodes[0].data
			#print 'stationstr=%s' %stationstr
			if stationstr != "LINUX" and stationstr != "SUN":
			    ipstr = (conf.getElementsByTagName("IP")[0]).childNodes[0].data
			    #print 'ipstr=%s' %ipstr
			    ppcList.append(ipstr)
			    self.ppcip_qcb.addItem(ipstr)
			
	def parseCmd(self,tf,taskNameList):
		try:
			next(tf)
			next(tf)
			next(tf)
			next(tf)
			for linestr in tf:
				line = linestr.rstrip('\n')
				if not line:break
				if line:
					tmp_list = line.split()
					if tmp_list[0][:5].isupper():
						taskNameList.append(tmp_list[0])
		except IOError:
			self.browser_show.append('read shell \"i\" Information Error!')
	def PPC_cmd(self,FINISH,tcn,shellcmd,f):
		if shellcmd =="i\n":
			self.browser_show.append('=====run  '+ shellcmd)
			f.write('============================run '+shellcmd+'\n')
			tfile=curDir+'/tilog.txt'
			print 'tfile=%s' %(tfile)
			try:
				tf=open(tfile,'w')
			except IOError:
				self.browser_show.append(tfile+"write mode open failed!")
			tcn.write(shellcmd)
			f.write(tcn.read_until(FINISH))
			
			tcn.write(shellcmd)
			tf.write(tcn.read_until(FINISH))
			tf.close()
			try:
				tf=open(tfile,'r')
			except IOError:
				self.browser_show.append(tfile+"read mode open failed!")
			self.parseCmd(tf,taskNameList)
			if 0 != len(taskNameList):
				for taskName in taskNameList:
					self.browser_show.append("tt "+taskName+"\n")
					tcn.write("tt "+taskName+"\n")
					f.write('============================tt '+taskName+'=========================\n')
					f.write(tcn.read_until(FINISH))
			tf.close()
			os.remove(tfile)
			print 'run remove tilog'
		else:
			self.browser_show.append(shellcmd)
			tcn.write(shellcmd)
			f.write('============================'+shellcmd+'=========================\n')
			f.write(tcn.read_until(FINISH))

			
if __name__ == '__main__':
	app = QApplication(sys.argv)
	widget = MainWindow()
	widget.resize(800,600) #kuang,gao
	widget.setWindowTitle("Info Collect")
	widget.show()
	sys.exit(app.exec_())