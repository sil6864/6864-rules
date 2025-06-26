import requests
from datetime import datetime
import re

def download_rules(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def is_valid_rule(line):
    """检查规则是否有效且格式正确"""
    # 跳过空行、注释行
    if not line or line.startswith('!') or line.startswith('#'):
        return False
    
    # 检查基本规则格式
    if line.startswith(('||', '@@', '/')):
        return True
    
    # 检查特殊格式规则（带修饰符）
    if re.match(r'^[\|\@]{0,2}[a-z0-9*\.\/]+\^\$[a-z]+=', line):
        return True
    
    return False

def format_rule(rule):
    """修正规则格式问题"""
    # 正则规则必须以/结束
    if rule.startswith('/^') and not rule.endswith('/'):
        # 处理带修饰符的情况
        if '$' in rule:
            parts = rule.split('$', 1)
            return f"{parts[0]}/${parts[1]}"
        return rule + '/'
    
    # 处理带修饰符的规则
    if '$' in rule and not re.search(r'\/\$\w+', rule):
        if re.search(r'\^\$\w+', rule):
            return rule
        
        parts = rule.split('$', 1)
        if parts[0].endswith('^'):
            return f"{parts[0]}${parts[1]}"
        
        if parts[0].endswith('/'):
            return f"{parts[0]}${parts[1]}"
    
    return rule

def save_rules(rules, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("! Merged AdBlock Rules (AdBlock DNS + anti-AD)\n")
        f.write(f"! Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"! Total unique rules: {len(rules)}\n")
        f.write("! Sources:\n")
        f.write("! - https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt\n")
        f.write("! - https://anti-ad.net/easylist.txt\n\n")
        
        # 分组排序：先放例外规则(@@)，再放域名规则(||)，最后是正则规则(/)
        exception_rules = sorted([r for r in rules if r.startswith('@@')])
        domain_rules = sorted([r for r in rules if r.startswith('||') and not r.startswith('@@')])
        regex_rules = sorted([r for r in rules if r.startswith('/')])
        
        f.write("\n".join(exception_rules + domain_rules + regex_rules))

def main():
    source1 = "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt"
    source2 = "https://anti-ad.net/easylist.txt"
    
    # 下载规则文件
    rules1 = download_rules(source1)
    rules2 = download_rules(source2)
    
    # 提取并验证规则
    active_rules = set()
    for line in rules1 + rules2:
        stripped = line.strip()
        if is_valid_rule(stripped):
            formatted = format_rule(stripped)
            active_rules.add(formatted)
    
    # 保存合并后的规则
    save_rules(active_rules, "rules.txt")

if __name__ == "__main__":
    main()
