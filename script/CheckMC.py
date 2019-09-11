#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys,re,os,ctypes

# 标准数据大小
g_std_size = {'char':1, 'SMEE_CHAR':1, 'SMEE_UINT8':1, 'short':2, 'SMEE_INT16':2, 'unsigned short':2, 'SMEE_UINT16':2,
              'int':4, 'SMEE_INT32':4,  'SMEE_UINT32':4, 'unsigned int':4, 'SMEE_UINT64':8, 'SMEE_INT64':8, 'float':4, 'SMEE_FLOAT':4,
              'double':8, 'SMEE_DOUBLE':8, 'SMEE_LDOUBLE':12, 'SMEE_ULONG32':4, 'SMEE_STRING':4, 'SMEE_LONG':4,
              'SMEE_BOOL':4, 'bool':4}

# 获取文件全路径名
def get_file_full_name(file_name, sp_dir = False, sp_mc = ''):
    if sp_dir:
        for i in range(len(g_cfg_params['sp_dir'][sp_mc])):
            for root, dirs, files in os.walk(g_cfg_params['sp_dir'][sp_mc][i]):
                for f in files:
                    if f == file_name:
                        return root + '\\' + file_name
    for root, dirs, files in os.walk(g_cfg_params['tc_path']):
        for f in files:
            if f == file_name:
                return root + '\\' + file_name
    return file_name

#e.g. 123UL  123
g_re_number1 = re.compile('^(?P<number>[\-]*\d+).*$')

#e.g. -123
g_re_number2 = re.compile('^[\-]*\d+$')

#e.g. 0x2af
g_re_number3 = re.compile('^\d[xX]\w*$')

#e.g. 1e-6  0.01
g_re_number4 = re.compile('^[\-]*\d+[eE\.\-]*\w*$')

#e.g. a+b*c
g_re_number5 = re.compile('^[\(]*\d+[\-\+\*\/\%\(\)]\d+[\-\+\*\/\%\(\)]*\d*[\)]*')

#e.g. name[NUMBER]
g_re_array1 = re.compile(r'^\S*\[(?P<array>\d+)\]\s*$')

#e.g. name[ENUM]
g_re_array2 = re.compile(r'^\S*\[(?P<array>.+)\]\s*$')

#e.g. name[][]
g_re_array3 = re.compile(r'^\S*\[(?P<array1>[^\[]+)\]\[(?P<array2>.+)\]\s*$')

#e.g. name[][][]
g_re_array4 = re.compile(r'^\S*\[(?P<array1>[^\[]+)\]\[(?P<array2>[^\[]+)\]\[(?P<array3>.+)\]\s*$')

#e.g. #4<matching_rate, modifiable="1"> @DirectConstant %double  !0.8  {[--]}  $none  &typical value
g_re_ini_data = re.compile(r'^\s*\#.*\<(?P<name>.*),\s*modifiable.*\>\s*@DirectConstant\s*\%(?P<type>.*)\s+!.*\{.*$')

#e.g. #include "smee.h"
g_re_include1 = re.compile(r'^\s*\#include\s+\"(?P<name>.*)\".*')

#e.g. #include <smee.h>
g_re_include2 = re.compile(r'^\s*\#include\s+\<(?P<name>.*)\>.*')

#e.g. #define name  number
g_re_define1 = re.compile(r'^\s*\#define\W+(?P<name>\w+)\s+\(*(?P<value>\-*\d+\.*[a-zA-Z]*\-*\d*)\)*.*')

#e.g. #define name (number)
g_re_define2 = re.compile(r'^\s*\#define\W+(?P<name>\w+)\W+(?P<value>\d+\.*\w*\-*\d*).*')

#e.g. #define name1 name2
g_re_define3 = re.compile(r'^\s*\#define\W+(?P<name1>\w+)\W+(?P<name2>\w+).*')

#e.g. #define name1 a+b*c
g_re_define4 = re.compile(r'^\s*\#define\W+(?P<name1>\w+)\s+(?P<name2>\W*\w+\s*[\-\+\*\/\%\(\)]\W*\w+\s*[\-\+\*\/\%\(\)\[\]]*\s*\w*[\)\]]*).*')

#e.g. type enum
g_re_enum_head1 = re.compile(r'^\s*typedef\s+enum\s*.*')

#e.g. enum
g_re_enum_head2 = re.compile(r'^\s*enum\s*.*')

#e.g. FSMC_REPAIR_TABLE_MIN = 0,
g_re_enum_body1 = re.compile(r'^\s*(?P<name>\w+)\s*=\s*(?P<value>[\(\)\w\+\-\*\%\/]*)\)*\s*,.*')

