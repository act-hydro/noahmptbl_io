import numpy as np
import re

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def string_data_format(s):
    if '"' in s:
        format = "%s"
    elif 'e' in s:
        num_list = s.split('e')
        if '.' in s:
            num_digit = len(num_list[0].split('.')[0]) + len(num_list[0].split('.')[1]) - 1
            if num_digit <1:
                num_digit = 1
        else:
            num_digit = 1
        format = "%."+"%i"%(num_digit) + "e"
    elif 'E' in s:
        num_list = s.split('E')
        if '.' in s:
            num_digit = len(num_list[0].split('.')[1])
            if num_digit <1:
                num_digit = 1
        else:
            num_digit = 1
        format = "%."+"%i"%(num_digit) + "E"
    elif '.' in s:
        num_digit = len(s.split('.')[1])
        if num_digit == 0:
            num_digit = 1
        format = "%."+"%i"%(num_digit) + "f"
    else:
        format = "%i"
    return format

def truncate_string(input_str):
    """
    Truncate a string after the last occurrence of a number or a dot.
    Args:
        input_str (str): The input string to truncate.
    Returns:
        str: The truncated string.
    """
    last_index = max(input_str.rfind('.'), input_str.rfind('0'), input_str.rfind('1'), 
                     input_str.rfind('2'), input_str.rfind('3'), input_str.rfind('4'),
                     input_str.rfind('5'), input_str.rfind('6'), input_str.rfind('7'), 
                     input_str.rfind('8'), input_str.rfind('9'))
    if last_index == -1:
        return input_str,''
    else:
        return input_str[:last_index + 1],input_str[last_index+1:]

def read_noahmp_table(fname):
    file1 = open(fname, 'r')
    # Using readlines()
    Lines = file1.readlines()
    count = 0
    # Strips the newline character
    dict_format = {}
    dict_value  = {}
    dict_parameters_section = {}
    dict_parameters_format_section = {}
    for line in Lines:
        count += 1
        # print("{}: {}".format(count, line))
        if len(line.strip())>0:
            # print(line.strip()[0])
            if line.strip()[0] == '&':
                # print(line)
                # print("section start for: %s"%line.strip()[1:])
                section_name = line.strip()[1:]
                dict_value.update({count:line})
                dict_format.update({count:''})
                dict_parameters = {}
                dict_parameters_format = {}
            elif line.strip()[0] == '!':
                dict_value.update({count:line})
                dict_format.update({count:''})
            elif line.strip()[0].isalpha():
                param_value_list = []
                whether_exist_comment = False
                if '!' in line:
                    line_split_exc = line.split('!')
                    # print(line_split_exc)
                    param_value_list.append("!"+line_split_exc[-1])
                    # print(param_value_list)
                    line = line_split_exc[0]
                    whether_exist_comment = True
                line_split_equal = line.split('=')
                # print(line_split_equal)
                param_name = line_split_equal[0]
                param_name_strip = param_name.strip()
                # if comment exists: we need to update the last string
                data_str,end_str = truncate_string(line_split_equal[1])
                if whether_exist_comment:
                    post_str = end_str + param_value_list[0]
                    param_value_list = []
                else:
                    post_str = end_str
                param_value_list.append(post_str)
                # start extract variables from
                num_values_list = []
                format_list = []
                if ',' in data_str:
                    values = re.split(',|\n', data_str)
                    for value in values:
                        # if has_numbers(value):
                        value_num = value
                        num = np.float(value_num)
                        value_num_strip = value_num.strip()
                        value_num_strip_format = string_data_format(value_num_strip)
                        value_num_format = value_num.replace(value_num.strip(), value_num_strip_format)
                        num_values_list.append(num)
                        format_list.append(value_num_format)
                        # else:
                        #     num_values_list.append(value)
                        #     format_list.append('')
                else:
                    value_num = data_str
                    if '"' in value_num:
                        num_values_list.append(value_num)
                        format_list.append('')
                    else:
                        num = np.float(value_num)
                        value_num_strip = value_num.strip()
                        value_num_strip_format = string_data_format(value_num_strip)
                        value_num_format = value_num.replace(value_num.strip(), value_num_strip_format)
                        num_values_list.append(num)
                        format_list.append(value_num_format)
                # print(num_values_list,format_list)
                dict_parameters.update({"%s:%s"%(section_name,param_name_strip):num_values_list})
                dict_parameters_format.update({"%s:%s"%(section_name,param_name_strip):[param_name]+format_list+[post_str]})
                dict_value.update({count:"%s:%s"%(section_name,param_name_strip)})
                dict_format.update({count:'customized'})
            elif line.strip()[0] == '/':
                dict_parameters_section.update({section_name:dict_parameters})
                dict_parameters_format_section.update({section_name:dict_parameters_format})
                dict_value.update({count:line})
                dict_format.update({count:''})
            else:
                dict_value.update({count:line})
                dict_format.update({count:''})
        else:
            dict_value.update({count:line})
            dict_format.update({count:''})
    return dict_value,dict_format,dict_parameters_format_section,dict_parameters_section

def write_noahmptbl(ofilename,dict_value,dict_format,dict_parameters_format_section,dict_parameters_section):
    ofile = open(ofilename, 'w')
    for key in dict_format.keys():
        l_format = dict_format[key]
        if l_format == '':
            line = dict_value[key]
        else:
            vkey = dict_value[key]
            section = vkey.split(':')[0]
            param_value = dict_parameters_section[section][vkey]
            param_v_format = dict_parameters_format_section[section][vkey]
            # print(param_value, param_v_format)
            len_format = len(param_v_format)
            len_value = len(param_value)
            line = ''
            for j,item in enumerate(param_v_format):
                if j == 0:
                    line += item
                    line += '='
                elif j == len_format-1:
                    line += item
                else:
                    if item == '':
                        line += param_value[j-1]
                    else:
                        line += item%param_value[j-1]
                    if j-1 < len_value-1:
                        line += ','
            # print([line])
        ofile.write(line)
    ofile.close()
