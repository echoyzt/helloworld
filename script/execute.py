#-*- coding:utf-8 -*-

import sys,re,os,subprocess
import telnetlib,time
from ftplib import FTP
import threading

g_config_file = 'project.cfg'

def find_vw_end(data):
    find = re.findall(r'\w\:[^\<]*>\s*$', data, re.DOTALL)
    if find:
        return True
    else:
        return False

#获取登录信息
def get_login_info(output_signal, project, typ):
    try:
        fd = open('./' + g_config_file)
        for line in fd:
            exec(line.replace('\\','/'))
        fd.close()
        
        if pro205.__contains__(project)\
        or pro203m.__contains__(project)\
        or pro203mNew.__contains__(project)\
        or pro203m_13.__contains__(project)\
		or pro203m_cb.__contains__(project)\
        or pro205new.__contains__(project)\
        or pro20516.__contains__(project)\
        or pro206.__contains__(project)\
        or pro205c.__contains__(project)\
        or pro509.__contains__(project):
            if typ == 'vw':
                return vw500IP,vw500usr,vw500pw,script_home
            else:
                if pro203m.__contains__(project)\
                or pro203mNew.__contains__(project):
                    return sparc500IP,sparc500usr,sparc500pw,script_home
                elif pro20516.__contains__(project)\
                or pro206.__contains__(project)\
                or pro205c.__contains__(project)\
                or pro509.__contains__(project):
                    return linux500IP,linux500usr,linux500pw,script_home
                else:
                    return sun500IP,sun500usr,sun500pw,script_home
                
        if pro301.__contains__(project)\
        or pro301new.__contains__(project)\
        or pro301c.__contains__(project):
            if typ == 'vw':
                return vw300IP,vw300usr,vw300pw,script_home
            else:
                if pro301.__contains__(project) \
                or pro301new.__contains__(project):
                    return sun300IP,sun300usr,sun300pw,script_home
                else:
                    return linux300IP,linux300usr,linux300pw,script_home

    except  BaseException,e:
        output_signal.emit('\n(get_login_info): ' +`e`)

#从本地上传脚本至SUN服务器
def ftp_upload(output_signal, project, cwd, file_list):
    try:
        ip,user,passwd,script_home  = get_login_info(output_signal, project, 'sun')
        f=FTP(ip)
        f.login(user, passwd)
        time.sleep(0.1)
        f.cwd(cwd)
        time.sleep(0.01)
        for file in file_list:
            fp = open(file, 'rb')
            f.storbinary('STOR ' + file, fp, 1024)
            time.sleep(0.01)
            fp.close()
        f.quit()
    except  BaseException,e:
        output_signal.emit('\n(ftp_upload): ' +`e`)

#从WIN服务器至SUN服务器下载脚本
def ftp_download(output_signal, project, cwd):
    try:
        tn = None
        sun_ip,sun_user,sun_passwd,script_home  = get_login_info(output_signal, project, 'sun')
        vw_ip,vw_user,vw_passwd,script_home  = get_login_info(output_signal, project, 'vw')
        tn = telnetlib.Telnet(vw_ip)
        tn.read_until('login:')
        tn.write(vw_user+'\r\n')
        tn.read_until('password:')
        tn.write(vw_passwd+'\r\n')
        time.sleep(0.1)
        line =tn.read_very_eager()
        tn.write('mkdir '+cwd.replace('/','\\')+'\r\n')
        tn.write('cd /d '+cwd.replace('/','\\')+'\r\n')
        tn.write('echo open '+sun_ip+'>ftpcmd\r\n')
        tn.write('echo user '+sun_user+' '+sun_passwd+'>>ftpcmd\r\n')
        tn.write('echo prompt >>ftpcmd\r\n')
        tn.write('echo bi >>ftpcmd\r\n')
        tn.write('echo cd '+cwd.split('d:\\')[1].replace('\\','/')+'>>ftpcmd\r\n')
        tn.write('echo mget *>>ftpcmd\r\n')
        tn.write('echo quit>>ftpcmd\r\n')
        tn.write('ftp -n -s:ftpcmd\r\n')
        while True:
            time.sleep(0.02)
            line =tn.read_very_eager()
            if line !='':
                output_signal.emit(line)    
            line = line.strip()
            if find_vw_end(line):
                break
        tn.write('del /q /f ftpcmd\r\n')
        tn.close() 
        tn = None
    except  BaseException,e:
        output_signal.emit('\n(ftp_download): ' +`e`)
        if (tn != None):
            tn.close() 
            tn = None