#e.g. FSMC_REPAIR_TABLE_MIN,
g_re_enum_body2 = re.compile(r'^\s*(?P<name>\w+)\s*,.*')

#e.g. FSMC_REPAIR_TABLE_MAX
g_re_enum_body3 = re.compile(r'^\s*(?P<name>\w+)\s*')

#e.g. typedef struct
g_re_struct_head1 = re.compile(r'^\s*typedef\s+struct\s*.*')

#e.g. unsigned int iZeroFreq; /* <default>250.0<unit><range><description>零点频率 */
g_re_struct_body1 = re.compile(r'^\s*(?P<type_name>\w+\s*\w*)\s+(?P<var_name>[^;]+)\s*;.*')

#e.g. }FSMC_ONE_FILTER_USER_PARAS_STRUCT;
g_re_end1 = re.compile(r'^\s*\}\s*(?P<name>\w+)\s*\;.*')

#e.g. };
g_re_end2 = re.compile(r'^\s*\}\s*\;.*')

#e.g. FSMC_ONE_FILTER_USER_PARAS_STRUCT;
g_re_end3 = re.compile(r'^\s*(?P<name>[\w\_]+)\s*\;.*')

#所有依赖头文件列表
g_include_file_list = []

#所有宏定义
g_define_dict = {}

#所有枚举
g_enum_dict = {}

#所有结构体
g_struct_dict = {}

#配置文件参数
g_cfg_params = {'tc_path':'', 'ini_path':'', 'macro':[], 'sp_mc':{}, 'sp_file':{}, 'sp_dir':{}}

#当前文件名称
g_cur_file = ''

#调试标志位
g_debug = 0

def init_gloabl_params():
    g_include_file_list = []
    g_define_dict = {}
    g_enum_dict = {}
    g_struct_dict = {}
    g_cfg_params = {'tc_path':'', 'ini_path':'', 'macro':[], 'sp_mc':{}, 'sp_file':{}, 'sp_dir':{}}
    g_cur_file = ''
    g_debug = 0
    
def clear_log():
    try:
        fd = open('./error.log', 'w')
        fd.close()
    except IOError,e:
        print '\nerror.log: ' + `e`

def log_info(line):
    try:
        fd = open('./error.log', 'a')
        fd.write(line)
        fd.close()
    except IOError,e:
        print '\nerror.log: ' + `e`       
    
#获取数组中枚举或宏的大小
def get_macro_size(macro):
    global g_debug,g_cur_file
    macro = macro.strip()
    re_number1 = g_re_number1.match(macro)
    re_number2 = g_re_number2.match(macro)
    re_number3 = g_re_number3.match(macro)
    re_number4 = g_re_number4.match(macro)
    if g_std_size.has_key(macro):
        size = 0
    elif re_number1:
        size = int(re_number1.group('number'))
    elif re_number2:
        size = int(macro)
    elif re_number3:
        size = int(macro, 16)
    elif re_number4:
        size = float(macro)
    else:
        if g_enum_dict.has_key(macro):
            size = g_enum_dict[macro]
        elif g_define_dict.has_key(macro):
            size = g_define_dict[macro]
        else:
            if re.compile(r'\w*\W+\w*').match(macro):
                print '%s: unknown macro, %s\n'%(g_cur_file, macro)
                return 0
            else:
                raise Exception(macro + ' is undefine.')
    return size

