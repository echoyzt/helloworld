# ——*—— coding: UTF-8 _*_
import sys,os,pexpect
import telnetlib
from datetime import datetime
import xml.dom.minidom
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#返回最近文件修改时间
#os.path.getmtime(path) 
FINISH="->"
passwd="root"
PPCcmdList=["i","checkStack","memShow","0xe0f30000","iosFdShow","devs"]
d=datetime.today()
date=d.strftime('%Y%m%d')
#date='20180927'
EH_TR_FILES_MAX=10
#datelong=d.strftime('%Y%m%d%H%M%S')

taskNameList=[]
ppcList=[]
homedir=os.environ['HOME']
curDir=os.getcwd()
commandCfg=curDir+'/command.cfg'
print ' homedir=%s\n curDir=%s\n commandCfg=%s\n' %(homedir,curDir,commandCfg)
print ' date=%s\n' %date

#ss_start 必须是第一条命令,有切换目录操作
localcmdlist=["ss_start",
	"/SMEE/data/process/trace/defaultTR.log",
	"/SMEE/data/process/error/EH_exception_log",
	"/SMEE/data/process/error/logging.dat",
	"/SMEE/data/process/",
	"/SMEE/log/OI",
	"/SMEE/data/process/log/OI  ./MonitorLog",
	"/var/log/messages",
	"top -u USERNAME -bn 1"]
	
	
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
		
		print '=====current dir=%s' %os.getcwd()

		self.connect(self.pushButton2,SIGNAL("clicked()"),self.ExecuteShell)
		self.connect(self.pushButtonAdd,SIGNAL("clicked()"),self.AddShellCmd)
		self.connect(self.pushButtonDel,SIGNAL("clicked()"),self.DelShellCmd)
	
	def PingPPC(self,hostip):
		pinginfo = os.system("ping -c 1 -w 1 %s" %hostip)
		if pinginfo:
			print "%s lost, cannot connect" %(hostip)
			self.browser_show.append('Error Connect '+hostip+' Failed. Try Again.')
			return -1
		return 0
	
	def AddShellCmd(self):
		strip=self.ppcip_qcb.currentText()
		
		cmdstr=unicode(strip)+',    '+self.otherShell_qle.text()
		self.otherShell_qlw.addItem(cmdstr)
		self.otherShell_qlw.setSortingEnabled(True)
		try:
			fd=open(commandCfg,'a+')
			fd.write(cmdstr+'\n')
			fd.close()
		except IOError:
			self.browser_show.append('shell command file open failed!')
			
	def DelShellCmd(self):
		#Items=(self.otherShell_qlw.selectedItems()).currentRow()
		#print Items
		item_del=self.otherShell_qlw.takeItem(self.otherShell_qlw.currentRow())
		item_del=None
		
		#Items=self.otherShell_qlw.selectAll()
		textItems=[]
		for index in range(self.otherShell_qlw.count()):
			textItems.append((unicode(self.otherShell_qlw.item(index).text())))
		try:
			fd=open(commandCfg,'w')
			fd.write('IP						CMD'+'\n')
			for item in textItems:
				fd.write(item+'\n')
			fd.close()
		except IOError:
			self.browser_show.append('shell command file open failed!')
	def ExecuteShell(self):
		if not os.path.exists(curDir+'/MonitorLog'):
			os.mkdir(curDir+'/MonitorLog')
			os.mkdir(curDir+'/MonitorLog/'+date)
			os.mkdir(curDir+'/MonitorLog/pstack')
			
		else:pass 
		#Items=self.otherShell_qlw.selectAll()
		textItems=[]
		for index in range(self.otherShell_qlw.count()):
			textItems.append((unicode(self.otherShell_qlw.item(index).text()).strip()).split(','))
		
		#print 'textItems=' 
		#print textItems
		for ppc_ip in ppcList:
			resultFile=curDir+'/MonitorLog/'+ppc_ip+'.txt'
			iResult=self.PingPPC(ppc_ip)
			if iResult==0:
				tcn=telnetlib.Telnet(ppc_ip)
				print '=====connecting to '+ppc_ip+'...'
				try:
					f=open(resultFile,'w')
					f.write("===============================PPC Log start================================\n")
					tcn.read_until(FINISH)
					print '=====collect infomation from PPC ...'+ppc_ip
					for shellcmd in PPCcmdList:
						self.PPC_cmd(FINISH,tcn,shellcmd,ppc_ip,f)
					print '=====collect infomation form PPC '+ppc_ip+' finish...'
					if 0 != len(textItems):
						for index in range(len(textItems)):
							if unicode(ppc_ip) == unicode(textItems[index][0]):
								othercmd=textItems[index][1]
								#print "othercmd=%s" %othercmd
								self.browser_show.append(ppc_ip +' '+str(othercmd))
								tcn.write(str(othercmd)+"\n")
								f.write('============================' +str(othercmd)+'=========================\n')
								f.write(tcn.read_until(FINISH))
					
					tcn.close()
				except IOError:
					print resultFile+' file open failed!'
				except EOFError:
					print '=====%s ' %EOFError
					f.close()
					print '=====Error Connect '+ppc_ip+' Failed. Try Again.'
					os.system('echo "Error Connect '+ppc_ip+' Failed. Try Again." > '+curDir+'/MonitorLog/'+ppc_ip+'.txt')
				except Exception , e:
					print e+'\n'
					f.close()
				finally:
					f.close()
			else:
				print '=====ping '+ppc_ip+ 'failed!!!'
				try:
					f=open(resultFile,'w')
					f.write("===============================PPC Log start================================\n")
					f.write('Error Connect '+ppc_ip+' Failed. Try Again')
					f.close()
				except IOError:
					print resultFile+'file open failed!'
					
					
		self.localshell()
		self.package()
		self.gui_close()
		
	def localshell(self):
		print '=====collect infomation from local computer...'
		for cmdstr1 in localcmdlist:
			if cmdstr1 == 'ss_start':
				USER=homedir.split('/')[-1]
				cmdstr='ps -u '+USER+' -o pid,tty,s,time,fname'
				os.chdir(homedir+'/SMEE')
				self.browser_show.append('run  '+cmdstr)
				os.system('echo ==========================run '+cmdstr +'>>'+curDir+'/MonitorLog/systemlog.txt')
				os.system(unicode(cmdstr) +'>>'+curDir+'/MonitorLog/systemlog.txt')
				os.system(unicode(cmdstr) +'>'+curDir+'/tf_ssstart.txt')
				try:
					pstackIDlist=[]
					tf=open(curDir+'/tf_ssstart.txt','r')
					
					next(tf)
					for linestr in tf:
						line = linestr.rstrip('\n')
						if not line:break
						if line:
							tmp_list = line.split()
							pstackIDlist.append(tmp_list[0]+','+tmp_list[4])
					#print "pstackIDlist====="
					#print  pstackIDlist
					if 0 != len(pstackIDlist):
						for taskitem in pstackIDlist:
							taskid=taskitem.split(',')
							if taskid[1][:5].isupper():
								self.browser_show.append("pstack "+taskid[0]+"----->"+taskid[1]+"\n")
								os.system('echo =====pstack '+taskid[0] +'-----'+taskid[1]+' >'+curDir+'/MonitorLog/pstack/'+taskid[1]+'.txt')
								os.system('pstack '+taskid[0] +' >>'+curDir+'/MonitorLog/pstack/'+taskid[1]+'.txt')
						tf.close()
						os.remove(curDir+'/tf_ssstart.txt')
				except IOError:
					self.browser_show.append('tf_ssstart.txt open failed!')
				os.chdir(curDir)
			elif cmdstr1=='/SMEE/data/process/trace/defaultTR.log':
				cmdstr = 'cp '+homedir+'/SMEE/data/process/trace/defaultTR.log  ./MonitorLog'
				os.system(unicode(cmdstr))
			elif cmdstr1=='/SMEE/data/process/error/EH_exception_log':
				cmdstr = 'cp '+homedir+'/SMEE/data/process/error/EH_exception_log  ./MonitorLog'
				os.system(unicode(cmdstr))
			elif cmdstr1=='/SMEE/data/process/error/logging.dat':
				cmdstr = 'cp '+homedir+'/SMEE/data/process/error/logging.dat  ./MonitorLog'
				os.system(unicode(cmdstr))
			elif cmdstr1=="/SMEE/data/process/":
				dir1=homedir+'/SMEE/data/process'
				os.chdir(dir1)
				num=0
				if os.path.exists(dir1+'/trace/'+date):
					for list in os.listdir(dir1+'/trace/'+date):
						if '.gz' == os.path.splitext(list)[1]:
							num +=1
					print 'trace file num=%s'  %num
					if num < EH_TR_FILES_MAX:
						cmdstr='cp -r  '+dir1+'/trace/'+date+ ' '+curDir+'/MonitorLog'
						os.system(unicode(cmdstr))
					else:
						tlistTime=[]
						for list in os.listdir(dir1+'/trace/'+date):
							tlistTime.append(list[8:-7])
							
						tlistTime.sort(reverse=True)
						#print 'trace tlistTime=====\n'
						#print tlistTime
						for i in range(EH_TR_FILES_MAX):
							#print tlistTime[i]
							cmdstr='cp -f '+dir1+'/trace/'+date+ '/ADAE_TR_'+tlistTime[i]+'.log.gz' +' '+curDir+'/MonitorLog/'+date
							os.system(unicode(cmdstr))
				else:
					print "dir "+dir1+'/trace/'+date+" not exist."
				num=0
				if os.path.exists(dir1+'/error/'+date):
					for list in os.listdir(dir1+'/error/'+date):
						if '.gz' == os.path.splitext(list)[1]:
							num +=1
					print 'error file num=%s'  %num
					if num < EH_TR_FILES_MAX:
						cmdstr='cp -r '+dir1+'/error/'+date+ ' '+curDir+'/MonitorLog'
						os.system(unicode(cmdstr))
					else:
						tlistTime=[]
						for list in os.listdir(dir1+'/error/'+date):
							tlistTime.append(list[8:-7])
							
						tlistTime.sort(reverse=True)
						#print 'error tlistTime=====\n'
						#print tlistTime
						for i in range(EH_TR_FILES_MAX):
							#print tlistTime[i]
							cmdstr='cp -f '+dir1+'/error/'+date+ '/ADAE_EH_'+tlistTime[i]+'.log.gz' +' '+curDir+'/MonitorLog/'+date
							os.system(unicode(cmdstr))
				else:
					print "dir "+dir1+'/error/'+date+" not exist."
				
				os.chdir(curDir)
				
			elif cmdstr1=='/SMEE/log/OI':
				cmdstr = 'cp -r '+homedir+'/SMEE/log/OI  ./MonitorLog'
				os.system(unicode(cmdstr))
			elif cmdstr1=='/SMEE/data/process/log/OI  ./MonitorLog':
				cmdstr='cp -r '+homedir+'/SMEE/data/process/log/OI/*  ./MonitorLog/OI'
				if os.path.isdir(curDir+'/MonitorLog/OI'):
					os.system(cmdstr)
				else:
					os.mkdir(curDir+'/MonitorLog/OI')
					os.system(cmdstr)
			elif cmdstr1=='/var/log/messages':
				cmdstr = 'cp /var/log/messages ./MonitorLog'
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
			elif cmdstr1=='top -u USERNAME -bn 1':
				cmdstr = 'top -u USERNAME -bn 1'
				USERNAME=homedir.split('/')[-1]
				os.system('echo ===============================top -u '+USERNAME +' -bn 1 >>'+curDir+'/MonitorLog/systemlog.txt')
				cmdstr='top -u '+USERNAME +' -bn 1 >>'+curDir+'/MonitorLog/systemlog.txt'
				
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
			
			if stationstr != "LINUX" and stationstr != "SUN":
				ipstr = (conf.getElementsByTagName("IP")[0]).childNodes[0].data
				
				if '127' not in ipstr:
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
						
						if 11< len(str(tmp_list[0])):
							taskNameList.append(tmp_list[0][:11])
						else:
							taskNameList.append(tmp_list[0])
			#print 'taskNameList====='
			#print taskNameList
		except IOError:
			self.browser_show.append('read shell \"i\" Information Error!')
	def PPC_cmd(self,FINISH,tcn,shellcmd,ppc_ip,f):
		if shellcmd =="i":
			#self.browser_show.append('=====run  '+ shellcmd+'\n')
			f.write('============================run '+shellcmd+'=============================\n')
			tfile=curDir+'/tilog.txt'
			try:
				tf=open(tfile,'w')
			except IOError:
				self.browser_show.append(tfile+"write mode open failed!")
			tcn.write(shellcmd+'\n')
			f.write(tcn.read_until(FINISH))
			
			tcn.write(shellcmd+'\n')
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
					tcn.write('tt "'+taskName+'"\n')
					#os.system('echo ============================tt '+taskName+'========================= >>'+resultFile)
					f.write('============================tt  '+taskName+'=========================\n')
					f.write(tcn.read_until(FINISH))
			tf.close()
			os.remove(tfile)
		else:
			self.browser_show.append(shellcmd+'\n')
			tcn.write(shellcmd+'\n')
			f.write('============================'+shellcmd+'=========================\n')
			f.write(tcn.read_until(FINISH))

	def package(self):
		os.chdir(curDir)
		os.system('tar -cf MonitorLog.tar  '+' MonitorLog')
		os.system('rm -rf MonitorLog')
		if os.path.exists(curDir+'/tilog.txt'):
			os.system('rm -f '+curDir+'/tilog.txt')
	def gui_close(self):
		#QMessageBox::question( self, QString( "Question" ), QString( "Script run end " ), QMessageBox::Ok,SMEE::MessageBox::Cancel);
		QMessageBox.information(self, "Tips", "The Infomation Collect Finish.")
if __name__ == '__main__':
	app = QApplication(sys.argv)
	widget = MainWindow()
	widget.resize(800,600) #kuang,gao
	widget.setWindowTitle("Info Collect")
	widget.show()
	sys.exit(app.exec_())