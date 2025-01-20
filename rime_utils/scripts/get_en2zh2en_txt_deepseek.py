import os
import sys
import re
import shutil
from pathlib import Path
from typing import Set, Dict, List
from timer import timer  # 假设这是一个计时器装饰器
from data.char_8105 import char_8105  # 假设这是一个字符集

# 获取词典表头
def get_en_dict_header(filename: str) -> str:
    return f"# {filename}\n# Generated by get_en_dict.py\n\n"

# 过滤无效字符
def filter_invalid_chars(text: str) -> str:
    """
    过滤掉无效字符（如标点符号、数字、英文字母等）。
    """
    invalid_chars = '!—:。：、…→;abcdefghijklmnopqrstuvwxyz.v（）()[]〔〕？！《》■／～ABCDEFGHIJKLMNOPQRSTUVWXYZ+/<\'"1234567890“〈〉【】'
    return ''.join(ch for ch in text if ch not in invalid_chars)

# 处理单行数据
def process_line(line: str, res_dict: Dict[str, str], res_set: Set[str]) -> None:
    """
    处理单行数据，提取单词和解释，并更新结果字典和集合。
    """
    line_list = re.split(r'\t+', line.strip())
    if len(line_list) < 2:
        print(f"⚠️  Invalid line format: {line}")
        return

    word = line_list[0]
    code = line_list[1].strip()
    code = re.sub(r'[，；,]', ' ', code)  # 替换中文标点为空格
    code = re.sub(r'\s+', ' ', code)  # 合并多个空格
    weight = line_list[2] if len(line_list) > 2 else '0'

    # 过滤无效字符并拆分解释
    code_list = [
        zh for zh in code.split(' ')
        if len(zh) <= 60 and all(ch in char_8105 for ch in zh)
    ]

    # 更新结果字典和集合
    for zh in code_list:
        if zh:
            if zh not in res_set:
                res_dict[zh] = word + ' '
                res_set.add(zh)
            elif word not in res_dict[zh]:
                res_dict[zh] += word + ' '

# 主函数
@timer
def convert(src_dir: Path, out_dir: Path, file_endswith_filter: str, multifile_out_mode: int) -> None:
    """
    遍历源文件夹，处理文件并生成词典。
    """
    dict_num = 0
    res_dict: Dict[str, str] = {}
    res_set: Set[str] = set()
    lines_total: List[str] = []

    # 遍历源文件夹
    for file_path in src_dir.iterdir():
        if file_path.is_file() and file_path.name.endswith(file_endswith_filter):
            dict_num += 1
            print(f'☑️  已加载第 {dict_num} 份码表 » {file_path}')

            with open(file_path, 'r', encoding='utf-8') as f:
                lines_total.extend(f.readlines())

    # 处理每一行数据
    for line in lines_total:
        process_line(line, res_dict, res_set)

    # 按最前面的汉字长度分组
    word_len_dict: Dict[int, List[str]] = {}
    for zh, en in res_dict.items():
        word_len = len(zh)  # 最前面的汉字长度
        if word_len not in word_len_dict:
            word_len_dict[word_len] = []
        word_len_dict[word_len].append(f'{zh}\t{zh} {en}\n')

    # 按最前面的汉字长度排序并生成最终结果
    lines_list: List[str] = []
    for word_len in sorted(word_len_dict.keys()):
        lines_list.extend(word_len_dict[word_len])

    # 去重并排序
    unique_list = list(dict.fromkeys(lines_list))  # 去重
    unique_list.sort(key=lambda x: x.casefold())  # 不区分大小写排序

    # 写入输出文件
    out_file = 'zh2en.txt'
    with open(out_dir / out_file, 'w', encoding='utf-8') as o:
        print(f'✅  » 已合并排序去重英文码表 - 共 {len(lines_list)} » {len(unique_list)} 条')
        o.write(get_en_dict_header(out_file))  # 添加表头
        o.write(''.join(unique_list))

# 主程序入口
if __name__ == '__main__':
    current_dir = Path.cwd()
    src = '../english-vocabulary'
    out = 'out'
    file_endswith_filter = '.txt'
    multifile_out_mode = 0

    # 命令行参数解析
    for i, arg in enumerate(sys.argv):
        if arg == "-i":
            src = sys.argv[i + 1]
        elif arg == '-o':
            out = sys.argv[i + 1]
        elif arg == '-f':
            file_endswith_filter = sys.argv[i + 1]
        elif arg == '-m':
            multifile_out_mode = sys.argv[i + 1]

    src_dir = current_dir / src  # 源文件夹路径
    out_dir = current_dir / out  # 输出文件夹路径

    # 清理并创建输出文件夹
    if out_dir.exists():
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)

    # 执行转换
    convert(src_dir, out_dir, file_endswith_filter, multifile_out_mode)