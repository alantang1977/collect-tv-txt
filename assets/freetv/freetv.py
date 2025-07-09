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

# 从分类表构建频道分类字典
CHANNEL_CATEGORIES = {
    # 广东频道
    '广州综合': '广东频道',
    '广州新闻': '广东频道',
    '广州影视频道': '广东频道',
    '广州电视台影视频道': '广东频道',
    '广州电视台法治频道': '广东频道',
    '广州南国都市频道': '广东频道',
    '4K南国都市频道': '广东频道',
    '广州竞赛频道': '广东频道',
    '广东珠江': '广东频道',
    '广东新闻': '广东频道',
    '广东卫视': '广东频道',
    '广东民生': '广东频道',
    '大湾区卫视': '广东频道',
    '广东体育': '广东频道',
    '江门综合': '广东频道',
    '江门侨乡生活': '广东频道',
    '佛山综合': '广东频道',
    '深圳卫视': '广东频道',
    '汕头综合': '广东频道',
    '汕头经济': '广东频道',
    '汕头文旅': '广东频道',
    '茂名综合': '广东频道',
    '茂名公共': '广东频道',
    '4KUHD': '广东频道',
    '纪实人文': '广东频道',
    '纪实科教': '广东频道',
    '金鹰纪实': '广东频道',

    # 央视频道
    'CCTV1': '央视频道',
    'CCTV2': '央视频道',
    'CCTV3': '央视频道',
    'CCTV4': '央视频道',
    'CCTV5': '央视频道',
    'CCTV5+': '央视频道',
    'CCTV6': '央视频道',
    'CCTV7': '央视频道',
    'CCTV8': '央视频道',
    'CCTV9': '央视频道',
    'CCTV10': '央视频道',
    'CCTV11': '央视频道',
    'CCTV12': '央视频道',
    'CCTV13': '央视频道',
    'CCTV14': '央视频道',
    'CCTV15': '央视频道',
    'CCTV16': '央视频道',
    'CCTV17': '央视频道',
    'CCTV4K': '央视频道',
    'CCTV8K': '央视频道',

    # 卫视频道
    '山东卫视': '卫视频道',
    '湖南卫视': '卫视频道',
    '浙江卫视': '卫视频道',
    '东方卫视': '卫视频道',
    '北京卫视': '卫视频道',
    '江苏卫视': '卫视频道',
    '安徽卫视': '卫视频道',
    '重庆卫视': '卫视频道',
    '四川卫视': '卫视频道',
    '东南卫视': '卫视频道',
    '深圳卫视': '卫视频道',
    '广东卫视': '卫视频道',
    '广西卫视': '卫视频道',
    '厦门卫视': '卫视频道',
    '南方卫视': '卫视频道',
    '甘肃卫视': '卫视频道',
    '贵州卫视': '卫视频道',
    '河北卫视': '卫视频道',
    '河南卫视': '卫视频道',
    '黑龙江卫视': '卫视频道',
    '湖北卫视': '卫视频道',
    '江西卫视': '卫视频道',
    '吉林卫视': '卫视频道',
    '内蒙古卫视': '卫视频道',
    '辽宁卫视': '卫视频道',
    '宁夏卫视': '卫视频道',
    '青海卫视': '卫视频道',
    '天津卫视': '卫视频道',
    '海南卫视': '卫视频道',
    '新疆卫视': '卫视频道',
    '云南卫视': '卫视频道',
    '西藏卫视': '卫视频道',
    '海峡卫视': '卫视频道',
    '兵团卫视': '卫视频道',
    '黄河卫视': '卫视频道',
    '安多卫视': '卫视频道',
    '康巴卫视': '卫视频道',
    '农林卫视': '卫视频道',
    '三沙卫视': '卫视频道',
    '延边卫视': '卫视频道',
    '山东齐鲁卫视': '卫视频道',

    # 港澳台
    '翡翠台': '港澳台',
    '凤凰中文': '港澳台',
    '凤凰资讯': '港澳台',
    '凤凰香港': '港澳台',
    '凤凰卫视': '港澳台',
    '香港卫视': '港澳台',
    'TVBS欢乐': '港澳台',
    'TVBS亚洲': '港澳台',
    'TVBS新闻': '港澳台',
    'J2': '港澳台',
    'Viutv': '港澳台',
    '明珠台': '港澳台',
    '三立台湾': '港澳台',
    '无线新闻': '港澳台',
    '三立新闻': '港澳台',
    '纬来体育': '港澳台',
    '纬来育乐': '港澳台',
    '东森综合': '港澳台',
    '东森超视': '港澳台',
    '东森电影': '港澳台',
    'Now剧集': '港澳台',
    'Now华剧': '港澳台',
    '靖天资讯': '港澳台',
    '星卫娱乐': '港澳台',
    '卫视卡式': '港澳台',
    '广东珠江': '港澳台',
    '广东体育': '港澳台',
    '广东民生': '港澳台',
    '广东综艺': '港澳台',
    '广东影视': '港澳台',
    '经济科教': '港澳台',
    '岭南戏曲': '港澳台',
    '现代教育': '港澳台',
    '大湾区卫视': '港澳台',

    # 少儿频道
    '东森幼幼': '少儿频道',
    'iFun动漫': '少儿频道',
    'momo亲子': '少儿频道',
    '黑莓动画': '少儿频道',
    '嘉佳少儿': '少儿频道',
    '卡酷少儿': '少儿频道',
    '动漫秀场': '少儿频道',
    '哈哈炫动': '少儿频道',
    '金鹰卡通': '少儿频道',
    '优漫卡通': '少儿频道',
    '靖洋卡通': '少儿频道',
    '广东少儿': '少儿频道',

    # 影视频道
    'CHC动作电影': '影视频道',
    'CHC高清电影': '影视频道',
    'CHC家庭影院': '影视频道',
    'NewTV惊悚悬疑': '影视频道',
    'NewTV动作电影': '影视频道',
    '黑莓电影': '影视频道',
    '纬来电影': '影视频道',
    '靖天映画': '影视频道',
    '靖天戏剧': '影视频道',
    '星卫娱乐': '影视频道',
    '艾尔达娱乐': '影视频道',
}

