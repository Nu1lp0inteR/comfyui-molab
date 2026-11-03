# comfyui-molab

在 [molab](https://molab.marimo.io)（marimo 的云端 notebook）里跑 ComfyUI 的模板，
用 cloudflared quick tunnel 把容器内的 `127.0.0.1:8188` 映射成公网地址，
这样就能在本地浏览器里打开完整的 ComfyUI 画布。

## 文件

| 文件 | 用途 |
|---|---|
| `comfyui_molab.py` | marimo notebook 源文件，可直接 `marimo edit` 打开，或用 molab 的 GitHub 镜像导入 |
| `comfyui_cells.txt` | 拆成 11 格的粘贴版，适合在 molab 网页编辑器里逐格粘 |

## 用法（molab 里）

1. 新建 notebook，先把右上角规格从 `4 CPU · 32 GiB` 切到带 GPU 的规格
2. 按 `comfyui_粘贴版.txt` 逐格粘贴（每个 `# ===== 第 N 格 =====` 之间是一格）
3. 点第 1 格运行 —— marimo 是反应式的，下游格会自动按依赖顺序跑完
4. 约 10–15 分钟后，隧道那格会给出 `https://xxx.trycloudflare.com`，浏览器打开即是 ComfyUI

## 注意

- molab **不暴露端口**，所以必须走 tunnel；地址每次重启都变
- 隧道**无鉴权**，用完跑最后一格关掉
- 会话结束（12 小时上限 / 空闲 90 分钟）后代码、torch、模型全部丢失，下次需重装重下
- Blackwell（RTX Pro 6000, sm_120）必须装 cu128 及以上的 torch wheel

## 安装自定义节点（插件）

在 `NODES` 列表里加仓库地址，脚本会 clone 到 `custom_nodes/` 并自动跑它的 `requirements.txt`：

```python
NODES = [
    "https://github.com/ltdrdata/ComfyUI-Manager",
]
```

**装完必须重启 ComfyUI**，但别点最后一格（会把隧道一起关掉，公网地址就变了）。只杀服务进程：

```python
subprocess.run(["pkill", "-f", "ComfyUI/main.py"])
```

然后回到「启动服务」那一格重新点运行。隧道进程还活着，地址不变，刷新画布就能看到新节点。

注意：装完会检查 `torch.cuda.is_available()`。如果变成 `False`，说明某个节点的依赖把 cu128 版 torch 换成了 CPU 版，重跑安装那一格即可恢复。

## 下载模型

```python
dl("https://huggingface.co/<用户>/<仓库>/resolve/main/<文件名>.safetensors", "checkpoints")
```

第二个参数是目标子目录：`checkpoints` / `vae` / `clip` / `loras` / `controlnet` / `upscale_models`。
需要鉴权时传第四个参数：`dl(url, "loras", None, {"Authorization": "Bearer hf_xxx"})`。

下完后在 ComfyUI 画布上按 `R` 刷新，模型才会出现在节点下拉框里。
