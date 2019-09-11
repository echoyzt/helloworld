# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\integration\mainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import os,sys
from execute import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
        
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
        
class Thread(QtCore.QThread):
    sun_output_signal = QtCore.pyqtSignal(str)
    win_output_signal = QtCore.pyqtSignal(str)
    finish_signal = QtCore.pyqtSignal(str)
    def __init__(self, func_name, parent=None, script='', project='', typ='', params=[]):
        super(Thread, self).__init__(parent)
        self.func_name = func_name
        self.project = project 
        self.script = script 
        self.typ = typ 
        self.params = params
        
    def run(self):
        if (self.typ == 'sun'):
            self.func_name(self.sun_output_signal, self.finish_signal, self.script, self.project, self.typ, self.params)
        else:
            self.func_name(self.win_output_signal, self.finish_signal, self.script, self.project, self.typ, self.params)
            
class Ui_MainWindow(object):
    def __init__(self):
        self.script_cfg = {}  #配置文件全部参数
        self.script_params = [] #脚本参数列表
        self.current_num_layout = 0 #当前脚本参数列表
        self.max_num_params = 0
        self.max_num_script = 0
        self.script_type = []
        self.v_params_h_layout = []
        self.v_params_name = []
        self.v_params_input = []
        self.perform_typ = ''
   
    def paintEvent(self, qpainter):
        painter = QtGui.QPainter(self.centralwidget)
        image = QtGui.QImage('sidepixmap.png')
        brush = QtGui.QBrush(QtGui.QColor(196,200,160))
        painter.setBrush(brush)
        painter.drawRoundedRect(self.centralwidget.rect(), 20, 20)
        painter.drawImage(self.centralwidget.rect(), image)
  
    def setupUi(self, MainWindow):
        self.get_config()
        self.init_params()
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(900, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        #self.centralwidget.paintEvent = self.paintEvent
        self.gridLayout_6 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.script_list_group = QtGui.QGroupBox(self.centralwidget)
        self.script_list_group.setObjectName(_fromUtf8("script_list_group"))
        self.gridLayout_3 = QtGui.QGridLayout(self.script_list_group)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.script_listWidget = QtGui.QListWidget(self.script_list_group)
        self.script_listWidget.setObjectName(_fromUtf8("script_listWidget"))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        font.setBold(True)

        for i in range(self.max_num_script):
            item = QtGui.QListWidgetItem()
            item.setFont(font)
            self.script_listWidget.addItem(item)
        self.gridLayout_3.addWidget(self.script_listWidget, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.script_list_group, 0, 0, 2, 1)
        self.params_group = QtGui.QGroupBox(self.centralwidget)
        self.params_group.setObjectName(_fromUtf8("params_group"))
        self.gridLayout_2 = QtGui.QGridLayout(self.params_group)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        
        for i in range(self.max_num_params):
            self.v_params_h_layout.append(QtGui.QHBoxLayout())
            self.v_params_h_layout[i].setObjectName(_fromUtf8("params_h_layout"+`i`))
            self.v_params_name.append(QtGui.QLabel(self.params_group))
            self.v_params_name[i].setObjectName(_fromUtf8("params_name"+`i`))
            self.v_params_h_layout[i].addWidget(self.v_params_name[i])
            self.v_params_input.append(QtGui.QLineEdit(self.params_group))
            self.v_params_input[i].setObjectName(_fromUtf8("params_input"+`i`))
            self.v_params_h_layout[i].addWidget(self.v_params_input[i])
            self.v_params_input[i].setVisible(False)
            self.v_params_name[i].setVisible(False)
            #self.v_params_name[i].setFont(font)
        
        self.go_h_layout = QtGui.QHBoxLayout()
        self.go_h_layout.setObjectName(_fromUtf8("go_h_layout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.go_h_layout.addItem(spacerItem)
        self.cancel_button = QtGui.QPushButton(self.params_group)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.cancel_button.setFont(font)
        self.go_h_layout.addWidget(self.cancel_button)
        self.go_button = QtGui.QPushButton(self.params_group)
        self.go_button.setObjectName(_fromUtf8("go_button"))
        self.go_button.setFont(font)
        self.go_h_layout.addWidget(self.go_button)
        self.gridLayout_6.addWidget(self.params_group, 0, 1, 1, 1)
        
        self.output_group = QtGui.QGroupBox(self.centralwidget)
        self.output_group.setObjectName(_fromUtf8("output_group"))
        self.gridLayout = QtGui.QGridLayout(self.output_group)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.win_group = QtGui.QGroupBox(self.output_group)
        self.win_group.setObjectName(_fromUtf8("win_group"))
        self.gridLayout_4 = QtGui.QGridLayout(self.win_group)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.win_output = QtGui.QTextEdit(self.win_group)
        self.win_output.setObjectName(_fromUtf8("win_output"))
        self.gridLayout_4.addWidget(self.win_output, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.win_group, 0, 0, 1, 1)
        self.sun_group = QtGui.QGroupBox(self.output_group)
        self.sun_group.setObjectName(_fromUtf8("sun_group"))
        self.gridLayout_5 = QtGui.QGridLayout(self.sun_group)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.sun_output = QtGui.QTextEdit(self.sun_group)
        self.sun_output.setObjectName(_fromUtf8("sun_output"))
        self.gridLayout_5.addWidget(self.sun_output, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.sun_group, 0, 1, 1, 1)
        self.gridLayout_6.addWidget(self.output_group, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.go_button.clicked.connect(self.__go_button_slot)
        self.cancel_button.clicked.connect(self.__cancel_button_slot)
        self.script_listWidget.clicked.connect(self.__list_slot)
        self.script_name = self.script_listWidget.item(0).text().toLatin1().data()
        if self.script_cfg.has_key(self.script_name ):
            self.current_num_layout = len(self.script_cfg[self.script_name])
            for i in range(self.current_num_layout):
                self.v_params_input[i].setVisible(True)
                self.v_params_name[i].setVisible(True)
                self.v_params_name[i].setText(_translate("MainWindow", self.script_params[0][i], None))
                self.gridLayout_2.addLayout(self.v_params_h_layout[i], i, 0, 1, 1)
            self.gridLayout_2.addLayout(self.go_h_layout, self.current_num_layout, 0, 1, 1)

    #界面文字显示
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Integration_Window", None))
        self.script_list_group.setTitle(_translate("MainWindow", "脚本列表", None))
        __sortingEnabled = self.script_listWidget.isSortingEnabled()
        self.script_listWidget.setSortingEnabled(False)
        i = 0
        for s_name in self.script_cfg:
            item = self.script_listWidget.item(i)
            item.setText(_translate("MainWindow", s_name, None))
            i += 1
        self.script_listWidget.setSortingEnabled(__sortingEnabled)
        self.params_group.setTitle(_translate("MainWindow", "参数列表", None))
        self.go_button.setText(_translate("MainWindow", "go", None))
        self.cancel_button.setText(_translate("MainWindow", "cancel", None))
        self.output_group.setTitle(_translate("MainWindow", "脚本输出", None))
        self.win_group.setTitle(_translate("MainWindow", "Win_Output", None))
        self.sun_group.setTitle(_translate("MainWindow", "Sun_Output", None))
	
    #SUN输出显示
    def display_sun_output_slot(self, content):
        self.sun_output.append(content)
      
    #WIN输出显示      
    def display_win_output_slot(self, content):
        self.win_output.append(content)
        
    #脚本完成函数
    def finish_slot(self, typ):
        if (self.perform_typ == typ):
            self.go_button.setEnabled(1)
            self.perform_typ=''
        
        if (self.perform_typ == 'sun/vw'):
            self.perform_typ=self.perform_typ.replace('/', '')
            self.perform_typ=self.perform_typ.replace(typ, '')
        
        if ('sun' == typ):
            if self.runner_sun:
                del self.runner_sun
        if ('vw' == typ):
            if self.runner_vw:
                del self.runner_vw 
        if ('sun/vw' == typ):
            if self.runner_sun:
                del self.runner_sun
            if self.runner_vw:
                del self.runner_vw 
                
    #执行按钮槽函数
    def __go_button_slot(self):
        self.go_button.setEnabled(0)
        c_row = self.script_listWidget.currentRow()
        name = self.script_listWidget.item(c_row).text().toLatin1().data()
        parameter = []
        for i in range(len(self.script_cfg[name])):
            parameter.append(self.v_params_input[i].text().toLatin1().data())
        
        view = parameter[0]
        parameter.remove(view)
        self.perform_typ = self.script_type[c_row]
        if self.script_type[c_row] == 'sun/vw':
            self.sun_output.setText('')
            self.runner_sun = Thread(perform_sun, parent=None, script=name, project=view, typ='sun', params=parameter)
            self.runner_sun.sun_output_signal.connect(self.display_sun_output_slot)
            self.runner_sun.finish_signal.connect(self.finish_slot) 
            self.runner_sun.start()

            self.win_output.setText('')
            self.runner_vw = Thread(perform_vw, parent=None, script=name, project=view, typ='vw', params=parameter)
            self.runner_vw.win_output_signal.connect(self.display_win_output_slot)  
            self.runner_vw.finish_signal.connect(self.finish_slot) 
            self.runner_vw.start()
            
        elif self.script_type[c_row] == 'sun':
            self.sun_output.setText('')
            self.runner_sun = Thread(perform_sun, parent=None, script=name, project=view, typ='sun', params=parameter)
            self.runner_sun.sun_output_signal.connect(self.display_sun_output_slot)  
            self.runner_sun.finish_signal.connect(self.finish_slot) 
            self.runner_sun.start()

        else:
            self.perform_typ = 'vw'
            self.win_output.setText('')
            self.runner_vw = Thread(perform_win, parent=None, script=name, project=view, typ='vw', params=parameter)
            self.runner_vw.win_output_signal.connect(self.display_win_output_slot)  
            self.runner_vw.finish_signal.connect(self.finish_slot) 
            self.runner_vw.start()

    #取消按钮槽函数
    def __cancel_button_slot(self):
        if (self.perform_typ != ''):
            if (self.perform_typ == 'sun/vw'):
                self.runner_sun.terminate()
                self.runner_vw.terminate()
                self.runner_sun.finish_signal.emit('vw')
                self.runner_vw.finish_signal.emit('sun')
            elif (self.perform_typ == 'sun'):
                self.runner_sun.terminate()
                self.runner_sun.finish_signal.emit('sun')
            else:
                self.runner_vw.terminate()
                self.runner_vw.finish_signal.emit('vw')
    
    #获取列表数据
    def __list_slot(self):
        c_row = self.script_listWidget.currentRow()
        c_name = self.script_listWidget.item(c_row).text().toLatin1().data()
        if self.script_cfg.has_key(c_name):
            param = self.script_cfg[c_name]
            
            for i in range(self.current_num_layout):
                self.gridLayout_2.removeItem(self.v_params_h_layout[i])
                self.v_params_input[i].setVisible(False)
                self.v_params_name[i].setVisible(False)

            for i in range(len(param)):
                self.v_params_input[i].setVisible(True)
                self.v_params_name[i].setVisible(True)        
                self.gridLayout_2.addLayout(self.v_params_h_layout[i], i, 0, 1, 1)
                self.v_params_name[i].setText(_translate("MainWindow", param[i], None))
                self.current_num_layout = i+1
            self.gridLayout_2.removeItem(self.go_h_layout)
            self.gridLayout_2.addLayout(self.go_h_layout, self.current_num_layout, 0, 1, 1)
     
    #获取配置数据
    def get_config(self):
        try:
            fd = open('./UI.cfg')
            next(fd)
            for line in fd:
                if line:
                    tmp_list = line.split()
                    s_name = tmp_list[0]
                    tmp_list.remove(s_name)
                    tmp={s_name:tmp_list}
                    self.script_cfg.update(tmp)
        except IOError:
            print 'read config file Error!'
            
    #初始化脚本数据
    def init_params(self):
        self.max_num_script = len(self.script_cfg)
        #script_cfg = [type, max_num, params...]
        for i in self.script_cfg:
            tmp_list = self.script_cfg[i]
            tmp_type = tmp_list[0]
            self.script_type.append(tmp_type)
            tmp_num = len(tmp_list)-1
            self.max_num_params = tmp_num > self.max_num_params and tmp_num or self.max_num_params
            tmp_list.remove(tmp_type)
            self.script_params.append(tmp_list)
            
            for i in range(len(self.script_params)):
                j = 0
                if (len(self.script_params[i]) > 1):
                    max_len = 0
                    for params in self.script_params[i]:
                        max_len = len(params) > max_len and len(params) or max_len
                    for params in self.script_params[i]:
                        lack_length = max_len-len(params)
                        if (lack_length > 0):
                            for l in range(lack_length):
                                self.script_params[i][j] += ' '
                        j += 1
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

