import os
import shutil
from pathlib import Path
# from scripts.old.header import get_header
from data.pinyin8105 import pinyin8105


current_dir = Path.cwd()

src_dir = current_dir / 'meta'
out_dir = current_dir / 'out'
FILE_ENDSWITH_FILETER = 'wubi86单字10万.dict.yaml'

# 如果存在输出文件，先删除
if os.path.exists(out_dir):
	shutil.rmtree(out_dir)
os.mkdir(out_dir)

def get_wubi86yd(SRC_DIR = src_dir, OUT_DIR = out_dir, FILE_ENDSWITH_FILETER = FILE_ENDSWITH_FILETER):
	# 遍历源文件夹文件，处理
	for file_path in SRC_DIR.iterdir():
		if file_path.is_file():
			file_name = file_path.name
			# print(file_name)
			if not file_name.endswith(FILE_ENDSWITH_FILETER):
				continue
			# print(file_name)

			src_file_path = SRC_DIR / file_name
			out_file_path = OUT_DIR / file_name
			
			# 添加词库头
			# with open(out_file_path, 'a', encoding='utf-8') as o:
			#     o.write(get_header(file_name))


			with open(src_file_path, 'r', encoding='utf-8') as f:
				num = 0
				res = ''
				res_dict = {}
				for line in f.readlines():
					if not line.startswith(('#', ' ', '\n')):    # 忽略非词表行
						line_arr = line.strip().split('\t')
						
						key = line_arr[0]
						val = line_arr[1]

						if len(key) == 1:
							if key not in res_dict.keys():
								res_dict[key] = val
							else:
								if len(val) > len(res_dict[key]):
									res_dict[key] = val

							# res = res + f'{line_arr[1]}\t{line_arr[0]}\n'
				
				# for key, value in res_dict.items():
				# 	res = res + f'{key}\t{value}\n'
				return res_dict