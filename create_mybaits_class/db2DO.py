#-*- encoding:utf8 -*-
import os

import mysqlutil

TYPE_MAP = {
    "varchar": "String",
    "bigint": "Long",
    "longtext": "String",
    "datetime": "Date",
    "int": "Integer",
    "tinyint": "Integer",
    "double": "Double",
    "date": "Date",
    "char": "String",
    "timestamp": "Date",
    "smallint": "Integer",
    "text": "String",
    "float": "Float",
    "time": "Date"
}


def db_create_class(database, table, path):
    print(database, path)
    # mysql都会有这个库，里面记录了所有数据表的详细信息
    util = mysqlutil.MySQLUtil(db='information_schema')
    result = util.query("select COLUMN_NAME,DATA_TYPE,COLUMN_COMMENT,COLUMN_KEY,EXTRA from `COLUMNS` where TABLE_SCHEMA = '%s' and TABLE_NAME='%s'"%(database, table))
    class_name = upper_first(field_name(table))
    # 根据业务自己定义pojo类名字
    class_do_name = class_name + "DO"
    class_list = []
    # 根据业务自己定义自己的包名
    class_list.append('package package tech.peche.%s.model;\r\n\r\n' % path)
    class_list.append('import java.util.Date;\r\n\r\n')
    class_list.append('public class %s {\r\n' % class_do_name)
    class_list = class_list + create_class_body(result)
    class_list.append('}\r\n')
    # 自己定义生成的路径
    f = open("/Users/peche/Desktop/" + class_do_name + ".java", 'wb')
    f.write((''.join(class_list)).encode('utf-8'))
    f.flush()
    f.close()

    class_mapper_name = class_name + "Mapper"
    class_list.clear()
    class_list.append('package package tech.peche.%s.mapper;\r\n\r\n' % path)
    class_list.append('import tech.peche.%s.model.%s;\r\n' % (path, class_do_name))
    class_list.append('import java.util.List;\r\n\r\n')
    class_list.append('public interface %s {\r\n\r\n' % class_mapper_name)
    class_list.append('%4sint insert(%s %s);\r\n\r\n' % (' ', class_do_name, lower_first(class_do_name)))
    class_list.append('%4sList<%s> selectEOByEO(%s %s);\r\n\r\n' % (' ', class_do_name, class_do_name, lower_first(class_do_name)))
    class_list.append('%4sint delete(%s %s);\r\n\r\n' % (' ', class_do_name, lower_first(class_do_name)))
    class_list.append('}')
    f = open("/Users/peche/Desktop/" + class_mapper_name + ".java", 'wb')
    f.write((''.join(class_list)).encode('utf-8'))
    f.flush()
    f.close()

    class_list.clear()
    class_list.append('<?xml version="1.0" encoding="UTF-8"?>\r\n')
    class_list.append('<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">\r\n')

    mapper_path = "tech.peche." + path + ".mapper." + class_mapper_name
    do_path = "tech.peche." + path + ".model." + class_do_name
    class_list = class_list + create_xml_body(result, mapper_path, do_path, table)
    f = open("/Users/peche/Desktop/" + class_name + ".xml", 'wb')
    f.write((''.join(class_list)).encode('utf-8'))
    f.flush()
    f.close()

    util.close()


def create_class_body(result):
    class_body = []
    for v in result:
        class_body.append('%4s/** %s */\r\n' % (' ', v['COLUMN_COMMENT']))
        class_body.append('%4sprivate %s %s;\r\n' % (' ', field_type(v['DATA_TYPE']), field_name(v['COLUMN_NAME'])))

    class_body.append("\r\n\r\n")
    # getter setter
    for v in result:
        java_type = field_type(v['DATA_TYPE'])
        filed_name = field_name(v['COLUMN_NAME'])
        method_suffix = upper_first(filed_name)
        class_body.append('%4spublic %s get%s() {\r\n' % (' ', java_type, method_suffix))
        class_body.append('%8sreturn this.%s;\r\n' % (' ', filed_name))
        class_body.append('%4s}\r\n' % ' ')

        class_body.append('%4spublic void set%s(%s %s) {\r\n' % (' ', method_suffix, java_type, filed_name))
        class_body.append('%8sthis.%s = %s;\r\n' % (' ', filed_name, filed_name))
        class_body.append('%4s}\r\n' % ' ')

    return class_body


