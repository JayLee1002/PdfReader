# -*- coding: utf-8 -*-

import sys

def translate(string):
    return string + " " + string

if __name__ == '__main__':
    # 检查是否提供了命令行参数
    if len(sys.argv) != 2:
        print("请提供一个字符串作为命令行参数。")
    else:
        # 获取命令行参数
        input_string = sys.argv[1]

        # 调用 translate 函数
        result = translate(input_string)

        # 输出结果
        print("翻译结果:", result)

        # 将结果写入文件，指定编码为 UTF-8
        with open('tmp_trans.txt', 'w', encoding='utf-8') as file:
            file.write(result)

        print("结果已写入 tmp_trans.txt 文件。")
