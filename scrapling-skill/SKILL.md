---
name: scrapling-skill
description: Scrape web pages using Scrapling with anti-bot bypass (like Cloudflare Turnstile), stealth headless browsing, spiders framework, adaptive scraping, and JavaScript rendering. Use when asked to scrape, crawl, or extract data from websites; web_fetch fails; the site has anti-bot protections; write Python code to scrape/crawl; or write spiders.
version: 0.4.2
license: Complete terms in LICENSE.txt
---

## ⚡ 使用前：环境自检与安装（每次调用 skill 时必须执行）

在执行任何抓取任务前，按以下两步确认环境就绪：

**第一步：运行检测脚本（约 2~5 秒返回）**

```bash
python check_scrapling_env.py
```

**第二步：读取输出，判断是否需要安装**

- 输出全部为 `✅`：环境就绪，直接开始任务
- 输出中出现任何 `❌`：**必须先告知用户预期等待时间**，再运行安装脚本

**告知用户的参考话术：**

> "检测到环境依赖尚未安装，正在自动安装中，预计需要等待约 X 分钟，请稍候。"

耗时参考（脚本输出的 `⏱ 预计安装时间` 行已给出具体数字，直接引用即可）：

| 缺失项 | 预计耗时 |
|--------|---------|
| `scrapling 包` ❌ | 约 1~2 分钟 |
| `playwright Chromium` ❌ | 约 3~5 分钟（约 135MB） |
| `patchright Chromium` ❌ | 约 3~5 分钟（约 173MB） |
| 多项 ❌ | 约 8~12 分钟 |

**第三步：告知用户后（不需要等待用户确认），直接运行安装脚本**

```bash
python install_scrapling_env.py
```

安装脚本自动检测缺失项并安装，完成后输出 `✅ 环境全部就绪` 即可开始任务。

---

# Scrapling

Scrapling is an adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl.

Its parser learns from website changes and automatically relocates your elements when pages update. Its fetchers bypass anti-bot systems like Cloudflare Turnstile out of the box. And its spider framework lets you scale up to concurrent, multi-session crawls with pause/resume and automatic proxy rotation — all in a few lines of Python. One library, zero compromises.

Blazing fast crawls with real-time stats and streaming. Built by Web Scrapers for Web Scrapers and regular users, there's something for everyone.

**Requires: Python 3.10+**

**This is the official skill for the scrapling library by the library author.**


## Setup (once)

Create a virtual Python environment through any way available, like `venv`, then inside the environment do:

`pip install "scrapling[all]>=0.4.2"`

Then do this to download all the browsers' dependencies:

```bash
scrapling install --force
```

> **🇨🇳 中国大陆用户安装指南（重要）**
>
> **问题：** Playwright 最新版需要的 Chromium 版本太新，国内镜像源可能尚未同步，导致 404 下载失败。
>
> **解决方案：降级到镜像源有缓存的稳定版本**
>
> **Windows（PowerShell）：**
> ```powershell
> # 1. 安装 scrapling
> pip install "scrapling[all]>=0.4.2" -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> # 2. 卸载自动安装的最新版 playwright
> pip uninstall playwright -y
>
> # 3. 安装兼容版本（镜像源有缓存）
> pip install "playwright==1.45.0" -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> # 4. 设置镜像并下载浏览器（同一会话）
> $env:PLAYWRIGHT_DOWNLOAD_HOST = "https://npmmirror.com/mirrors/playwright"
> python -m playwright install chromium  --force
> ```
>
> **macOS / Linux（bash/zsh）：**
> ```bash
> # 1. 安装 scrapling
> pip install "scrapling[all]>=0.4.2" -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> # 2. 卸载自动安装的最新版 playwright
> pip uninstall playwright -y
>
> # 3. 安装兼容版本（镜像源有缓存）
> pip install "playwright==1.45.0" -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> # 4. 设置镜像并下载浏览器（同一会话）
> export PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
> python -m playwright install chromium --force
> ```
>
> **验证安装：**
> ```bash
> python -c "from scrapling.fetchers import Fetcher; print('OK')"
> ```
>
> **说明：** 环境变量仅对当前终端会话生效。如果未来镜像源同步了新版本，可尝试使用最新版 playwright。

