# Response 对象属性速查

> 本文档用于排查 `AttributeError` 或抓取结果异常的情况。
> 正常使用时无需阅读。

---

## 1. Response 对象是什么

所有 Fetcher / DynamicFetcher / StealthyFetcher 返回的是 scrapling 的 `Selector` 对象，
**不是** `requests.Response`，两者属性完全不同。

---

## 2. 常用属性速查

| 属性 | 类型 | 说明 |
|------|------|------|
| `page.html_content` | str | 完整 HTML 字符串 ✅ 最常用 |
| `page.text` | str | 纯文本（去除所有标签） |
| `page.status` | int | HTTP 状态码（如 200、202） |
| `page.url` | str | 最终落地 URL（含重定向后） |
| `page.css(selector)` | list | CSS 选择器查询 |
| `page.xpath(expr)` | list | XPath 查询 |
| `page.find(tag, ...)` | element | BeautifulSoup 风格单个查找 |
| `page.find_all(tag, ...)` | list | BeautifulSoup 风格批量查找 |

---

## 3. 常见错误写法对照

| ❌ 错误写法 | 报错 | ✅ 正确写法 |
|------------|------|------------|
| `page.content` | AttributeError | `page.html_content` |
| `page.markdown` | AttributeError | `page.html_content`（再自行转换） |
| `page.html` | AttributeError | `page.html_content` |
| `str(page)` | 返回状态摘要 `<202 https://...>`，不是 HTML | `page.html_content` |
| `python -m scrapling extract ...` | `No module named scrapling.__main__` | `scrapling extract ...` |
| `python3 -m scrapling extract ...` | 同上 | `scrapling extract ...` |

---

## 4. 抓取结果有效性判断

拿到 `page` 后，先做有效性判断再处理数据，避免把拦截页当正常内容处理：

```python
page = DynamicFetcher.fetch(url)

# 步骤1：检查状态码
if page.status not in (200, 201):
    print(f"异常状态码: {page.status}")

# 步骤2：检查 text 是否为空
# html_content 有内容但 text 为空 = 典型的验证码/拦截页特征
if not page.text.strip():
    print("text 为空，疑似被反爬拦截，html_content 预览：")
    print(page.html_content[:500])
    # 参考 references/anti-bot-limits.md 决定下一步策略

# 步骤3：正常处理
print(page.text[:1000])
```

> `html_content` 有内容但 `text` 为空，是验证码/拦截页的典型特征——
> 页面有 HTML 结构但没有可读文本。遇到此情况请参考
> `references/anti-bot-limits.md` 的止损流程。