#进行简单整型四则运算
def cal_size(array):
    global g_debug,g_cur_file
    array = array.strip()
    #e.g. (a)
    re_number6 = re.compile('^\((?P<data>.+)\)$').match(array)
    if re_number6:
        array = re_number6.group('data')
    size = 0
    #e.g.  a+b*c
    re_cal = re.compile('\s*(?P<br1>\(*)\s*(?P<data1>\-*\w+)\s*(?P<br11>\)*)\s*(?P<sign1>[\+\-\*\/|%])\s*(?P<br2>\(*)\s*(?P<data2>\w+)\s*(?P<br22>\)*)\s*(?P<sign2>[\+\-\*\/|%]*)\s*(?P<br3>\(*)\s*(?P<data3>\w*)\s*(?P<br33>\)*)\s*')
    re_cal = re_cal.match(array)
    if re_cal:
        if re_cal.group('data1').lower().find('e') and re.match('^[\-]*\d+[eE]$', re_cal.group('data1')):  #踢出10e-10指数的干扰，仅支持正数计算
            re_cal = None     
    if re_cal:
        data1 = get_macro_size(re_cal.group('data1'))
        sign1 = re_cal.group('sign1')
        data2 = get_macro_size(re_cal.group('data2'))
        sign2 = re_cal.group('sign2')
        data3 = ''
        if '' != re_cal.group('data3'):
            data3 = get_macro_size(re_cal.group('data3'))
        br1 = re_cal.group('br1')
        br11 = re_cal.group('br11')
        br2 = re_cal.group('br2')
        br22 = re_cal.group('br22')
        br3 = re_cal.group('br3')
        br33 = re_cal.group('br33')

        #带有括号的算式
        if (br1 and br22) or (br2 and br33):
            if (br1 and br22):
                if '+' == sign1:
                    size = data1+data2
                elif '-' == sign1:
                    size = data1-data2
                elif '*' == sign1:
                    size = data1*data2
                elif '/' == sign1:
                    size = data1/data2
                else:
                    size = data1%data2
                if '' != sign2:
                    if '+' == sign2:
                        size = size+data3
                    elif '-' == sign2:
                        size = size-data3
                    elif '*' == sign2:
                        size = size*data3
                    elif '/' == sign2:
                        size = size/data3
                    else:
                        size = size%data3
            else:
                if '+' == sign2:
                    size = data2+data3
                elif '-' == sign2:
                    size = data2-data3
                elif '*' == sign2:
                    size = data2*data3
                elif '/' == sign2:
                    size = data2/data3
                else:
                    size = data2%data3
                if '' != sign1:
                    if '+' == sign1:
                        size = data1+size
                    elif '-' == sign1:
                        size = data1-size
                    elif '*' == sign1:
                        size = data1*size
                    elif '/' == sign1:
                        size = data1/size
                    else:
                        size = data1%size    
        else:
            #不带有括号的算式
            if (('*' == sign1) or ('/' == sign1) or ('%' == sign1)) and (('*' == sign2) or ('/' == sign2) or ('%' == sign2)):
                if '*' == sign1:
                    if ('*' == sign2):
                        size = data1*data2*data3
                    elif ('/' == sign2):
                        size = data1*data2/data3
                    elif ('%' == sign2):
                        size = data1*data2%data3
                        
                if '/' == sign1:
                    if ('*' == sign2):
                        size = data1/data2*data3
                    elif ('/' == sign2):
                        size = data1/data2/data3
                    elif ('%' == sign2):
                        size = data1/data2%data3

                if '%' == sign1:
                    if ('*' == sign2):
                        size = data1%data2*data3
                    elif ('/' == sign2):
                        size = data1%data2/data3
                    elif ('%' == sign2):
                        size = data1%data2%data3
            elif (('+' == sign1) or ('=' == sign1)) and (('*' == sign2) or ('/' == sign2) or ('%' == sign2)):
                if '+' == sign1:
                    if ('*' == sign2):
                        size = data1+data2*data3
                    elif ('/' == sign2):
                        size = data1+data2/data3
                    elif ('%' == sign2):
                        size = data1+data2%data3
                if '-' == sign1:
                    if ('*' == sign2):
                        size = data1-data2*data3
                    elif ('/' == sign2):
                        size = data1-data2/data3
                    elif ('%' == sign2):
                        size = data1-data2%data3
            else:
                if '' != sign2:
                    if '+' == sign1:
                        if ('+' == sign2):
                            size = data1+data2+data3
                        elif ('-' == sign2):
                            size = data1+data2-data3
                    elif '-' == sign1:
                        if ('+' == sign2):
                            size = data1-data2+data3
                        elif ('-' == sign2):
                            size = data1-data2-data3

                    if '*' == sign1:
                        if ('+' == sign2):
                            size = data1*data2+data3
                        elif ('-' == sign2):
                            size = data1*data2-data3
                    elif '/' == sign1:
                        if ('+' == sign2):
                            size = data1/data2+data3
                        elif ('-' == sign2):
                            size = data1/data2-data3       
                    elif '%' == sign1:
                        if ('+' == sign2):
                            size = data1%data2+data3
                        elif ('-' == sign2):
                            size = data1%data2-data3
                else:
                    if '+' == sign1:
                        size = data1+data2
                    elif '-' == sign1:
                        size = data1-data2
                    elif '*' == sign1:
                        size = data1*data2
                    elif '/' == sign1:
                        size = data1/data2
                    elif '%' == sign1:
                        size = data1%data2
                        
    else:
        size = get_macro_size(array)
    return size

