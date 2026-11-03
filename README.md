# comfyui-molab

在 [molab](https://molab.marimo.io)（marimo 云端 notebook）里跑 ComfyUI，用 **ngrok** 把容器内的
`127.0.0.1:8188` 映射成公网地址，浏览器打开就是完整画布。

## 文件

| 文件 | 用途 |
|---|---|
| `comfyui_molab.py` | marimo notebook 源文件，可用 molab 的 GitHub 镜像直接导入 |
| `comfyui_cells.txt` | 拆成 13 格的粘贴版，适合手动逐格粘 |

## 每格做什么

| 格 | 内容 | 什么时候重跑 |
|---|---|---|
| 4 | 环境体检（GPU / 磁盘 / 当前状态） | 想确认状态时 |
| 5 | 安装 ComfyUI + torch cu128 | 新会话第一次 |
| 7 | 下载模型 | 新会话第一次 |
| 9 | 安装自定义节点 | 新会话第一次 |
| **10** | **★ 启动 ComfyUI** | 服务挂了 |
| **11** | **★★ 生成公网地址（ngrok）** | 地址失效 / 隧道断了 |
| 12 | 状态检查与排错 | 出问题时 |
| 13 | 停止服务（需勾选） | 用完 |

## 中断之后从哪继续

| 情况 | 从哪开始 |
|---|---|
| 服务或隧道挂了，notebook 还开着 | 只跑第 10 格，再跑第 11 格 |
| 改了模型列表 | 只跑第 7 格（已下好的自动跳过） |
| 加了新节点 | 第 9 格 → 第 10 格 |
| 容器被回收 / 换会话 | 从第 1 格重来 |

## 第一次使用

1. 打开 https://dashboard.ngrok.com/signup 注册，取 authtoken
2. 把 token 填进第 11 格的 `NGROK_TOKEN`，跑一次
3. 跑通后建议清空该行（notebook 公开可读），token 已存在容器内 `~/.config/ngrok/ngrok.yml`
4. 切 GPU 规格 → 从第 1 格跑到第 11 格

## 踩过的坑（都已在代码里处理）

- **molab 不暴露端口**，必须走隧道
- **cloudflared 不可用**：它连 Cloudflare 边缘固定用 7844，molab 沙箱封了该端口
- **bore.pub 不可用**：服务端连不上（7835 通，但 bore.pub 超时）
- **pinggy 只能 60 分钟**，ngrok 免费版不限会话时长
- **marimo 只渲染单元格最后一个顶层表达式**，`mo.md` 别写在 `if` 分支里
- **带副作用的格会被"全部运行"自动执行**，停止操作必须加勾选框
- **torch 必须是 cu128 及以上**，否则 Blackwell（sm_120）跑不了

## 限制

- molab 会话最长 12 小时，空闲 90 分钟回收
- 回收后 ComfyUI、torch、模型全部消失，下次需重装重下
- ngrok 免费版：1 个 agent、地址每次重启变化、首次访问有提示页