CATEGORY_ORDER = [
    '广东频道',
    '央视频道',
    '卫视频道',
    '港澳台',
    '少儿频道',
    '影视频道',
    '其他'
]

def classify_channel_name(name):
    return CHANNEL_CATEGORIES.get(name, '其他')

def category_sort_key(name):
    cat = classify_channel_name(name)
    try:
        cat_idx = CATEGORY_ORDER.index(cat)
    except Exception:
        cat_idx = 99
    return (cat_idx, name)

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

    # 其他频道
    return (999, name)

# 对频道列表做归类和排序
def group_and_sort_channels(channels):
    grouped = {cat: [] for cat in CATEGORY_ORDER}
    for line in channels:
        if "," not in line:
            continue
        channel_name = line.split(',')[0].strip()
        category = classify_channel_name(channel_name)
        grouped.setdefault(category, []).append(line)
    # 对每个类别内部排序
    for cat in grouped:
        grouped[cat] = sorted(grouped[cat], key=lambda x: extract_channel_number(x.split(',')[0]))
    # 按优先级输出
    sorted_all = []
    for cat in CATEGORY_ORDER:
        sorted_all.extend(grouped.get(cat, []))
    return sorted_all

# 主函数
def main():
    global freetv_dictionary, freetv_dictionary_cctv, freetv_dictionary_ws
    global freetv_cctv_lines, freetv_ws_lines, freetv_other_lines

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

    # 按分类和排序规则排序
    sorted_lines = group_and_sort_channels(freetv_lines_renamed)

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

    # 各分类也按归类排序
    freetv_cctv_lines = group_and_sort_channels(freetv_cctv_lines)
    freetv_ws_lines = group_and_sort_channels(freetv_ws_lines)
    freetv_other_lines = group_and_sort_channels(freetv_other_lines)

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