# 解析头文件中的include
def parse_include(line, sp_dir = False, sp_mc = ''):
    global g_debug,g_cur_file
    try:
        re_include1 = g_re_include1.match(line)
        re_include2 = g_re_include2.match(line)
        if re_include1:
            f = re_include1.group('name').strip()
            if False == g_include_file_list.__contains__(f):
                tmp_name = get_file_full_name(f, sp_dir, sp_mc)
                if tmp_name:
                    parse_tc_file(tmp_name, sp_dir, sp_mc)
                g_include_file_list.append(f)
                
        elif re_include2:
            f = re_include2.group('name').strip()
            if False == g_include_file_list.__contains__(f):
                tmp_name = get_file_full_name(f, sp_dir, sp_mc)
                if tmp_name:
                    parse_tc_file(tmp_name, sp_dir, sp_mc)
                g_include_file_list.append(f)
    except BaseException, e:
        print '%s: parse_include error, %s\n'%(g_cur_file, line)
    return

# 解析头文件中define
def parse_define(line):
    global g_debug,g_cur_file
    try:
        if line.__contains__('//'):
            line = line.split('//')[0]
        if line.__contains__('/*'):
            line = line.split('/*')[0]
        
        re_define1 = g_re_define1.match(line)
        re_define2 = g_re_define2.match(line)
        re_define3 = g_re_define3.match(line)
        re_define4 = g_re_define4.match(line)
        #if g_debug:
        #    print line,re_define1,re_define2,re_define3,re_define4
        if re_define4:
            macro = re_define4.group('name1').strip()
            value = re_define4.group('name2').strip()
            tmp_dict = {macro:cal_size(value)}
            g_define_dict.update(tmp_dict)
            return

        if re_define1 or re_define2:
            if re_define1:
                re_define = re_define1
            else:
                re_define = re_define2
            if re_define:
                macro = re_define.group('name').strip()
                value = re_define.group('value').strip()
                re_number3 = g_re_number3.match(value)
                #if g_debug:
                #    print line,re_number3,value,macro
                if re_number3:
                    tmp_dict = {macro:int(value, 16)}
                elif value.__contains__('.') or value.__contains__('e'):
                    tmp_dict = {macro:float(value)}
                else:
                    re_number = g_re_number1.match(value)
                    if re_number:
                        tmp_dict = {macro:int(re_number.group('number'))}
                g_define_dict.update(tmp_dict) 
        else:    
            if re_define3:
                name1 = re_define3.group('name1').strip()
                name2 = re_define3.group('name2').strip()
                if g_define_dict.has_key(name2):
                   tmp_dict = {name1:g_define_dict[name2]}
                   g_define_dict.update(tmp_dict)
                elif g_enum_dict.has_key(name2):
                   tmp_dict = {name1:g_enum_dict[name2]}
                   g_define_dict.update(tmp_dict)
    except BaseException, e:
        print '%s: parse_define error, %s\n'%(g_cur_file, line)
    return

# 解析头文件中的enum
def parse_enum(line, parse_key_dict):
    global g_debug,g_cur_file
    try:
        if parse_key_dict['enum_flag']:
            re_enum_body1 = g_re_enum_body1.match(line)
            re_enum_body2 = g_re_enum_body2.match(line)
            re_enum_body3 = g_re_enum_body3.match(line)
            re_end1 = g_re_end1.match(line)
            re_end2 = g_re_end2.match(line)
            re_end3 = g_re_end3.match(line)
            if re_end1 or re_end2 or re_end3:
                parse_key_dict['enum_flag'] = 0
            elif re_enum_body1: #如果枚举后面带数字，枚举值取数字
                enum_name = re_enum_body1.group('name').strip()
                value = re_enum_body1.group('value').strip()
                if re.match('\(*\w+\)*[\+\-\*\%\/]\(*\w+\)*', value) or re.match('[A-Za-z]+.*', value):
                    parse_key_dict['enum_value'] = cal_size(value)
                else:
                    re_number3 = g_re_number3.match(value)
                    if re_number3:
                        parse_key_dict['enum_value'] = int(value, 16)
                    else:
                        parse_key_dict['enum_value'] = int(value)
                tmp_dict = {enum_name:parse_key_dict['enum_value'] }        
                g_enum_dict.update(tmp_dict)
                parse_key_dict['enum_index'] += 1
            elif re_enum_body2: #如果枚举值不带数字则，枚举值按前一个加1
                name = re_enum_body2.group('name').strip()
                if (0 != parse_key_dict['enum_index']): 
                    parse_key_dict['enum_value'] += 1
                tmp_dict = {name:parse_key_dict['enum_value']}
                g_enum_dict.update(tmp_dict)
                parse_key_dict['enum_index'] += 1
            elif re_enum_body3:
                name = re_enum_body3.group('name').strip()
                parse_key_dict['enum_value'] += 1
                tmp_dict = {name:parse_key_dict['enum_value']}
                g_enum_dict.update(tmp_dict)
                parse_key_dict['enum_index'] += 1
            #if g_debug:
            #    print line,parse_key_dict['enum_value'],re_enum_body1,re_enum_body2,re_enum_body3
        else:
            re_enum_head1 = g_re_enum_head1.match(line)
            re_enum_head2 = g_re_enum_head2.match(line)
            if re_enum_head1 or re_enum_head2:
                parse_key_dict['enum_flag'] = 1
                parse_key_dict['enum_value'] = 0
                parse_key_dict['enum_index'] = 0
    except BaseException, e:
        print '%s: parse_enum error, %s\n'%(g_cur_file, line)
    return