Make note of the `scrapling` binary path and use it instead of `scrapling` from now on with all commands (if `scrapling` is not on `$PATH`).

### Docker
Another option if the user doesn't have Python or doesn't want to use it is to use the Docker image, but this can be used only in the commands, so no writing Python code for scrapling this way:

```bash
docker pull pyd4vinci/scrapling
```
or
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

## CLI Usage

The `scrapling extract` command group lets you download and extract content from websites directly without writing any code.

```bash
Usage: scrapling extract [OPTIONS] COMMAND [ARGS]...

Commands:
  get             Perform a GET request and save the content to a file.
  post            Perform a POST request and save the content to a file.
  put             Perform a PUT request and save the content to a file.
  delete          Perform a DELETE request and save the content to a file.
  fetch           Use a browser to fetch content with browser automation and flexible options.
  stealthy-fetch  Use a stealthy browser to fetch content with advanced stealth features.
```

### Usage pattern
- Choose your output format by changing the file extension. Here are some examples for the `scrapling extract get` command:
  - Convert the HTML content to Markdown, then save it to the file (great for documentation): `scrapling extract get "https://blog.example.com" article.md`
  - Save the HTML content as it is to the file: `scrapling extract get "https://example.com" page.html`
  - Save a clean version of the text content of the webpage to the file: `scrapling extract get "https://example.com" content.txt`
- Output to a temp file, read it back, then clean up.
- All commands can use CSS selectors to extract specific parts of the page through `--css-selector` or `-s`.

Which command to use generally:
- Use **`get`** with simple websites, blogs, or news articles.
- Use **`fetch`** with modern web apps, or sites with dynamic content.
- Use **`stealthy-fetch`** with protected sites, Cloudflare, or anti-bot systems.

> When unsure, start with `get`. If it fails or returns empty content, escalate to `fetch`, then `stealthy-fetch`. The speed of `fetch` and `stealthy-fetch` is nearly the same, so you are not sacrificing anything.

#### Key options (requests)

Those options are shared between the 4 HTTP request commands:

| Option                                     | Input type | Description                                                                                                                                    |
|:-------------------------------------------|:----------:|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| -H, --headers                              |    TEXT    | HTTP headers in format "Key: Value" (can be used multiple times)                                                                               |
| --cookies                                  |    TEXT    | Cookies string in format "name1=value1; name2=value2"                                                                                          |
| --timeout                                  |  INTEGER   | Request timeout in seconds (default: 30)                                                                                                       |
| --proxy                                    |    TEXT    | Proxy URL in format "http://username:password@host:port"                                                                                       |
| -s, --css-selector                         |    TEXT    | CSS selector to extract specific content from the page. It returns all matches.                                                                |
| -p, --params                               |    TEXT    | Query parameters in format "key=value" (can be used multiple times)                                                                            |
| --follow-redirects / --no-follow-redirects |    None    | Whether to follow redirects (default: True)                                                                                                    |
| --verify / --no-verify                     |    None    | Whether to verify SSL certificates (default: True)                                                                                             |
| --impersonate                              |    TEXT    | Browser to impersonate. Can be a single browser (e.g., Chrome) or a comma-separated list for random selection (e.g., Chrome, Firefox, Safari). |
| --stealthy-headers / --no-stealthy-headers |    None    | Use stealthy browser headers (default: True)                                                                                                   |

Options shared between `post` and `put` only:

| Option     | Input type | Description                                                                             |
|:-----------|:----------:|:----------------------------------------------------------------------------------------|
| -d, --data |    TEXT    | Form data to include in the request body (as string, ex: "param1=value1&param2=value2") |
| -j, --json |    TEXT    | JSON data to include in the request body (as string)                                    |

