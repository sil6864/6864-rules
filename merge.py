import requests
from datetime import datetime

def download_rules(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def save_rules(rules, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"! Merged AdBlock Rules (AdBlock DNS + anti-AD)\n")
        f.write(f"! Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"! Total unique rules: {len(rules)}\n")
        f.write("\n".join(sorted(rules)))

def main():
    source1 = "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt"
    source2 = "https://anti-ad.net/easylist.txt"
    
    # 下载规则文件
    rules1 = download_rules(source1)
    rules2 = download_rules(source2)
    
    # 提取有效规则（非注释/空行）
    active_rules = set()
    for line in rules1 + rules2:
        if line and not line.startswith('!') and not line.startswith('#'):
            active_rules.add(line.strip())
    
    # 保存合并后的规则
    save_rules(active_rules, "rules.txt")

if __name__ == "__main__":
    main()
