# WAR-65 原始实验执行证据（Eric 本地）

权威宿主：**Eric**，项目根目录 `/home/sean/projects/canvas-lab`。此处保留不可覆盖的 C/D 原始规则隔离文本回放数据；研究正文与结论见上级目录 Markdown。

## 冻结证据包

- 压缩包：`war-65-cd-original-execution-20261111.tar.gz`
- SHA256：`3cd2eb5b84653aaa384612b05f49166283454faa17cff1a407125a784629cc51`
- 大小：2,229,743 bytes
- TAR 中 **137 个文件条目**，每文件原始 SHA256 和字节数见 `war-65-cd-member-manifest.json`
- 来源：Terry `/home/ubuntu/research/xia-59/directorskill-20261109/war-65-cd-raw-evidence-transfer-20261111.tar.gz`；Eric 接收后整体 SHA 相同、逐项解包读取，检查安全路径与冻结输出 SHA
- 含 C 的原始运行数据 66 个文件、D-assisted v1 的原始运行数据 68 个文件、D 原剧本、D 辅助输入，以及独立原 C 证据包
- 内嵌 C 原证据包 `war-65-script-C-raw-evidence-20261109.tar.gz` 的 SHA256：`272523022e3361dc7a46590852317deb8677b1b417e89f5d33eb8df2b3814266`；与 WAR-65 Linear 旧 Resources 所记哈希一致
- D 原剧本 SHA256：`65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d`
- D Step2/3/5/6/7 原始输出 SHA256 均与上级独立 Markdown 以及 Terry 源证据一致

## 包内结构

- `war-65-script-C/step{2,3,5,6,7}/`：C 冻结剧本、原始 Skill/参考、输入 Prompt、输出、日志、manifest、exit codes 等
- `war-65-script-D-assisted-v1/step{2,3,5,6,7}/`：D 同类证据；Step4 跳过决策见 Step5–7 目录
- `war-65-script-C-raw-evidence-20261109.tar.gz`：C 原始独立冻结压缩包
- `D-assisted-v1-input.md` 与 `source-script-D/script-D.txt`：D 冻结输入原件

## 使用与校验

在 Eric 项目根目录执行：

```bash
sha256sum docs/validation/WAR-65/evidence/war-65-cd-original-execution-20261111.tar.gz
tar -tzf docs/validation/WAR-65/evidence/war-65-cd-original-execution-20261111.tar.gz | head -30
tar -xOf docs/validation/WAR-65/evidence/war-65-cd-original-execution-20261111.tar.gz war-65-script-D-assisted-v1/step7/step7-output.txt
```

逐文件证据清单只用于完整性复核，不代表文本内容已做事实真实性保证。原版 Skill 文本回放**不是正式安装 Skill 的生产调用**。

## 保留与备份策略

压缩包属于原始运行日志与二进制归档，**本地保存，不直接提交到 Git**；同目录 `.gitignore` 防止无意提交。研究结论、归档说明与 SHA manifest 由 Git 版本管理。未验证远端备份或灾备完成；不可仅凭 Git 文本提交声称原始证据已异机备份。

Terry 旧原始目录及 Linear 原 Resources **暂时保留，未删除**。用户确认备份策略后才考虑清理。所有新研究正文与原始证据默认写入 Eric，而非 Terry。
