#-*- coding:utf-8 -*-

import urllib
import urllib2
import sys,re,os

##########################################
#需填写StarTeam用户名和密码
login_name='203build'
login_passwd='203smeebuild'
##########################################

build_500_solaris = [
            {'205 SSB500_30':'http://172.16.42.76:8814/overview/11'},
            {'207001 207002 207003 207004 207005 207006 207007' : 'http://172.16.42.76:8814/overview/16'},
            {'207008 207009 207010 207011 207012 207013' : 'http://172.16.42.76:8814/overview/20'},
            {'207014 207015 207017 207018 207019 207020' : 'http://172.16.42.76:8814/overview/21'},
            {'207021 207022 207023 207024 207025 207026' : 'http://172.16.42.76:8814/overview/17'},
            {'207030 207031 207032 207033 207034 207035 207036' : 'http://172.16.42.76:8814/overview/22'},
            {'207037 207038 207039' : 'http://172.16.42.76:8814/overview/32'},
            {'205-SWS3.3' : 'http://172.16.42.76:8814/overview/31'}
            ]
build_500_linux = [
             {'207027 207028' : 'http://172.16.42.76:8811/overview/11'},
             {'207016 207029' : 'http://172.16.42.76:8811/overview/26'},
             {'207040 207041' : 'http://172.16.42.76:8811/overview/24'},
             {'207042 207043 207044 207045 207046 207047 207048 207049' : 'http://172.16.42.76:8811/overview/25'},
             {'205C SSB530_10' : 'http://172.16.42.76:8811/overview/9'},
             {'206 SSB545_10' : 'http://172.16.42.76:8811/overview/12'},
             {'20516 SSB500_28' : 'http://172.16.42.76:8811/overview/21'},
             {'509 SSB500_25P' : 'http://172.16.42.76:8811/overview/10'},
             {'210001' : 'http://172.16.42.76:8811/overview/23'}
             ]

build_300 = [
             {'301 SSB300' : 'http://172.16.42.76:8812/overview/10'},
             {'206003 206004 206005 206007 206008 206010 206011 206012' : 'http://172.16.42.76:8812/overview/17'},
             {'206009 206013 206014 206015 206016 206017 206018 206019' : 'http://172.16.42.76:8812/overview/18'},
             {'206020 206021 206022 206023 206024 206025 206026 206027 206028 206029' : 'http://172.16.42.76:8812/overview/19'},
             {'301C' : 'http://172.16.42.76:8812/overview/9'}
             ]
             
build_203M = [
             {'203M SSB500_10M' : 'http://172.16.42.76:10010/overview/9'},
             {'CB' : 'http://172.16.42.76:10010/overview/15'},
             {'204001 204002 204003 204004 204005 204006' : 'http://172.16.42.76:10010/overview/11'},
             {'204007 204008 204009 204010 204011 204012' : 'http://172.16.42.76:10010/overview/12'},
             {'204013 204014' : 'http://172.16.42.76:10010/overview/13'},
             {'203M-SWS3.3' : 'http://172.16.42.76:10010/overview/14'},
             {'203M-CB-SWS' : 'http://172.16.42.76:10010/overview/16'},
             {'203M-13-SWS' : 'http://172.16.42.76:10010/overview/17'},
             ]

def find_data(regex, data, tag = None):
    find = re.findall(regex, data, re.DOTALL)
    if find:
        return find[0]
    else:
        try:
            fd = open(os.getcwd()+'\QBuild_log.log', 'w')
            fd.write(`data`)
            fd.close()
        except:
            print 'create ' + os.getcwd()+'\QBuild_log.log failed.'
        raise Exception(tag + ' is not exist.')
        return None

class URLReader(object):
    def __init__(self):
        user_agent = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.1; .NET CLR 2.0.50727)'
        self.__opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
        self.__opener.addheaders = [('User-agent', user_agent)]
        urllib2.install_opener(self.__opener)
    def read(self, url, params = None):
        if None == params:
            f = self.__opener.open(url)
        else:
            f = self.__opener.open(url, urllib.urlencode(params))
        data = f.read()
        return data