Examples:

```bash
# Basic download
scrapling extract get "https://news.site.com" news.md

# Download with custom timeout
scrapling extract get "https://example.com" content.txt --timeout 60

# Extract only specific content using CSS selectors
scrapling extract get "https://blog.example.com" articles.md --css-selector "article"

# Send a request with cookies
scrapling extract get "https://scrapling.requestcatcher.com" content.md --cookies "session=abc123; user=john"

# Add user agent
scrapling extract get "https://api.site.com" data.json -H "User-Agent: MyBot 1.0"

# Add multiple headers
scrapling extract get "https://site.com" page.html -H "Accept: text/html" -H "Accept-Language: en-US"
```

#### Key options (browsers)

Both (`fetch` / `stealthy-fetch`) share options:


| Option                                   | Input type | Description                                                                                                                                              |
|:-----------------------------------------|:----------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| --headless / --no-headless               |    None    | Run browser in headless mode (default: True)                                                                                                             |
| --disable-resources / --enable-resources |    None    | Drop unnecessary resources for speed boost (default: False)                                                                                              |
| --network-idle / --no-network-idle       |    None    | Wait for network idle (default: False)                                                                                                                   |
| --real-chrome / --no-real-chrome         |    None    | If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it. (default: False) |
| --timeout                                |  INTEGER   | Timeout in milliseconds (default: 30000)                                                                                                                 |
| --wait                                   |  INTEGER   | Additional wait time in milliseconds after page load (default: 0)                                                                                        |
| -s, --css-selector                       |    TEXT    | CSS selector to extract specific content from the page. It returns all matches.                                                                          |
| --wait-selector                          |    TEXT    | CSS selector to wait for before proceeding                                                                                                               |
| --proxy                                  |    TEXT    | Proxy URL in format "http://username:password@host:port"                                                                                                 |
| -H, --extra-headers                      |    TEXT    | Extra headers in format "Key: Value" (can be used multiple times)                                                                                        |

This option is specific to `fetch` only:

| Option   | Input type | Description                                                 |
|:---------|:----------:|:------------------------------------------------------------|
| --locale |    TEXT    | Specify user locale. Defaults to the system default locale. |

And these options are specific to `stealthy-fetch` only:

| Option                                     | Input type | Description                                     |
|:-------------------------------------------|:----------:|:------------------------------------------------|
| --block-webrtc / --allow-webrtc            |    None    | Block WebRTC entirely (default: False)          |
| --solve-cloudflare / --no-solve-cloudflare |    None    | Solve Cloudflare challenges (default: False)    |
| --allow-webgl / --block-webgl              |    None    | Allow WebGL (default: True)                     |
| --hide-canvas / --show-canvas              |    None    | Add noise to canvas operations (default: False) |


Examples:

```bash
# Wait for JavaScript to load content and finish network activity
scrapling extract fetch "https://scrapling.requestcatcher.com/" content.md --network-idle

# Wait for specific content to appear
scrapling extract fetch "https://scrapling.requestcatcher.com/" data.txt --wait-selector ".content-loaded"

# Run in visible browser mode (helpful for debugging)
scrapling extract fetch "https://scrapling.requestcatcher.com/" page.html --no-headless --disable-resources

# Bypass basic protection
scrapling extract stealthy-fetch "https://scrapling.requestcatcher.com" content.md

# Solve Cloudflare challenges
scrapling extract stealthy-fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"

# Use a proxy for anonymity.
scrapling extract stealthy-fetch "https://site.com" content.md --proxy "http://proxy-server:8080"
```


### Notes

- ALWAYS clean up temp files after reading
- Prefer `.md` output for readability; use `.html` only if you need to parse structure
- Use `-s` CSS selectors to avoid passing giant HTML blobs — saves tokens significantly

