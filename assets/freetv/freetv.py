import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime, timedelta, timezone

# 全局变量
freetv_lines = []
freetv_cctv_lines = []
freetv_ws_lines = []
freetv_other_lines = []

# 读取修改频道名称的方法
def load_modify_name(filename):
    corrections = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            correct_name = parts[0]
            for name in parts[1:]:
                corrections[name] = correct_name
    return corrections

# 纠错频道名称
def rename_channel(corrections, data):
    corrected_data = []
    for line in data:
        name, url = line.split(',', 1)
        if name in corrections and name != corrections[name]:
            name = corrections[name]
        corrected_data.append(f"{name},{url}")
    return corrected_data

# 读取文本文件的方法
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# 组织过滤后的频道信息
def process_channel_line(line):
    if "#genre#" not in line and "," in line and "://" in line:
        channel_name, channel_address = line.split(',', 1)
        channel_address = channel_address + "$" + channel_name.strip().replace(' ', '_')
        line = channel_name + "," + channel_address
        freetv_lines.append(line.strip())

# 处理URL
def process_url(url):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        with urllib.request.urlopen(req) as response:
            data = response.read()
            text = data.decode('utf-8')
            lines = text.split('\n')
            print(f"读取行数: {len(lines)}")
            for line in lines:
                if "#genre#" not in line and "," in line and "://" in line:
                    channel_name, channel_address = line.split(',', 1)
                    if channel_name in freetv_dictionary:
                        process_channel_line(line)
    except Exception as e:
        print(f"处理URL时发生错误：{e}")

# 清理URL
def clean_url(url):
    last_dollar_index = url.rfind('$')
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

# 提取频道数字
def extract_channel_number(name):
    # 处理CCTV频道
    cctv_match = re.match(r'^CCTV-?(\d+)([A-Za-z]*)$', name)
    if cctv_match:
        num_part = cctv_match.group(1)
        alpha_part = cctv_match.group(2)
        # 处理特殊数字
        special_nums = {'新闻': 13, '少儿': 14, '音乐': 15, '国防军事': 7}
        if num_part in special_nums:
            num = special_nums[num_part]
        else:
            try:
                num = int(num_part)
            except ValueError:
                return (0, name)  # 无法转换为数字时返回0
            
        # 处理数字后的字母部分，如CCTV5+
        if alpha_part:
            return (100 + num, name)  # 给带字母的CCTV频道更高权重
        return (num, name)
    
    # 处理数字频道，如"北京卫视2"
    num_match = re.search(r'(\d+)$', name)
    if num_match:
        try:
            return (200 + int(num_match.group(1)), name)  # 普通数字频道权重200+
        except ValueError:
            pass
    
    # 处理"卫视"频道
    if "卫视" in name:
        return (300, name)
    
    # 处理"教育"频道
    if "教育" in name:
        return (400, name)
    
    # 处理"电影"频道
    if "电影" in name:
        return (500, name)
    
    # 处理"体育"频道
    if "体育" in name:
        return (600, name)
    
    # 处理"新闻"频道
    if "新闻" in name:
        return (700, name)
    
    # 处理"综合"频道
    if "综合" in name:
        return (800, name)
    
    # 其他频道
    return (999, name)

# 主函数
def main():
    global freetv_dictionary, freetv_dictionary_cctv, freetv_dictionary_ws
    
    # 读取配置文件
    print("正在读取配置文件...")
    rename_dic = load_modify_name('assets/freetv/freetv_rename.txt')
    freetv_dictionary = read_txt_to_array('assets/freetv/freetvlist.txt')
    freetv_dictionary_cctv = read_txt_to_array('assets/freetv/freetvlist_cctv.txt')
    freetv_dictionary_ws = read_txt_to_array('assets/freetv/freetvlist_ws.txt')
    
    # 处理URL
    urls = ["https://freetv.fun/test_channels_original_new.txt"]
    for url in urls:
        print(f"正在处理URL: {url}")
        process_url(url)
    
    # 获取当前时间
    utc_time = datetime.now(timezone.utc)
    beijing_time = utc_time + timedelta(hours=8)
    formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")
    version = formatted_time + ",url"
    
    # 处理并保存全集文件
    print("正在处理频道数据...")
    freetv_lines_renamed = rename_channel(rename_dic, freetv_lines)
    
    # 按特定规则排序
    sorted_lines = sorted(freetv_lines_renamed, key=lambda x: extract_channel_number(x.split(',')[0]))
    
    # 分批再次保存
    for line in sorted_lines:
        if "#genre#" not in line and "," in line and "://" in line:
            channel_name = line.split(',')[0].strip()
            channel_address = clean_url(line.split(',')[1].strip())
            line = channel_name + "," + channel_address

            if channel_name in freetv_dictionary_cctv:
                freetv_cctv_lines.append(line.strip())
            elif channel_name in freetv_dictionary_ws:
                freetv_ws_lines.append(line.strip())
            else:
                freetv_other_lines.append(line.strip())
    
    # 按特定规则排序各分类
    freetv_cctv_lines = sorted(freetv_cctv_lines, key=lambda x: extract_channel_number(x.split(',')[0]))
    freetv_ws_lines = sorted(freetv_ws_lines, key=lambda x: extract_channel_number(x.split(',')[0]))
    freetv_other_lines = sorted(freetv_other_lines, key=lambda x: extract_channel_number(x.split(',')[0]))
    
    # 构建输出内容
    output_lines = ["更新时间,#genre#"] + [version] + ['\n'] + ["freetv,#genre#"] + sorted_lines
    
    output_lines_cctv = ["更新时间,#genre#"] + [version] + ['\n'] + ["freetv_cctv,#genre#"] + freetv_cctv_lines
    output_lines_ws = ["更新时间,#genre#"] + [version] + ['\n'] + ["freetv_ws,#genre#"] + freetv_ws_lines
    output_lines_other = ["更新时间,#genre#"] + [version] + ['\n'] + ["freetv_other,#genre#"] + freetv_other_lines
    
    # 保存文件
    output_files = [
        ("assets/freetv/freetv_output.txt", output_lines),
        ("assets/freetv/freetv_output_cctv.txt", output_lines_cctv),
        ("assets/freetv/freetv_output_ws.txt", output_lines_ws),
        ("assets/freetv/freetv_output_other.txt", output_lines_other)
    ]
    
    for file_path, lines in output_files:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(line + '\n')
            print(f"已成功保存文件: {file_path}")
        except Exception as e:
            print(f"保存文件 {file_path} 时发生错误：{e}")
    
    print("所有操作已完成!")

if __name__ == "__main__":
    main()    