class QB(object):
    def __init__(self, name, passwd, url, port):
        self.QB_name = name
        self.QB_passwd = passwd
        self.base_url = url
        self.port = port
    def add_QB_task(self):
        reader = URLReader()
        reader.read('http://172.16.42.76:%s/signin'%self.port)
        data = reader.read('http://172.16.42.76:%s/signin'%self.port)
        login_url = 'http://172.16.42.76:%s/signin?'%self.port
        login_url = str(login_url + find_data(r'<form id=.* action="signin\?(?P<url>.*?)">.*</form>', data, 'login_url'))
        reader.read(login_url, {'userName': self.QB_name, 'password': self.QB_passwd})
        data = reader.read(self.base_url)
        url = 'http://172.16.42.76:%s/overview/'%self.port
        url = url + find_data(r'<button class="btn run" title="Run the configuration".*href=&#039;../(?P<url>.*?)&#039;; } ;return false"><i class="fa fa-play"></i></button>', data, 'Run the configuration')
        data = reader.read(url)
        url = 'http://172.16.42.76:%s/wicket/'%self.port
        url = str(url + find_data(r'<form id=.* action="(?P<url>.*?)"><div.*', data, 'Build configuration url'))
        data = find_data(r'<form id=.*</form>', data, 'form data').decode('utf-8')
        find = re.findall(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">%s</option>.*<span class="label">标签</span>'%project, data, re.DOTALL)
        if find:
            view_value=find[0]
        else:
            if (project == '205'):
                view_value = find_data(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">SSB500_30</option>.*<span class="label">标签</span>', data, 'view_value')
            elif (project == '203M'):
                view_value = find_data(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">SSB500_10M</option>.*<span class="label">标签</span>', data, 'view_value')
            elif (project == '205C'):
                view_value = find_data(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">SSB530_10</option>.*<span class="label">标签</span>', data, 'view_value')
            elif (project == '206'):
                view_value = find_data(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">SSB545_10</option>.*<span class="label">标签</span>', data, 'view_value')
            elif (project == '20516'):
                view_value = find_data(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">SSB500_28</option>.*<span class="label">标签</span>', data, 'view_value')
            elif (project == '509'):
                view_value = find_data(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">SSB500_25P</option>.*<span class="label">标签</span>', data, 'view_value')
            elif (project == '301'):
                view_value = find_data(u'<span class="label">视图</span>.*<option.*value="(?P<value>.*?)">SSB300</option>.*<span class="label">标签</span>', data, 'view_value')
        view_tag   = find_data(r'<select name="(?P<tag>.*?)" .*</select>', data, 'view_tag')
        label_tag  = find_data(u'<span class="label">标签</span>.*<input type=.* name="(?P<tag>.*?)".*</input>.*<span class="label">.*账户</span>', data, 'label_tag')
        user_tag   = find_data(u'<span class="label">.*账户</span>.*<input type=.* name="(?P<tag>.*?)" id=.*</input>.*<span class="label">.*密码</span>', data, 'user_tag')
        passwd_tag = find_data(u'<span class="label">.*密码</span>.*<input type=.* name="(?P<tag>.*?)" id=.*</input>', data, 'passwd_tag')
        url_data = {view_tag : view_value, label_tag : label, user_tag : login_name, passwd_tag : login_passwd}
        reader.read(url, url_data)
        print '\nAdd QB success.'
        return
        
if __name__ == '__main__':
    try:
        if (3 != len(sys.argv)):
            raise Exception('parameter invalid! Usage : QBBuild.py project label')
        project = str(sys.argv[1])
        label = str(sys.argv[2])
        prj_valid = False
        for prj in build_500_solaris:
            if (-1 != prj.keys()[0].find(project)):
                prj_valid = True
                qb = QB('500qb', '500qb', prj.values()[0], '8814')
                break
        if (False == prj_valid):
            for prj in build_203M:
                if (-1 != prj.keys()[0].find(project)):
                    prj_valid = True
                    qb = QB('500qb2', '500qb2', prj.values()[0], '10010')
                    break
        if (False == prj_valid):
            for prj in build_500_linux:
                if (-1 != prj.keys()[0].find(project)):
                    prj_valid = True
                    qb = QB('500cqb', '500cqb', prj.values()[0], '8811')
                    break
        if (False == prj_valid):
            for prj in build_300:
                if (-1 != prj.keys()[0].find(project)):
                    prj_valid = True
                    qb = QB('300qb', '300qb', prj.values()[0], '8812')
                    break
        if (False == prj_valid):
            raise Exception('project=%s is not exist'%project)  
        qb.add_QB_task()
    except  BaseException,e:
        print '\nError : ' +`e`
    