# 解析头文件中的struct大小
def parse_struct_size(line, parse_key_dict):
    global g_debug,g_cur_file
    try:
        if parse_key_dict['struct_flag']:
            re_struct_body1 = g_re_struct_body1.match(line)
            re_end1 = g_re_end1.match(line)
            re_end3 = g_re_end3.match(line)
            if re_end1 or re_end3:
                if re_end1:
                    tmp_dict = {re_end1.group('name').strip():parse_key_dict['struct_size']}
                else:
                    tmp_dict = {re_end3.group('name').strip():parse_key_dict['struct_size']}
                g_struct_dict.update(tmp_dict)
                parse_key_dict['struct_flag'] = 0
            elif re_struct_body1:
                type_name = re_struct_body1.group('type_name').strip()
                var_name = re_struct_body1.group('var_name').strip()
                re_array1 = g_re_array1.match(var_name)
                re_array2 = g_re_array2.match(var_name)
                re_array3 = g_re_array3.match(var_name)
                re_array4 = g_re_array4.match(var_name)
                array = 0
                if re_array1 or re_array2 or re_array3 or re_array4:
                    if re_array1:
                        array = cal_size(re_array1.group('array'))
                    if re_array2:
                        array = cal_size(re_array2.group('array'))
                    if re_array3:
                        x = cal_size(re_array3.group('array1'))
                        y = cal_size(re_array3.group('array2'))
                        array = x*y
                    if re_array4:
                        x = cal_size(re_array4.group('array1'))
                        y = cal_size(re_array4.group('array2'))
                        z = cal_size(re_array4.group('array3'))
                        array = x*y*z 
                    if g_std_size.has_key(type_name):
                        parse_key_dict['struct_size'] += g_std_size[type_name] * array
                    elif g_struct_dict.has_key(type_name):
                        parse_key_dict['struct_size'] += g_struct_dict[type_name]*array
                    else:
                        parse_key_dict['struct_size'] += 4*array
                else:
                    if g_std_size.has_key(type_name):
                        parse_key_dict['struct_size'] += g_std_size[type_name]
                    elif g_struct_dict.has_key(type_name):
                        parse_key_dict['struct_size'] += g_struct_dict[type_name]
                    else:
                        parse_key_dict['struct_size'] += 4            
        else:
            re_struct_head1 = g_re_struct_head1.match(line)
            if re_struct_head1:
                parse_key_dict['struct_flag'] = 1
                parse_key_dict['struct_size'] = 0
        #else: do nothing 
    except BaseException, e:
        print '%s: parse_include error, %s'%(g_cur_file, line)
    return