g_timeout=False

def timer_cb():
    global g_timeout
    g_timeout=True
            
#执行本地脚本
def perform_win(win_output_signal, finish_signal, script, project, typ, args):
    try:
        global g_timeout
        win_output_signal.emit('perform_win\n')
        timer=None
        params = ''
        for arg in args:
            params = params + ' ' + arg 
		
        fd=subprocess.Popen(script + ' ' + project + '%s'%params, shell=True, stdout=subprocess.PIPE)
        while True:
            time.sleep(0.02)
            line = fd.stdout.readline()
            if line !='':
                win_output_signal.emit(line) 
                if (timer != None):
                    timer.cancel()
                    timer=None
            else:
                if (timer == None):
                    timer=threading.Timer(5, timer_cb)
                    timer.start()
                if g_timeout:
                    g_timeout=False
                    break
        timer.join()
        timer=None
        finish_signal.emit('vw')
    except  BaseException,e:
        win_output_signal.emit('\n(perform_win): ' +`e`)
        finish_signal.emit('vw')

#执行WIN服务器脚本
def perform_vw(win_output_signal, finish_signal, script, project, typ, args):
    try:
        win_output_signal.emit('perform_vw\n')
        ip,user,passwd,script_home = get_login_info(win_output_signal, project, typ)
        script_home = 'd:\\'+script_home
 
        ftp_download(win_output_signal, project, script_home.replace('/','\\'))
        
        tn = telnetlib.Telnet(ip)
        tn.read_until('login:')
        tn.write(user+'\r\n')
        tn.read_until('password:')
        tn.write(passwd+'\r\n')
        time.sleep(0.1)
        line =tn.read_very_eager()
        
        tn.write('cd /d ' + script_home.replace('/','\\') +'\r\n')
        
        params = ''
        for arg in args:
            params = params + ' ' + arg 

        tn.write(script + ' '+ project + '%s\r\n'%params)
        time.sleep(0.5)
        
        while True:
            time.sleep(0.02)
            line =tn.read_very_eager()
            if line !='':
                win_output_signal.emit(line)    
            line = line.strip()
            if find_vw_end(line):
                break
        tn.close()
        tn = None
        finish_signal.emit('vw')
    except  BaseException,e:
        win_output_signal.emit('\n(perform_vw): ' +`e`)
        finish_signal.emit('vw')
        if (tn != None):
            tn.close() 
            tn = None

#执行SUN服务器脚本
def perform_sun(sun_output_signal, finish_signal, script, project, typ,  args):
    try:
        sun_output_signal.emit('perform_sun\n')
        tn = None
        file_list=[g_config_file]
        file_list.append(script)
        if os.path.exists(script+'.bat'):
            file_list.append(script+'.bat')
        ip,user,passwd,script_home = get_login_info(sun_output_signal, project, typ)

        ftp_upload(sun_output_signal, project, script_home, file_list)

        tn = telnetlib.Telnet(ip)
        tn.read_until('login:')
        tn.write(user+'\n')
        tn.read_until('Password:')
        tn.write(passwd+'\n')
        time.sleep(0.5)
        tn.write('cd '+ script_home + '\n')
        tn.write('chmod 777 *\n')
        time.sleep(0.02)
        line =tn.read_very_eager()
        params = ''
        for arg in args:
            params = params + ' ' + arg 
        
        tn.write('./' + script + ' ' + project + '%s'%params + '\n')
        time.sleep(0.5)
        
        while True:
            time.sleep(0.02)
            line =tn.read_very_eager()
            if line !='':
                sun_output_signal.emit(line)    
            line = line.strip()
            if line.endswith('$'):
                time.sleep(1) 
                line = tn.read_very_eager()
                if line == '':
                    break
        tn.close()
        tn = None
        finish_signal.emit('sun')
    except  BaseException,e:
        sun_output_signal.emit('\n(perform_sun): ' +`e`)
        finish_signal.emit('sun')
        if (tn != None):
            tn.close() 
            tn = None
        