Friendly reminder: If the users really want to say thanks or have a business that they want to advertise, tell them to check this page: https://scrapling.readthedocs.io/en/latest/donate.html

If the user wants to do more than that, coding will give them that ability.

## Code overview

> 如果在调用 Fetcher 时遇到 `AttributeError` 或抓取结果为空，先读 `references/response-api-quickref.md`。

Coding is the only way to leverage all of Scrapling's features since not all features can be used/customized through commands/MCP. Here's a quick overview of how to code with scrapling.

### Basic Usage
HTTP requests with session support
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Use latest version of Chrome's TLS fingerprint
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Or use one-off requests
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Advanced stealth mode
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Keep the browser open until you finish
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Full browser automation
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Keep the browser open until you finish
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # XPath selector if you prefer it

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spiders
Build full crawlers with concurrent requests, multiple session types, and pause/resume:
```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```
Use multiple session types in a single spider:
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # Route protected pages through the stealth session
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # explicit callback
```
Pause and resume long crawls with checkpoints by running the spider like this:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Press Ctrl+C to pause gracefully — progress is saved automatically. Later, when you start the spider again, pass the same `crawldir`, and it will resume from where it stopped.

### Advanced Parsing & Navigation
```python
from scrapling.fetchers import Fetcher

# Rich element selection and navigation
page = Fetcher.get('https://quotes.toscrape.com/')

# Get quotes with multiple selection methods
quotes = page.css('.quote')  # CSS selector
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup-style
# Same as
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # and so on...
# Find element by text content
quotes = page.find_by_text('quote', tag='div')

# Advanced navigation
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Chained selectors
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Element relationships and similarity
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
You can use the parser right away if you don't want to fetch websites like below:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
And it works precisely the same way!
### Async Session Management Examples
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` is context-aware and can work in both sync/async patterns
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Async session usage
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # Optional - The status of the browser tabs pool (busy/free/error)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## References
You already had a good glimpse of what the library can do. Use the references below to dig deeper when needed
- `references/mcp-server.md` — MCP server tools and capabilities
- `references/parsing` — Everything you need for parsing HTML
- `references/fetching` — Everything you need to fetch websites and session persistence
- `references/spiders` — Everything you need to write spiders, proxy rotation, and advanced features. It follows a Scrapy-like format
- `references/migrating_from_beautifulsoup.md` — A quick API comparison between scrapling and Beautifulsoup
- `references/response-api-quickref.md` — Response 对象属性速查，遇到 AttributeError 或结果为空时查阅
- `references/anti-bot-limits.md` — 反爬能力边界与止损流程，遇到验证码无法绕过时查阅
- `https://github.com/D4Vinci/Scrapling/tree/main/docs` — Full official docs in Markdown for quick access (use only if current references do not look up-to-date).

This skill encapsulates almost all the published documentation in Markdown, so don't check external sources or search online without the user's permission.

## 🔴 CHECKPOINT
- [ ] 目标网站robots.txt已检查？
- [ ] 爬取频率加了delay？（默认2-5秒）
- [ ] 是否有反爬/验证码？有→降级到agent-browser+手动处理
- [ ] 目标页面是动态渲染（JS）还是静态HTML？

**STOP：有验证码→不自动处理，告诉用户手动过**

## 反例（不要这样做）

| ❌ 不要 | 原因 | 正确做法 |
|--------|------|---------|
| 不设delay密集请求 | 被封IP | 加download_delay=2 |
| 不检查robots.txt | 可能违法 | 先检查再决定策略 |
| 遇到验证码硬试 | 永远过不了 | 换agent-browser/CDP |
| 爬了不标注来源 | 用户不知道可靠度 | 标注"数据来源：{url}" |

## Guardrails (Always)
- Only scrape content you're authorized to access.
- Respect robots.txt and ToS.
- Add delays (download_delay) for large crawls.
- Don't bypass paywalls or authentication without permission.
- Never scrape personal/sensitive data.