def create_xml_body(result, mapper_path, do_path, table):
    class_body = []
    class_body.append('<mapper namespace="%s">\r\n' % mapper_path)
    class_body.append('%4s<resultMap id="result" type="%s">\r\n' % (' ', do_path))
    for v in result:
        sql_name = v['COLUMN_NAME']
        java_name = lower_first(field_name(sql_name))
        if sql_name == 'id':
            class_body.append('%8s<id property="id" column="id" />\r\n' % ' ')
        else:
            class_body.append('%8s<result property="%s" column="%s" />\r\n' % (' ', java_name, sql_name))
    class_body.append('%4s</resultMap>\r\n\r\n' % ' ')

    class_body.append('%4s<sql id="insert_columns">\r\n' % ' ')
    for v in result:
        sql_name = v['COLUMN_NAME']
        java_name = lower_first(field_name(sql_name))
        class_body.append('%8s<if test="%s != null">#{%s}</if>\r\n' % (' ', java_name, java_name))
    class_body.append('%4s</sql>\r\n\r\n' % ' ')

    class_body.append('%4s<sql id="insert_values">\r\n' % ' ')
    for v in result:
        sql_name = v['COLUMN_NAME']
        java_name = lower_first(field_name(sql_name))
        class_body.append('%8s<if test="%s != null">#{%s}</if>\r\n' % (' ', java_name, java_name))
    class_body.append('%4s</sql>\r\n\r\n' % ' ')

    class_body.append('%4s<insert id="insert" parameterType="%s" useGeneratedKeys="true" keyProperty="id">\r\n' % (' ', do_path))
    class_body.append('%8sinsert into %s(\r\n' % (' ', table))
    class_body.append('%12s<include refid="insert_columns" />\r\n' % ' ')
    class_body.append('%8s)values(\r\n' % ' ')
    class_body.append('%12s<include refid="insert_values" />\r\n' % ' ')
    class_body.append('%8s)\r\n' % ' ')
    class_body.append('%4s</insert>\r\n\r\n' % ' ')

    class_body.append('%4s<select id="selectEOByEO" parameterType="%s" resultMap="result">\r\n' % (' ', do_path))
    class_body.append('%8s<include refid="select_all_column" />\r\n' % ' ')
    class_body.append('%8sfrom %s\r\n' % (' ', table))
    class_body.append('%8s<where>\r\n' % ' ')
    for v in result:
        sql_name = v['COLUMN_NAME']
        java_name = lower_first(field_name(sql_name))
        if field_type(v['DATA_TYPE']) == "String":
            class_body.append('%12s<if test="%s != null and %s != ''"> and %s=#{%s} </if>\r\n' % (' ', java_name, java_name, sql_name, java_name))
        else:
            class_body.append('%12s<if test="%s != null"> and %s=#{%s} </if>\r\n' % (' ', java_name, sql_name, java_name))
    class_body.append('%8s</where>\r\n' % ' ')
    class_body.append('%4s</select>\r\n\r\n' % ' ')

    class_body.append('%4s<sql id="select_all_column">\r\n' % ' ')
    for v in result:
        sql_name = v['COLUMN_NAME']
        if sql_name == 'id':
            class_body.append('%8sselect ID\r\n' % ' ')
        else:
            class_body.append('%8s,%s\r\n' % (' ', sql_name))
    class_body.append('%4s</sql>\r\n\r\n' % ' ')

    class_body.append('%4s<delete id="delete" parameterType="%s">\r\n' % (' ', do_path))
    class_body.append('%8sdelete from %s\r\n' % (' ', table))
    class_body.append('%8swhere id=#{id}\r\n' % ' ')
    class_body.append('%4s</delete>\r\n\r\n' % ' ')

    class_body.append('</mapper>\r\n')
    return class_body


def field_type(db_type):
    return TYPE_MAP[db_type]


def field_name(line_world):
    new_str = ''
    for e in line_world.split('_'):
        new_str = new_str + upper_first(e)
    return lower_first(new_str)


def upper_first(str):
    return str[0].upper() + str[1:]


def lower_first(str):
    return str[0].lower() + str[1:]


if __name__ == "__main__":
    db_create_class('history_trace', 'es_struct', 'trace')

