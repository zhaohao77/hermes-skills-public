# 反爬能力边界与已知限制

> 本文档用于判断目标网站是否在 scrapling 的支持范围内，
> 以及遇到无法绕过的验证码时如何止损。
> 正常使用时无需阅读。

---

## 1. 反爬绕过能力范围

| 防护类型 | 支持情况 | 推荐命令/参数 |
|---------|---------|-------------|
| 无防护 / User-Agent 检测 | ✅ 完全支持 | `get` |
| 动态 JS 渲染（无防护） | ✅ 完全支持 | `fetch` |
| Cloudflare 5 秒盾 | ✅ 支持 | `stealthy-fetch` |
| Cloudflare Turnstile | ✅ 支持 | `stealthy-fetch --solve-cloudflare` |
| 普通 IP 频率限制 | ⚠️ 部分支持 | 配合 `--proxy` 使用 |
| BALEEN 自定义验证码 | ❌ 不支持 | — |
| reCAPTCHA v3 / hCaptcha | ❌ 不支持 | — |
| 登录墙 / 付费内容 | ❌ 不支持 | 需手动提供 Cookie |

> `--solve-cloudflare` 只能处理 Cloudflare 系验证码，
> 对 BALEEN、reCAPTCHA 等第三方验证码无效。

---

## 2. 止损判断：何时应该停止尝试

满足以下任意一条，即判定为**无法绕过**，应立即止损：

- 已尝试 `stealthy-fetch --solve-cloudflare`，返回内容仍含验证码关键词
  （`captcha`、`challenge`、`robot`、`BALEEN`、`Je ne suis pas un robot` 等）
- `page.text` 持续为空，且 `page.html_content` 含验证码页面特征
- 同一网站连续升级两次抓取策略（`get` → `fetch` → `stealthy-fetch`）后结果无改善

**不要在确认无法绕过后继续重复尝试**，这只会让用户继续等待而无法得到结果。

---

## 3. 止损后：告知用户并给出替代方案

确认无法绕过后，停止尝试，向用户说明情况：

> "该网站使用了 scrapling 目前无法自动绕过的验证码保护，继续尝试不会改变结果。
> 建议以下替代方案：
>
> 1. **官方 API**：查询该网站是否提供数据 API（通常更稳定）
> 2. **手动 Cookie**：在浏览器中完成验证后，将 Cookie 传入 `--cookies` 参数
> 3. **付费代理**：使用带住宅 IP 的代理池配合 `--proxy` 参数，部分场景有效
> 4. **Docker 模式**：`docker pull pyd4vinci/scrapling`，部分场景绕过率更高"
