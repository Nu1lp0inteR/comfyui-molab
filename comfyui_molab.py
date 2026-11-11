import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # ComfyUI on molab · v2（cpolar 版）

    molab 不暴露端口，所以用 **cpolar** 把容器内的 `127.0.0.1:8188` 映射成公网 https 地址，
    浏览器打开就是完整画布。

    ---

    ## 每格干什么、什么时候重跑

    | 格 | 内容 | 什么时候重跑 |
    |---|---|---|
    | 4 | 环境体检（GPU / 磁盘 / 当前状态） | 想确认状态时 |
    | 5 | 安装 ComfyUI + torch（cu128） | 新会话第一次 |
    | 7 | 下载模型 | 新会话第一次 |
    | 9 | 安装自定义节点 | 新会话第一次 |
    | **10** | **★ 启动 ComfyUI 服务** | 服务挂了 |
    | **11** | **★★ 生成公网地址（cpolar）** | 地址失效 / 隧道断了 |
    | **12** | **API 出图（不用开画布）** | 换提示词/参数 |
    | 13 | 状态检查与排错 | 出问题时 |
    | **14 / 15** | **停止服务**（14 勾选框，15 执行） | 用完 |

    ---

    ## 中断之后从哪继续

    | 情况 | 从哪开始 |
    |---|---|
    | 服务或隧道进程挂了，notebook 还开着 | **只跑第 10 格，再跑第 11 格** |
    | 改了模型列表 | 只跑第 7 格（已下好的会自动跳过） |
    | 加了新的自定义节点 | 跑第 9 格 → 再跑第 10 格（重启才生效） |
    | 容器被回收 / 换了会话 / 隔天再用 | **从第 1 格重来**，之前的安装和模型全部消失 |

    > 拿不准就先跑第 4 格，看「当前状态」那一栏。
    """
    )
    return


@app.cell
def _(mo):
    import json
    import pathlib
    import platform
    import shutil
    import subprocess
    import sys
    import time
    import urllib.parse
    import urllib.request

    return (
        json,
        pathlib,
        platform,
        shutil,
        subprocess,
        sys,
        time,
        urllib,
    )


@app.cell
def _(json, mo, pathlib, platform, shutil, subprocess, sys, urllib):
    # ═══════════════════════ 第 4 格 · 环境体检 ═══════════════════════
    COMFY_ROOT = pathlib.Path.home() / "comfy"
    COMFY_DIR = COMFY_ROOT / "ComfyUI"
    MODELS = COMFY_DIR / "models"
    COMFY_URL = "http://127.0.0.1:8188"

    def _gpu():
        _r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True,
        )
        return _r.stdout.strip() or "未检测到（先在右上角规格里打开 GPU）"

    def _alive():
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/system_stats", timeout=2) as _r:
                return json.loads(_r.read())
        except Exception:
            return None

    def _count(sub):
        _d = MODELS / sub
        return len([p for p in _d.iterdir() if p.is_file()]) if _d.exists() else 0

    _nodes = 0
    if (COMFY_DIR / "custom_nodes").exists():
        _nodes = len([p for p in (COMFY_DIR / "custom_nodes").iterdir() if p.is_dir()])

    _installed = (COMFY_DIR / "main.py").exists()
    _up = _alive()
    _free = shutil.disk_usage(str(pathlib.Path.home())).free / 2**30

    mo.md(
        f"""
    ## 第 4 格 · 环境体检

    | 项目 | 状态 |
    |---|---|
    | GPU | `{_gpu()}` |
    | 可用磁盘 | {_free:.1f} GB |
    | ComfyUI | {"已安装" if _installed else "**未安装 → 跑第 5 格**"} |
    | 服务进程 | {"运行中 ✅" if _up else "未运行 → 跑第 10 格"} |
    | 模型 | diffusion_models {_count("diffusion_models")} · text_encoders {_count("text_encoders")} · vae {_count("vae")} · checkpoints {_count("checkpoints")} · loras {_count("loras")} |
    | 自定义节点 | {_nodes} 个 |
    | 安装目录 | `{COMFY_DIR}` |

    {platform.machine()} / Python {sys.version.split()[0]}
    """
    )
    return COMFY_DIR, COMFY_ROOT, COMFY_URL, MODELS


@app.cell
def _(COMFY_DIR, COMFY_ROOT, mo, subprocess, sys):
    # ═════════════════ 第 5 格 · 安装 ComfyUI + torch cu128 ═════════════════
    _steps = []

    if (COMFY_DIR / "main.py").exists():
        _steps.append("ComfyUI 已存在，跳过 clone")
    else:
        COMFY_ROOT.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1",
             "https://github.com/comfyanonymous/ComfyUI", str(COMFY_DIR)],
            check=True,
        )
        _steps.append("ComfyUI 已 clone")

    _probe = subprocess.run(
        [sys.executable, "-c", "import torch;print(torch.cuda.is_available())"],
        capture_output=True, text=True,
    )
    if _probe.stdout.strip() == "True":
        _steps.append("torch 已装且 CUDA 可用，跳过重装")
    else:
        _steps.append("正在装 torch cu128（约 2.5G，5 分钟，别中断）…")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "--upgrade",
             "torch", "torchvision", "torchaudio",
             "--index-url", "https://download.pytorch.org/whl/cu128"],
            check=True,
        )
        _steps.append("torch 安装完成")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(COMFY_DIR / "requirements.txt")],
        check=True,
    )
    _steps.append("ComfyUI 依赖已满足")

    _ver = subprocess.run(
        [sys.executable, "-c",
         "import torch;print(torch.__version__,'| cuda:',torch.cuda.is_available(),'|',torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-')"],
        capture_output=True, text=True,
    ).stdout.strip()

    mo.md(
        "## 第 5 格 · 安装\n\n"
        + "\n".join(f"- {s}" for s in _steps)
        + f"\n\n**`{_ver}`**"
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 第 6 格 · 模型该放哪个目录

    | 模型类型 | `dl()` 的第二个参数 |
    |---|---|
    | 扩散模型（split-file 的 unet 部分） | `diffusion_models` |
    | 文本编码器（CLIP / T5 / Qwen） | `text_encoders` |
    | VAE | `vae` |
    | 单体 checkpoint（SD1.5 / SDXL 单文件） | `checkpoints` |
    | LoRA | `loras` |
    | ControlNet | `controlnet` |
    | 放大模型 | `upscale_models` |

    旧版 ComfyUI 里 `diffusion_models` 叫 `unet`、`text_encoders` 叫 `clip`，现在两个名字都认。

    **链接怎么拿**：HuggingFace 模型页 → `Files and versions` → 点文件 → 复制链接，
    必须是 `.../resolve/main/...`，不是 `blob/main`。
    """
    )
    return


