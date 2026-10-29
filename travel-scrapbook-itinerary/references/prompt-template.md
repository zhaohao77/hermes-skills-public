# Prompt Template

Use this exact structure for every page prompt. Fill every placeholder with the page's actual itinerary facts. Do not use "same as above".

```text
Create a vertical 9:16 Chinese travel scrapbook itinerary page for phone viewing. The page must work as a travel-flow process board first and a cute scrapbook second.

Style:
route-first Chinese travel scrapbook collage layout, beige grid-paper background, cute travel-journal collage, sticker-like cutout photos with white borders, gray dashed route lines, black handwritten Chinese labels, rounded pastel blocks in soft blue / cream yellow / muted brick red, playful doodles, high-density but clear layout, practical travel guide feeling, suitable for phone viewing.

Page title:
[Day X] [城市 / 主题]

Route:
[路线顺序，用中文地点名和箭头表达，例如: 上海站 -> 苏州站 -> 平江路妆造 -> 狮子林 -> 酒店 -> 金鸡湖夜景]

Required information:
[交通信息: 航班/车次/租车/步行/打车/地铁，保留编号和时间]
[酒店信息: 酒店名、区域、地址或住宿推荐区，如未提供写未提供]
[景点信息: 景点名、顺序、核心看点、开放时间或预约要求]
[美食信息: 餐厅/菜品/区域，如为补充写建议补充或需复核营业]
[天气信息: 温度、降雨、风、穿搭/雨具提醒，如无法实时查询写待实时查询]
[时间提醒: 出发、到达、开门、离开、换乘、返程等硬卡点]
[门票提醒: 价格、预约、开门时间，如未提供写未提供]
[注意事项: 赶路、换酒店、行李、天气、距离、体力、交通衔接]

Visual elements:
[需要补充的景点图片、美食图片、交通图标、地图感元素、票根贴纸、酒店小卡、天气气泡]

Replaceable photo slots:
[列出本页可替换图片槽位，例如 P1-IMG1 苏州站, P1-IMG2 旗袍妆造, P1-IMG3 狮子林园林, P1-IMG4 苏式面, P1-IMG5 金鸡湖夜景。Design each scenic/food/hotel/transport photo as a distinct replaceable sticker photo slot with clear white border, stable label, and enough spacing so the image can be swapped later without changing the route map or text cards.]

Character stickers:
[If user/private character references are available, use those characters as small corner or route-node stickers. If not, use two generic traveler companion stickers: Traveler A as route/time/luggage reminder, Traveler B as photo/food/rest reminder. Do not use proprietary character names or distinctive private IP features unless provided by the user/local private profile.]

Layout:
large Day badge as the first visual entrance, clear central dashed route map with numbered travel nodes, multiple sticker photo cards attached to the route in real sequence, readable Chinese text, useful reminder bubbles, transport/weather/hotel cards clearly separated, cute but practical travel handbook design.
```

## Prompt Assembly Rules

- Put the route near the visual center as a dashed route spine; attach numbered cards to it in travel order.
- Describe route, hard times, weather, transport, hotel, ticket, and warning bubbles before scenic decorative details.
- Keep long facts short in the visual prompt. Use compact Chinese labels such as `10:00 到站`, `门票40`, `15:00前离开`, `雨天带伞`, `晚餐建议补充`.
- If the image model may distort small text, ask for `readable large Chinese labels, not tiny paragraphs`.
- For merged pages, show two Day bubbles or one combined badge such as `Day 4-5`, and separate the days with small timeline chips.
- For a tight day, include one strong warning bubble, for example `重点: 15:00前离开赶高铁`.
- For suggested additions, label them as `建议补充`, not confirmed itinerary.
- For user/private character pages, preserve the provided identity and keep characters away from route-critical text.
- For public/open-source use, default to generic traveler companions and never mention private character names.
- For replaceable photo slots, keep each photo sticker visually separate from the beige grid-paper background, route lines, characters, and text cards.
