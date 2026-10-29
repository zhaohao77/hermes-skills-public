# Rough-Idea Trip Builder

Load this when the user gives only a rough travel idea, such as:

`2026年5月24日到2026年5月26日，两天想从上海去苏州，想去金鸡湖夜景和狮子林。`

## Capability

The Skill should turn a rough idea into a usable travel-flow scrapbook plan:

`基础想法 -> 实时/可验证信息补齐 -> 可行性判断 -> 行程排布 -> 交通/住宿/小吃建议 -> 手账页规划 -> 9:16 生图提示词/图片`

## Required Inputs To Extract

- 出发地.
- 目的地.
- 日期范围 and nights count.
- Must-go places.
- Travel companions if mentioned.
- Pace preference if mentioned.
- Missing constraints: budget, hotel standard, whether driving, luggage, food taboos, child/elder needs.

If the user does not provide missing constraints, make conservative assumptions and label them clearly, instead of asking repeatedly.

## Live Data Rule

Weather, temperature, transportation schedule, hotel availability/price, restaurant opening status, ticket policy, opening hours, and crowd conditions can change. For actual trip planning, use `references/live-data-automation.md` and verify these with current sources whenever tools/network are available.

Do not stop at `待实时查询` before trying available lookup sources. If live lookup is unavailable after fallback attempts, write:

`待实时查询`

or:

`以下为基于常规路线的建议，出发前需复核天气、班次、营业时间和酒店价格。`

Do not invent exact weather, hotel prices, train times, or restaurant opening hours.

For food and snack recommendations, automatically search nearby food sources around the route nodes. Prefer 大众点评/美团/小红书/高德 or accessible public equivalents; mark unverified items as `建议补充` or `需复核营业`.

## Output Requirements For Rough Ideas

Before image prompts, produce:

1. `【0. 基础假设与需实时查询】`
   - List assumptions and which facts need live verification.
2. `【1. 行程可行性判断】`
   - Say whether the trip works, where it is tight, and the recommended pace.
3. `【2. 天气与穿搭/携带提醒】`
   - Include weather/temperature if live data was checked; otherwise mark `待实时查询`.
4. `【3. 推荐行程安排】`
   - Day-by-day route, time blocks, travel order, fallback options.
5. `【4. 交通方式推荐】`
   - Intercity transport, local transit/taxi/walking, luggage handling.
6. `【5. 住宿区域建议】`
   - Recommend areas near core route, not unverifiable specific bookings unless checked.
7. `【6. 景点附近小吃/餐饮建议】`
   - Use real place categories or verified shops; mark additions as `建议补充`.
8. Then continue the normal scrapbook output:
   - structured table, page split, page planning, replaceable slots, prompts/images.

## Planning Heuristics

- Put fixed must-go attractions first.
- Put night-view attractions in the evening slot.
- Avoid zigzag routes.
- Keep first day lighter if it involves intercity travel.
- Keep departure day lighter and close to transport hubs.
- Group sites by area.
- Give fallback options for rain, heat, crowding, or fatigue.
- Prefer a clear two-page or three-page hand账 split for short trips, not one giant page.

## Example: Shanghai To Suzhou Rough Idea

For a rough input like:

`2026年5月24日到2026年5月26日，从上海去苏州，想去金鸡湖看夜景和狮子林看园林。`

Use this default planning logic:

- Trip length: 2 nights / roughly 3 calendar days if dates include 24, 25, 26.
- Core city: 苏州.
- Must-go: 狮子林, 金鸡湖夜景.
- Likely split:
  - Page 1: 上海 -> 苏州抵达 + 平江路/拙政园片区轻逛 + 狮子林.
  - Page 2: 苏州老城/园林 + 晚上金鸡湖夜景.
  - Page 3: 轻松收尾 + 返回上海, if the 26th is a real travel day.
- If the user truly means only two full days, compress into:
  - Page 1: 上海 -> 苏州老城园林线.
  - Page 2: 金鸡湖夜景 + 返程/收尾.

Recommended lodging areas to evaluate:

- 老城区 / 平江路 / 拙政园-狮子林周边: best for gardens and old-city walk.
- 观前街: convenient food/metro/commercial base.
- 金鸡湖 / 东方之门 / 苏州中心周边: best for night view and modern waterfront, but farther from old gardens.

Recommended food categories near the route:

- 苏式面, 生煎/汤包, 糖粥, 桂花糕/糕团, 松鼠桂鱼, 藏书羊肉 if seasonally suitable.
- Shops must be verified before naming as confirmed stops.

## Scrapbook-Specific Rule

For rough-idea trips, the hand账 should show both:

- `确认点`: user-mentioned must-go places.
- `建议补充`: planner-added stops, food, lodging areas, and fallback options.

Never let suggested additions look like booked or confirmed itinerary facts.