@app.cell
def _(MODELS, mo, shutil, subprocess, urllib):
    # ═══════════════════════ 第 7 格 · 下载模型 ═══════════════════════
    def dl(url, subdir, filename=None, headers=None):
        """下载到 models/<subdir>/，带断点续传 + 坏文件识别。

        url     任意直链（HF / ModelScope / Civitai / GitHub Release）
        subdir  diffusion_models / text_encoders / vae / checkpoints / loras ...
        filename 想改名才填，否则取 URL 最后一段
        headers 需要鉴权时传，如 {"Authorization": "Bearer hf_xxx"}
        """
        _dir = MODELS / subdir
        _dir.mkdir(parents=True, exist_ok=True)
        _name = filename or urllib.parse.unquote(url.split("?")[0].rstrip("/").split("/")[-1])
        _dest = _dir / _name

        MIN = 1024 * 1024  # 小于 1MB 一律视为"没下成"
        if _dest.exists() and _dest.stat().st_size > MIN:
            return f"⏭ `{subdir}/{_name}` 已存在（{_dest.stat().st_size / 2**30:.2f} GB）"

        _cmd = ["curl", "-L", "-C", "-", "--retry", "3", "--retry-delay", "2", "-o", str(_dest)]
        for _k, _v in (headers or {}).items():
            _cmd += ["-H", f"{_k}: {_v}"]
        subprocess.run(_cmd + [url], capture_output=True, text=True)

        if not _dest.exists():
            _req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(_req, timeout=120) as _res, open(_dest, "wb") as _f:
                shutil.copyfileobj(_res, _f)

        if _dest.stat().st_size < MIN:
            with open(_dest, "rb") as _f:
                _head = _f.read(200).decode("utf-8", "ignore").strip()
            _dest.unlink(missing_ok=True)
            return f"❌ `{_name}` 返回的是文本不是模型（已删除）：`{_head[:120]}`"

        return f"✅ `{subdir}/{_name}`（{_dest.stat().st_size / 2**30:.2f} GB）"

    # ══════════ 要下什么模型，只改下面这个列表 ══════════
    # 格式：(链接, 子目录, 可选新文件名；不需要写 None)
    DOWNLOADS = [
        # Anima base v1.0 —— split-file 三件套，缺一不可
        ("https://huggingface.co/circlestone-labs/Anima/resolve/main/split_files/diffusion_models/anima-base-v1.0.safetensors", "diffusion_models", None),
        ("https://huggingface.co/circlestone-labs/Anima/resolve/main/split_files/text_encoders/qwen_3_06b_base.safetensors", "text_encoders", None),
        ("https://huggingface.co/circlestone-labs/Anima/resolve/main/split_files/vae/qwen_image_vae.safetensors", "vae", None),
        ("https://huggingface.co/ElectronGirl/anima-ref-adapter/resolve/main/anima_ref_adapter_v2_r64.safetensors", "loras", None),
        ("https://www.modelscope.cn/models/Nu1lp0inteR/ComfyUI-models/resolve/master/4x-AnimeSharp.pth", "upscale_models", None),
    ]
    # ═══════════════════════════════════════════════

    _out = [dl(_u, _s, _f) for _u, _s, _f in DOWNLOADS]
    mo.md(
        "## 第 7 格 · 下载模型\n\n"
        + "\n\n".join(_out)
        + "\n\n> 下完后到画布按 `R` 刷新，模型才会出现在节点下拉框里。"
    )
    return (dl,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 第 8 格 · 自定义节点说明

    在 `NODES` 列表里加仓库地址，第 9 格会 clone 到 `custom_nodes/` 并自动装它的 `requirements.txt`。

    装完**必须重启 ComfyUI** 才生效：跑第 10 格即可（它是幂等的，检测到没在跑就会重新拉起）。
    """
    )
    return


@app.cell
def _(COMFY_DIR, mo, subprocess, sys):
    # ══════════════════════ 第 9 格 · 安装自定义节点 ══════════════════════
    NODES = [
        "https://github.com/ltdrdata/ComfyUI-Manager",
        "https://github.com/ArcAnima/ComfyUI-Anima-Ref-Adapter",
        # "https://github.com/Fannovel16/comfyui_controlnet_aux",
    ]

    _msgs = []
    for _u in NODES:
        _name = _u.rstrip("/").split("/")[-1]
        _dest = COMFY_DIR / "custom_nodes" / _name
        if _dest.exists():
            _msgs.append(f"⏭ `{_name}` 已存在")
            continue
        subprocess.run(["git", "clone", "--depth", "1", _u, str(_dest)], check=True)
        _req = _dest / "requirements.txt"
        if _req.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(_req)], check=True)
        _msgs.append(f"✅ `{_name}`")

    _gpu = subprocess.run(
        [sys.executable, "-c", "import torch;print(torch.cuda.is_available())"],
        capture_output=True, text=True,
    ).stdout.strip()
    _warn = "" if _gpu == "True" else "\n\n⚠️ torch 的 CUDA 变成不可用——某个节点的依赖把 cu128 换成了 CPU 版，跑第 5 格可恢复。"

    mo.md("## 第 9 格 · 自定义节点\n\n" + "\n\n".join(_msgs) + f"\n\ntorch CUDA：`{_gpu}`" + _warn)
    return


@app.cell
def _(COMFY_DIR, COMFY_ROOT, COMFY_URL, json, mo, subprocess, sys, time, urllib):
    # ═══════════════ 第 10 格 · ★ 启动 ComfyUI 服务 ═══════════════
    # 幂等：已经在跑就只报告状态，不会起第二个进程。
    PIDFILE = COMFY_ROOT / "comfy.pid"

    def _alive():
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/system_stats", timeout=2) as _r:
                return json.loads(_r.read())
        except Exception:
            return None

    _stats = _alive()
    _started = False

    if _stats is None:
        _log = open(COMFY_DIR.parent / "comfyui.log", "w")
        _p = subprocess.Popen(
            [sys.executable, "main.py", "--listen", "127.0.0.1", "--port", "8188",
             "--preview-size", "256"],
            cwd=str(COMFY_DIR), stdout=_log, stderr=subprocess.STDOUT,
        )
        PIDFILE.write_text(str(_p.pid))
        _started = True
        for _ in range(90):
            _stats = _alive()
            if _stats:
                break
            time.sleep(2)

    if _stats:
        _dev = _stats.get("devices", [{}])[0]
        _body = (
            "## 第 10 格 · 服务已就绪\n\n"
            "| 项目 | 值 |\n|---|---|\n"
            f"| 容器内地址 | `{COMFY_URL}` |\n"
            f"| 设备 | {_dev.get('name', '-')} |\n"
            f"| VRAM | {_dev.get('vram_total', 0) / 2**30:.0f} GB |\n"
            f"| 本次 | {'刚刚拉起' if _started else '本来就在跑'} |\n"
            f"| PID | `{PIDFILE.read_text().strip() if PIDFILE.exists() else '-'}` |\n\n"
            "→ **下一步：跑第 11 格拿公网地址。**"
        )
    else:
        _tail = (COMFY_DIR.parent / "comfyui.log").read_text(errors="ignore")[-1500:]
        _body = f"## 第 10 格 · 启动失败\n\n```\n{_tail}\n```"

    mo.md(_body)
    return


@app.cell
def _(COMFY_ROOT, mo, subprocess, time, urllib):
    # ═══════════ 第 11 格 · ★★ 生成公网地址（cpolar）═══════════
    # 幂等：隧道已在跑就复用现有地址，不会起第二个进程。
    import re as _re2

    CP = COMFY_ROOT / "cpolar"
    CPLOG = COMFY_ROOT / "cpolar.log"
    CPPID = COMFY_ROOT / "cpolar.pid"

    if not CP.exists():
        _zip = COMFY_ROOT / "cpolar.zip"
        urllib.request.urlretrieve(
            "https://www.cpolar.com/static/downloads/cpolar-stable-linux-amd64.zip", _zip
        )
        import zipfile as _zipmod

        with _zipmod.ZipFile(_zip) as _z:
            _z.extractall(COMFY_ROOT)
        _zip.unlink(missing_ok=True)
        CP.chmod(0o755)

    # ⚠️ 首次必填，跑通后建议清空（notebook 公开可读）。token 会存进 ~/.cpolar/cpolar.yml
    CPOLAR_TOKEN = ""

    _tok_problem = None
    if CPOLAR_TOKEN:
        _tok = subprocess.run(
            [str(CP), "authtoken", CPOLAR_TOKEN], capture_output=True, text=True
        )
        _cfgdir = __import__("pathlib").Path.home() / ".cpolar"
        if _tok.returncode != 0:
            _tok_problem = f"authtoken 命令失败（返回码 {_tok.returncode}）：\n" + (
                _tok.stdout + _tok.stderr
            ).strip()[:400]
        elif not _cfgdir.exists():
            _tok_problem = "authtoken 命令返回成功，但 ~/.cpolar 目录没生成，配置没写进去"
    else:
        _cfgdir = __import__("pathlib").Path.home() / ".cpolar"
        if not _cfgdir.exists():
            _tok_problem = "CPOLAR_TOKEN 为空，且容器里没有已保存的 token（~/.cpolar 不存在）"

    def _cp_url():
        if not CPLOG.exists():
            return None
        _hits = _re2.findall(
            r"https://[A-Za-z0-9.\-]*cpolar\.(?:cn|top|io)", CPLOG.read_text(errors="ignore")
        )
        return _hits[-1] if _hits else None

    _alive = subprocess.run(["pgrep", "-f", "cpolar http"], capture_output=True, text=True).stdout.strip()
    _url = _cp_url() if _alive else None
    _new = False

    # ══ 地区：账号只允许中国区（实测 us/ap/hk 全部报"不在用户允许范围内"）══
    # 你的账号若换了限制，可以改这里，多个地区按顺序试
    REGIONS = ["cn"]
    _used_region = None

    if not _url and not _tok_problem:
        for _reg in REGIONS:
            subprocess.run(["pkill", "-f", "cpolar"], capture_output=True)
            time.sleep(1)
            if CPLOG.exists():
                CPLOG.unlink()
            _fh = open(CPLOG, "w")
            # -log=stdout 让日志落到文件；-region 指定接入地区
            _p = subprocess.Popen(
                [str(CP), "http", "8188", "-region=" + _reg, "-log=stdout"],
                stdout=_fh, stderr=subprocess.STDOUT,
            )
            CPPID.write_text(str(_p.pid))
            _new = True
            _url = None
            for _ in range(10):
                time.sleep(2)
                _url = _cp_url()
                if _url:
                    break
                _txt = CPLOG.read_text(errors="ignore") if CPLOG.exists() else ""
                if "failed to allocate tunnel" in _txt or "不在用户允许范围内" in _txt:
                    break  # 这个地区不行，换下一个
            if _url:
                _used_region = _reg
                break

    if _url:
        _body = (
            "## 第 11 格 · 公网地址（cpolar）\n\n"
            f"# {_url}\n\n"
            "浏览器打开就是完整的 ComfyUI 画布。\n\n"
            "| 说明 | 内容 |\n|---|---|\n"
            "| 带宽 | 免费版 **1 Mbps**，首屏要 40–80 秒，属正常 |\n"
            "| 域名 | 随机域名，**24 小时内会变** |\n"
            "| 安全 | 无鉴权，别外传 |\n"
            f"| 本次 | {'新建立' if _new else '复用已有隧道'} |\n"
            f"| 接入地区 | {_used_region or '（复用，未重连）'} |\n\n"
            "前提是第 10 格显示「服务已就绪」，否则会 502。\n\n"
            "**预览图提速（重要）**：ComfyUI 设置里把 `Preview Method` 改成 `Latent`——能看到采样过程，但流量只有几 KB/步；`None` 完全没预览，`TAESD`/`VAE` 会让 1Mbps 直接卡死。"
        )
    else:
        _tail = CPLOG.read_text(errors="ignore")[-1200:] if CPLOG.exists() else "（无日志，进程可能没输出就退出了）"
        _tok_part = f"\n### ⚠️ token 有问题\n\n```\n{_tok_problem}\n```\n" if _tok_problem else ""
        _body = (
            "## 第 11 格 · 隧道没建起来\n\n"
            f"{_tok_part}\n"
            "**进程日志：**\n\n"
            f"```\n{_tail}\n```\n\n"
            "对照排查：\n"
            "- 提示 `authtoken` 相关 → token 失效或填错，去 cpolar 后台重新复制（重置过就要用新的）\n"
            "- `connection refused` / `timeout` → 连不上 cpolar 服务端，检查容器能否访问 cpolar.com\n"
            "- 端口占用 → 先跑第 13 格停止，再试"
        )

    mo.md(_body)
    return


@app.cell
def _(COMFY_DIR, COMFY_URL, json, mo, time, urllib):
    # ═════════════ 第 12 格 · API 出图（不用打开画布）═════════════
    # 由你导出的 UI 工作流转写。已剥掉 bypass(mode=4) 节点：
    #   IP-Adapter 515/516/517、UltimateSDUpscale 500/502、CFG-ZeroStar 293、
    #   以及 Set/Get/Join/Fast Bypasser 等纯 UI 辅助节点
    # 只保留 comfy-core 节点，不依赖任何自定义节点（SageAttention 值为 disabled，也已去掉）

    W, H = 1024, 1536
    SEED = 123456789
    STEPS = 18
    CFG = 4.0
    SAMPLER = "sa_solver_pece"   # 若报 "Value not in list"，改成 "euler"
    SCHEDULER = "sgm_uniform"
    UNET = "anima-base-v1.0.safetensors"
    CLIP_NAME = "qwen_3_06b_base.safetensors"
    VAE_NAME = "qwen_image_vae.safetensors"

    POS = (
        "masterpiece,best quality,highres,score_9,year 2025, newest,\n"
        "film grain,(@mellozzo:1.1),@mizikayo,(@eluthel,@zhenli-mari:0.95),, "
        "yuuka \(pajamas\) \(blue archive\), 1girl, arm support, bare shoulders, "
        "blue pajamas, blue shirt, blue shorts, blush, cleavage, clothes pull, halo, "
        "indoors, long hair, looking at viewer, navel, official alternate costume, "
        "pajamas, purple hair, shirt, shorts, shorts pull, sitting, sleepy, solo, "
        "squeans, straight hair, strap gap, thighs, very long hair"
    )
    NEG = (
        "eformed hands, bad anatomy, extra limbs, mutated, extra eyes, bad proportions, "
        "character doll, old, early, artist collaboration, lowres, artistic error, "
        "bad perspective, too many watermarks, (ai-generated:2), artist name, "
        "twitter username, watermark"
    )

    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 2.5}},
        "3": {"class_type": "RescaleCFG", "inputs": {"model": ["2", 0], "multiplier": 0.7}},
        "4": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP_NAME, "type": "stable_diffusion", "device": "default"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": VAE_NAME}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 0], "text": POS}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 0], "text": NEG}},
        "8": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "9": {"class_type": "KSamplerAdvanced", "inputs": {
            "model": ["3", 0], "positive": ["6", 0], "negative": ["7", 0],
            "latent_image": ["8", 0], "add_noise": "enable", "noise_seed": SEED,
            "steps": STEPS, "cfg": CFG, "sampler_name": SAMPLER, "scheduler": SCHEDULER,
            "start_at_step": 0, "end_at_step": 10000, "return_with_leftover_noise": "disable"}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["5", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "molab"}},
    }

    def _post(_path, _payload=None):
        _req = urllib.request.Request(
            f"{COMFY_URL}{_path}",
            data=None if _payload is None else json.dumps(_payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(_req, timeout=60) as _r:
            return json.loads(_r.read())

    _out = None
    _t0 = time.time()
    try:
        _pid = _post("/prompt", {"prompt": wf})["prompt_id"]
        _hist = {}
        for _ in range(600):
            _hist = _post(f"/history/{_pid}")
            if _pid in _hist:
                break
            time.sleep(2)
        _imgs = _hist.get(_pid, {}).get("outputs", {}).get("11", {}).get("images", [])
        if not _imgs:
            _out = mo.md("## 第 12 格 · 没有产出\n\n任务提交成功但没拿到图。检查 ComfyUI 日志（第 13 格有日志末尾）。")
        else:
            _i = _imgs[0]
            _q = urllib.parse.urlencode({
                "filename": _i["filename"],
                "subfolder": _i.get("subfolder", ""),
                "type": _i.get("type", "output"),
            })
            _p = COMFY_DIR / "output" / _i["filename"]
            _p.parent.mkdir(parents=True, exist_ok=True)
            _p.write_bytes(urllib.request.urlopen(f"{COMFY_URL}/view?{_q}", timeout=180).read())
            _out = mo.vstack([
                mo.md(f"## 第 12 格 · 出图完成\n\n`{_p.name}` · {_p.stat().st_size / 1024:.0f} KB · 耗时 {time.time() - _t0:.0f} 秒"),
                mo.image(str(_p)),
            ])
    except Exception as _e:
        _detail = ""
        try:
            _detail = _e.read().decode("utf-8", "ignore")[:1200]
        except Exception:
            pass
        _out = mo.md(
            "## 第 12 格 · 提交失败\n\n"
            f"```\n{_e}\n{_detail}\n```\n\n"
            "常见原因：\n"
            "- `Value not in list: sampler_name` → 把 `SAMPLER` 改成 `euler`\n"
            "- `Value not in list: clip_name / unet_name / vae_name` → 文件名和 models/ 里的不一致\n"
            "- `Cannot connect to host` → ComfyUI 没启动，先跑第 10 格"
        )

    _out
    return


@app.cell
def _(COMFY_DIR, COMFY_ROOT, COMFY_URL, json, mo, subprocess, urllib):
    # ═══════════════════ 第 13 格 · 状态检查 / 排错 ═══════════════════
    import re as _re3

    def _comfy():
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/system_stats", timeout=2) as _r:
                return json.loads(_r.read())
        except Exception:
            return None

    _up = _comfy()
    _procs = subprocess.run(["pgrep", "-af", "cpolar"], capture_output=True, text=True).stdout.strip()
    _cplog = COMFY_ROOT / "cpolar.log"
    _hits = (
        _re3.findall(r"https://[A-Za-z0-9.\-]*cpolar\.(?:cn|top|io)", _cplog.read_text(errors="ignore"))
        if _cplog.exists()
        else []
    )
    _url = _hits[-1] if _hits else "❌ 无 → 跑第 11 格"
    _comfy_log = COMFY_DIR.parent / "comfyui.log"
    _tail = _comfy_log.read_text(errors="ignore")[-800:] if _comfy_log.exists() else "（还没有日志）"

    mo.md(
        "## 第 13 格 · 状态检查\n\n"
        "| 检查项 | 结果 |\n|---|---|\n"
        f"| ComfyUI | {'✅ 运行中' if _up else '❌ 未运行 → 跑第 10 格'} |\n"
        f"| cpolar 进程 | {'✅ 在跑' if _procs else '❌ 没在跑 → 跑第 11 格'} |\n"
        f"| 公网地址 | {_url} |\n"
        f"| 日志位置 | `{_comfy_log}` / `{_cplog}` |\n\n"
        "**ComfyUI 日志末尾：**\n\n"
        f"```\n{_tail}\n```"
    )
    return


@app.cell
def _(mo):
    # ══════════ 第 14 格 · 停止开关（只创建，不读值）══════════
    # marimo 规定：读取 UIElement 的 .value 不能在创建它的同一格里，
    # 所以开关和"执行停止"必须拆成两格（13 建、14 用）。
    stop = mo.ui.checkbox(label="勾选即停止 cpolar 隧道与 ComfyUI（公网地址随即失效）")
    stop
    return (stop,)


@app.cell
def _(mo, stop, subprocess):
    # ══════════ 第 15 格 · 执行停止（只有勾选后才会真的杀进程）══════════
    if stop.value:
        subprocess.run(["pkill", "-f", "cpolar"], capture_output=True)
        subprocess.run(["pkill", "-f", "ComfyUI/main.py"], capture_output=True)
        _msg = "## 已停止\n\n隧道与 ComfyUI 都已退出。要恢复：先跑第 10 格，再跑第 11 格。\n\n（把上面的勾去掉，本格会显示为「运行中」，但进程不会自动重启）"
    else:
        _msg = "## 第 15 格 · 停止服务\n\n服务运行中。勾选第 14 格的复选框才会停止。"

    mo.md(_msg)
    return


if __name__ == "__main__":
    app.run()