# 解析块注释
def parse_block_comment(line, parse_key_dict):
    global g_debug,g_cur_file
    try:
        if line.__contains__('/*') and (False == line.__contains__('*/')):
            if re.match('^\s*\/\/.*$', line):
                return
            s_line = re.match('^\s*(?P<data>.*)\/\*.*', line) #e.g. valid data /*
            if s_line:
                data = s_line.group('data')
                parse_include(data)
                parse_define(data)
                parse_enum(data, parse_key_dict)
                parse_struct_size(data, parse_key_dict)
            parse_key_dict['line_comment_start_flag']=1  
            parse_key_dict['line_comment_end_flag']=0
        
        if parse_key_dict['line_comment_start_flag']:
            if (False == line.__contains__('/*')) and line.__contains__('*/'):
                s_line = re.match('.*\*\/\s*(?P<data>.*)', line) #e.g. */ valid data
                if s_line:
                    data = s_line.group('data')
                    parse_include(data)
                    parse_define(data)
                    parse_enum(data, parse_key_dict)
                    parse_struct_size(data, parse_key_dict)
                parse_key_dict['line_comment_start_flag']=0  
                parse_key_dict['line_comment_end_flag']=1
        else:
            if line.__contains__('#if') and (False == line.__contains__('#endif')):
                if re.match('^\s*\/\/.*$', line):
                    return
                macro_name = 0
                if re.match('^\s*#if[^n]*[ef]*\s+(?P<macro>[\w\_]+)\s*.*', line):
                    macro_name = re.match('^\s*#if[^n]*[ef]*\s+(?P<macro>\w+)\s*.*', line).group('macro')
                    parse_key_dict['macro_comment_start_flag']=1  
                    parse_key_dict['macro_comment_end_flag']=0
                if re.match('^\s*#if\s+[-]*(?P<number>\d+)\s*.*', line):
                    if 0 == int(re.match('^\s*#if\s+[-]*(?P<number>\d+)\s*.*', line).group('number')):
                        parse_key_dict['macro_comment_start_flag']=1  
                        parse_key_dict['macro_comment_end_flag']=0
                    else:
                        parse_key_dict['macro_comment_start_flag']=0  
                        parse_key_dict['macro_comment_end_flag']=1 
                if g_cfg_params['macro'].__contains__(macro_name):
                    parse_key_dict['macro_comment_start_flag']=1  
                    parse_key_dict['macro_comment_end_flag']=1
      
            if parse_key_dict['macro_comment_start_flag'] and parse_key_dict['macro_comment_end_flag']:
                if line.__contains__('#else'):
                    parse_key_dict['macro_comment_start_flag']=1 
                    parse_key_dict['macro_comment_end_flag']=0
                elif line.__contains__('#endif'):
                    parse_key_dict['macro_comment_start_flag']=0  
                    parse_key_dict['macro_comment_end_flag']=1
            elif parse_key_dict['macro_comment_start_flag']:
                if line.__contains__('#else') or line.__contains__('#endif') :
                    parse_key_dict['macro_comment_start_flag']=0  
                    parse_key_dict['macro_comment_end_flag']=1
    except BaseException,e:
        print '%s: parse_include error, %s\n'%(g_cur_file, line)   
    return

# 解析XXMC_tc文件
def parse_tc_file(file_name, sp_dir = False, sp_mc = ''):
    global g_debug,g_cur_file
    line = ''
    tmp = file_name.split('\\')
    if g_include_file_list.__contains__(tmp[len(tmp)-1]):
        return
    parse_key_dict = {'enum_flag':0, 'struct_flag':0, 'macro_comment_start_flag':0, 'macro_comment_end_flag':1,
                      'line_comment_start_flag':0, 'line_comment_end_flag':1, 'enum_index':0, 'enum_value':0, 'struct_size':0} 
    print file_name
    try:
        g_cur_file=file_name
        fd = open(file_name, 'r')
        for line in fd:
            if -1 == file_name.find('xx.h'):
               g_debug=0
            else:
                g_debug=1
            parse_block_comment(line, parse_key_dict)
            if ((0 == parse_key_dict['line_comment_start_flag']) and parse_key_dict['line_comment_end_flag']) \
            and parse_key_dict['macro_comment_end_flag']:
                parse_include(line, sp_dir, sp_mc)
                parse_define(line)
                parse_enum(line, parse_key_dict)
                parse_struct_size(line, parse_key_dict)
    except IOError,e:
        pass
        #print 'parse_tc_file(%s):'%file_name+`e`+'\n'
    return

# 解析XXMC.ini数据大小
def parse_ini_file(file_name):
    try:
        size = 0
        fd = open(file_name, 'r')
        for line in fd:
            match_line = g_re_ini_data.match(line)
            if match_line:
                v_name = match_line.group('name').strip()
                v_type = match_line.group('type').strip()
                if g_std_size.has_key(v_type):
                    size += g_std_size[v_type]
                elif -1 != v_type.find('char[]') or -1 != v_type.find('SMEE_CHAR[]'):
                    match_array = g_re_array1.match(v_name)
                    if match_array:
                        size += int(match_array.group('array'))
                else:
                    size += 4
        fd.close()
    except IOError,e:
        print 'parse_ini_file(%s):'%file_name+`e`+'\n'
    return size

