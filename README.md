# Windborne 宣传网站 · Windy-WebSite

[Windborne（风信来客）](https://github.com/Astroite) 的官方宣传落地页 —— 自绘卡通天气壁纸 + 天象访客收集玩法。现已在 [Steam](https://store.steampowered.com/app/4947380/_/) 上线。

零构建、零依赖的静态站点：一份 `index.html` + `css/` + `js/`，剪纸拼贴 / 粉彩气象地图美术风格与主项目一致，双语（默认中文，可切换英文），主打 **215 种天象访客**。

## 目录结构

```
index.html            单页落地页（导航 / hero / 特色 / 天象访客画廊 / 实时天气 / 收集玩法 / 区域 / 下载 / 页脚）
css/site.css          设计系统（调色板取自 apps/wallpaper/css/style.css）
js/site.js            精选画廊渲染、稀有度筛选、中英切换、滚动出现、生成图注入（零依赖）
data/visitors.json    24 位精选访客的 {id,label,labelEn,rarity,art}，含完整图鉴数量但不公开名录
assets/visitors/      仅精选访客的代表 sprite（从主项目复制）
assets/art/           Paper 生成的剪纸风美术：hero / og / visitor-showcase / ranch，及 preview.jpg
tools/                构建脚本（见下）
```

## 素材来源与再生成

美术与数据都从相邻的主项目 `Windy-WallPaper` 派生，脚本可重跑。

```bash
# 1) 提取公开精选访客元数据 + 复制代表 sprite（读 apps/wallpaper/data/visitors.js）
python tools/extract_visitors.py

# 2) 用 PaperArt 生成技能重出剪纸风主视觉 / OG / 装饰图（异步，读技能 .env 里的 UAT key）
python tools/gen_all_art.py        # 内部调用 tools/gen_image.py
```

- `tools/gen_image.py`：单张图生成 + 轮询下载的通用封装（PaperArt direct-task API）。
- `tools/extract_visitors.py`：只会导出 24 位公开展示的访客，并清理 `assets/visitors/` 中不在精选集内的旧 sprite，避免重新生成时剧透完整图鉴。
- API Key 从 `~/.claude/skills/.env` 读取，**绝不**写入仓库、前端或日志。
- 生成的大图用 PIL 压成 web 友好的 JPEG（hero 2MB → ~250KB）。

## 本地预览

```bash
python -m http.server 8123      # 然后打开 http://127.0.0.1:8123
```

## 部署

面向 **腾讯云 EdgeOne Pages**：全站相对路径，直接把仓库根目录作为静态站点发布即可，无需构建步骤。

## 归属

数据：Open-Meteo (AWS open data / NOAA GFS) · 台风 GDACS.org (NOAA) · 底图 Natural Earth（public domain）。
仅作氛围可视化，不用于安全攸关决策。与 windy.com、Open-Meteo、GDACS、Natural Earth 无隶属关系。
