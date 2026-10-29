# Live Data Automation

Load this whenever the user asks for fully automated trip planning from a rough idea, weather/temperature prediction, transport, lodging, nearby food, group-buying, or social-platform recommendations.

## Standing Rule

Do not treat weather and nearby food as manual follow-up work. They are default automated lookup modules.

For rough-idea trips, run live lookup before finalizing the plan:

1. Weather and temperature.
2. Intercity and local transport options.
3. Lodging areas and, when searchable, candidate hotels.
4. Nearby food/snack recommendations around the confirmed attractions.
5. Ticket/opening-time checks for fixed attractions.

If a preferred source fails, automatically use fallback sources and state which source was used.

## Weather Lookup

Use the best available live weather tool first. If unavailable or empty, use web search sources.

Priority:

1. Built-in weather forecast tool/API if available.
2. Official meteorological source or local weather bureau when available.
3. Reliable forecast pages such as 中国天气网/天气网, timeanddate, weather-forecast, etc.
4. Historical/average weather only as a last-resort fallback, labeled clearly as not a live forecast.

For each travel date, output:

- Weather condition.
- Low/high temperature.
- Rain probability or rain warning when available.
- Practical advice: umbrella, shoes, indoor fallback, night-view visibility, heat/humidity.
- Source and timestamp/date checked.

Never invent exact temperatures. If sources conflict, give a range and pick the planning-safe recommendation.

## Food And Snack Lookup

Use location-aware recommendation sources around each core route node.

Preferred sources:

- 大众点评 / 美团团购: best for local popularity, distance, price, queue, packages, current business status.
- 小红书: best for recent travel notes, photo appeal, hidden snack leads, but must be treated as inspiration, not proof.
- 高德/百度/Apple Maps: best for distance, navigation, opening status, nearby clusters.
- 携程/Tripadvisor/Google-style public pages: useful fallback for open web results.

When logged-in or app-only platforms are inaccessible, use:

- Public search snippets.
- Map pages.
- Search queries combining attraction + nearby food + platform name.
- Multiple-source cross-checks.

## Food Ranking Rules

Rank candidates by usefulness for the trip, not just internet popularity:

1. Within the route or within roughly 15 minutes by walk/taxi/metro from the attraction.
2. Fits the meal slot: breakfast/lunch/dinner/night snack.
3. Local relevance: 苏式面、汤包、生煎、糕团、糖粥、苏帮菜, etc.
4. Recent platform signals: high rating, high review count, recent mentions, crowd/queue notes.
5. Practicality: easy to reach, not too far, not too queue-heavy before fixed attractions.
6. Good visual sticker value for the scrapbook.

Avoid recommending a shop as a confirmed stop if opening hours, queue, reservation, or current operation cannot be checked. Label it as:

- `建议补充`
- `需复核营业`
- `适合备选`

## Required Output For Food

For every confirmed attraction or lodging area, output:

| Area | Candidate | Type | Why | Distance/Route Fit | Source | Status |
| --- | --- | --- | --- | --- | --- | --- |

Status examples:

- `可放入行程`
- `建议补充`
- `需复核营业`
- `只作种草参考`

## Suzhou Example Search Logic

For `狮子林`:

- Search `狮子林 附近 小吃 大众点评`
- Search `狮子林 附近 苏式面 汤包 平江路 美食`
- Search `小红书 狮子林 附近 美食`
- Consider the route cluster: 狮子林 -> 苏州博物馆 -> 平江路 -> 观前街.

For `金鸡湖`:

- Search `金鸡湖 附近 美食 大众点评`
- Search `金鸡湖 夜景 晚餐 李公堤 东方之门 苏州中心`
- Search `小红书 金鸡湖 夜景 吃什么`
- Consider the route cluster: 东方之门 / 苏州中心 / 李公堤 / 湖滨新天地.

## Automation Fallbacks

If no live browser/app access:

- Use web search and public pages.
- Provide source links.
- Mark uncertain items as `需复核`.

If live weather lookup fails:

- Try a second weather source.
- If all live sources fail, use historical average only with `非实时，仅作穿搭参考`.

If group-buying platforms block access:

- Use public search results and map/review sources.
- Keep the restaurant list as `建议补充`, not confirmed.

## Scrapbook Integration

Weather should become a small practical card:

- `天气: 小雨 22-28°C`
- `带伞 / 防滑鞋 / 金鸡湖夜景看雨势`

Food should become replaceable sticker slots:

- `P1-IMG5 苏式面`
- `P1-IMG6 糕团`
- `P2-IMG4 金鸡湖晚餐`

Do not let food recommendations clutter the route. Use 2-4 strong food/snack cards per page.