#读取配置文件
def read_config_file(project, src_path, SIT_path):
    file_list = os.listdir(os.getcwd()+'\\CheckMC_cfg')
    find_flag = 0
    file_tag = 0
    re_sp_dir = re.compile('(?P<mc_file>.*[\.][i][n][i][^:]*)[:](?P<path>.*)')
    re_dir = re.compile('\s*(?P<path>w+\\+)\.h\s*$')
    for i in range(file_list.__len__()):
        if ('CheckMC.cfg_'+project) == file_list[i]:
            find_flag = 1
            try:
                f = open(os.getcwd()+'\\CheckMC_cfg\\'+file_list[i])
                for line in f:
                    if None == re.match('^\s*#.*$', line):
                        if line.__contains__('='):
                            var_name = line.split('=')[0].strip()
                            params = line.split('=')[1]
                        else:
                            params = line
                            var_name = ''
                        
                        if 'tc_path' == var_name:
                            file_tag = 1
                        if 'ini_path' == var_name:
                            file_tag = 2
                        if 'macro' == var_name:
                            file_tag = 3   
                        if 'sp_mc' == var_name:
                            file_tag = 4
                        if 'sp_file' == var_name:
                            file_tag = 5
                        if 'sp_dir' == var_name:
                            file_tag = 6    
                     
                        if  1 == file_tag:
                            if '' != params.strip():
                                if src_path:
                                    g_cfg_params['tc_path'] = src_path
                                else:
                                    g_cfg_params['tc_path'] = params.strip()

                        if  2 == file_tag:
                            if '' != params.strip():
                                if src_path:
                                    g_cfg_params['ini_path'] = SIT_path
                                else:
                                    g_cfg_params['ini_path'] = params.strip()

                        if  3 == file_tag:
                            macro_list = params.split(',')
                            for i in range(len(macro_list)):
                                if '' != macro_list[i].strip():
                                    g_cfg_params['macro'].append(macro_list[i].strip())

                        if  4 == file_tag:
                            tmp_data = params.split(',')
                            for i in range(len(tmp_data)):
                                if '' != tmp_data[i].strip():
                                    tmp_dict = {tmp_data[i].split(':')[0].strip():tmp_data[i].split(':')[1].strip()}
                                    g_cfg_params['sp_mc'].update(tmp_dict)

                        if  5 == file_tag:
                            tmp_data = params.split(',')
                            for i in range(len(tmp_data)):
                                sp_dir = re_sp_dir.match(tmp_data[i])
                                if sp_dir:
                                    tmp_dict = {sp_dir.group('mc_file').strip():g_cfg_params['tc_path']+'\\'+sp_dir.group('path').strip()}
                                    g_cfg_params['sp_file'].update(tmp_dict) 

                        if  6 == file_tag:
                            tmp_data = params.split(',')
                            file_name = ''
                            for i in range(len(tmp_data)):
                                sp_dir = re_sp_dir.match(tmp_data[i])
                                dire = re_dir.match(tmp_data[i])
                                if sp_dir:
                                    file_name = sp_dir.group('mc_file').strip()
                                    tmp_dict = {file_name:[g_cfg_params['tc_path']+'\\'+ sp_dir.group('path').strip()]}
                                    g_cfg_params['sp_dir'].update(tmp_dict) 
                                elif dire:
                                    g_cfg_params['sp_dir'][file_name].append(dire.group('path').strip())
                f.close()
            except IOError, e:
                print 'read_config_file(CHeckMC.cfg):'+`e`+'\n'
    return find_flag

#定义终端字体输出颜色，两位16进制，低位表示字体颜色，高位表示背景
FG_BLUE = 0X0B
FG_RED = 0X0C
FG_GREEN = 0X0A

class COLOR(object):
    def __init__(self):
        self.STD_INPUT_HANDLE = -10
        self.STD_OUTPUT_HANDLE = -11
        self.STD_ERROR_HANDLE = -12
        self.std_out_handle = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    #设置字体属性
    def set_cmd_text_color(self, color):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(self.std_out_handle, color)
        return Bool
    #重置字体颜色    
    def reset_color(self):
        self.set_cmd_text_color(FG_BLUE | FG_GREEN | FG_RED)

    #输出蓝颜色字体
    def print_blue(self, strings):
        self.set_cmd_text_color(FG_BLUE)
        sys.stdout.write(strings+'\n')
        self.reset_color()
    #输出绿颜色字体
    def print_red(self, strings):
        self.set_cmd_text_color(FG_RED)
        sys.stdout.write(strings+'\n')
        self.reset_color()
    #输出绿颜色字体    
    def print_green(self, strings):
        self.set_cmd_text_color(FG_GREEN)
        sys.stdout.write(strings+'\n')
        self.reset_color()


