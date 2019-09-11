#-*- coding:utf-8 -*-

import urllib
import urllib2
import sys,re,os

##########################################
#需填写StarTeam用户名和密码
login_name='203build'
login_passwd='203smeebuild'
##########################################


ToView = [
         {'203M 205':'http://172.16.42.76:8819/overview/18'},
         {'20516 301C 206 205C 509' :'http://172.16.42.76:8819/overview/15'}
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
        view_tag   = find_data(r'<select name="(?P<tag>.*?)" .*</select>', data, 'view_tag')
        label_tag  = find_data(u'<span class="label">标签</span>.*<textarea class=.* name="(?P<tag>.*?)" id=.*</textarea>.*<span class="label">目标视图', data, 'label_tag')
        SubView_tag = find_data(u'<span class="label">目标视图</span>.*<input type=.* name="(?P<tag>.*?)" id=.*<span class="label">.*账户', data, 'SubView_tag')
        user_tag   = find_data(u'<span class="label">.*账户</span>.*<input type=.* name="(?P<tag>.*?)" id=.*</input>.*<span class="label">.*密码</span>', data, 'user_tag')
        passwd_tag = find_data(u'<span class="label">.*密码</span>.*<input type=.* name="(?P<tag>.*?)" id=.*</input>', data, 'passwd_tag')
        url_data = {view_tag : view_value, label_tag : label, SubView_tag : SubView, user_tag : login_name, passwd_tag : login_passwd}
        reader.read(url, url_data)

        print '\nAdd QB success.'
        return
        
if __name__ == '__main__':
    try:
        if (4 != len(sys.argv)):
            raise Exception('parameter invalid! Usage : QBBuild.py project label')
        project = str(sys.argv[1])
        label = str(sys.argv[2])
        SubView = str(sys.argv[3])
        prj_valid = False
        for prj in ToView:
            if (-1 != prj.keys()[0].find(project)):
                prj_valid = True
                qb = QB('500qb', '500qb', prj.values()[0], '8819')
                break
        if (False == prj_valid):
            raise Exception('project=%s is not exist'%project)  
        qb.add_QB_task()
    except  BaseException,e:
        print '\nError : ' +`e`
    