if __name__ == '__main__':
    ini_size = {}
    unuse_ini = []
    project = sys.argv[1]
    src_path= sys.argv[2]
    SIT_path= sys.argv[3]
    init_gloabl_params()
    
    find = read_config_file(project, src_path, SIT_path)
    if 0 == find:
        print '\nError: CheckMC.cfg is not exist.'
        exit(1)
    cfg_sp_dir = g_cfg_params['sp_dir']
    cfg_sp_file = g_cfg_params['sp_file']
    
    #解析指定目录所有的ini文件
    if {} !=  g_cfg_params['ini_path']:
        for root, dirs, files in os.walk(g_cfg_params['ini_path']):
            for f in files:
                size = 0
                if f.endswith('.ini'):
                    abs_f = root + '\\'+ f
                    size = parse_ini_file(abs_f)
                    ini_size.update({f.split('.')[0]:size})

    re_mc_file = re.compile('[\w][\w]MC_tc.h$')
    #解析所有的MC_tc.h文件
    cfg_mc = []
    if {} != cfg_sp_dir:
        for i in cfg_sp_dir:
            cfg_mc.append(i.split('.')[0])
    if {} != cfg_sp_file:
        for i in cfg_sp_file:
            cfg_mc.append(i.split('.')[0])
    if '' !=  g_cfg_params['tc_path']:
        for root, dirs, files in os.walk(g_cfg_params['tc_path']):
            for f in files:
                if re_mc_file.match(f):
                    skip = False
                    for i in range(len(cfg_mc)):
                        if f.__contains__(cfg_mc[i]):
                            skip = True
                            break
                    if skip:
                       continue
                    abs_f = root + '\\'+ f
                    parse_tc_file(abs_f)

    #解析配置文件中指定目录的机器常数
    if {} != cfg_sp_dir:
        for i in cfg_sp_dir:
            if g_cfg_params['sp_file'].has_key(i):
                mc_file = g_cfg_params['sp_file'][i]
                f = mc_file.split('\\')[len(mc_file.split('\\'))-1]
            else:
                f = i.split('.')[0] + '_tc.h'
                mc_file = get_file_full_name(f, True, i)

            if g_include_file_list.__contains__(f):
                g_include_file_list.remove(f)
            for root, dirs, files in os.walk(cfg_sp_dir[i][0]):
                for f in files:
                    if g_include_file_list.__contains__(f):
                        g_include_file_list.remove(f)
            parse_tc_file(mc_file, True, i)
        
    #解析配置文件指定文件的.h文件
    if {} != cfg_sp_file:
        for i in cfg_sp_file:
            parse_tc_file(cfg_sp_file[i])
            tmp = cfg_sp_file[i].split('\\')
            g_include_file_list.append(tmp[len(tmp)-1])
            
    print '***********************check result***********************'
    
    color = COLOR()
    #输出所有命名规范的ini和对应的STRUCT信息           
    for i in ini_size:
        struct = i+'_FILE_STRUCT'
        if g_struct_dict.has_key(struct):
            if ini_size[i] == g_struct_dict[struct]:
                color.print_green(i+'.ini=%d, '%ini_size[i] + struct + '=%d'%g_struct_dict[struct] + '   ** OK **')
            else:
                color.print_red(i+'.ini=%d, '%ini_size[i]+  struct+ '=%d'%g_struct_dict[struct] + '   --Error--')
        else:
            unuse_ini.append(i)
            
    #输出指定ini和指定STRUCT的信息       
    for i in ini_size:
        if g_cfg_params['sp_mc'].has_key(i+'.ini') and g_struct_dict.has_key(g_cfg_params['sp_mc'][i+'.ini']):
            if unuse_ini.__contains__(i):
                unuse_ini.remove(i)
            if ini_size[i] == g_struct_dict[g_cfg_params['sp_mc'][i+'.ini']]:
                color.print_green(i+'.imi=%d, '%ini_size[i] + g_cfg_params['sp_mc'][i+'.ini'] + '=%d'%g_struct_dict[g_cfg_params['sp_mc'][i+'.ini']] + '   ** OK **')
            else:
                color.print_red(i+'.imi=%d, '%ini_size[i] + g_cfg_params['sp_mc'][i+'.ini'] + '=%d'%g_struct_dict[g_cfg_params['sp_mc'][i+'.ini']] + '   --Error--')
        
    for i in range(len(unuse_ini)):
        color.print_blue(unuse_ini[i]+'.imi=%d, '%ini_size[unuse_ini[i]] + 'XX_STRUCT' + '   ??Unknown??')
        
    print '***********************check finish!***********************'
