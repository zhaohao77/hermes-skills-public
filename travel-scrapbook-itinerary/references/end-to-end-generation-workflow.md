# End-To-End Generation Workflow

Load this when checking whether the Skill can go from a travel plan to final scrapbook images.

## Capability Answer

Yes. Given a travel plan or rough trip idea, this Skill should run the full flow:

`旅行计划/粗想法输入 -> 实时信息补齐或标注待查 -> 行程结构化 -> 可行性判断 -> 信息密度拆页 -> 每页流程规划 -> 可替换图片槽位 -> 9:16 生图提示词 -> 批量生成手账图片`

Actual image generation depends on whether the runtime has an image-generation tool/API available. If available, generate one image per page by default. If not available, output copy-ready prompts and slot manifests.

## Required Reference Loading Order

1. `references/itinerary-structure-rules.md` for screenshot/OCR/text itinerary parsing.
2. `references/rough-idea-trip-builder.md` when the input is only an origin/destination/date/must-go idea.
3. `references/live-data-automation.md` for weather, temperature, transport, lodging, nearby food, group-buying, and social-platform lookup.
4. `references/itinerary-feasibility-rules.md` for route feasibility and supplement boundaries.
5. `references/visual-style-guide.md` for route-first scrapbook layout grammar.
6. `references/character-system.md` when character references or traveler stickers are used.
7. `references/replaceable-image-slots.md` for editable photo sticker slots.
8. `references/prompt-template.md` for final page prompts.
9. `references/default-config.yaml` for backend defaults and mode switches.
10. `references/open-source-ip-policy.md` when packaging or sharing the Skill publicly.

## Execution Logic

### 1. Parse

Extract city, date/day, transport, train/flight number, departure/arrival time, hotel, address, attractions, tickets, food, weather needs, time cutoffs, notes, and missing fields.

For rough ideas, extract origin, destination, date range, nights, must-go places, and missing constraints. Weather/temperature, transportation schedules, lodging availability/prices, restaurant status, ticket rules, and opening hours must be verified live through `references/live-data-automation.md`; use fallback sources automatically before marking anything `待实时查询`.

### 2. Judge Feasibility

Say whether the route can work. Flag tight days, sparse days, risky transfers, missing train details, hotel switches, weather risks, and optional supplements.

### 3. Split Pages

Use density, not calendar habit. Merge low-density adjacent days when it improves phone readability.

### 4. Plan Pages

Each page must include route order, must-show facts, weather, visual supplements, character actions, layout advice, and replaceable photo slots.

### 5. Generate

Use 9:16 image prompts. The page must be a travel-flow board first and a cute scrapbook second.

### 6. Replace

If the user wants to replace a picture, keep the successful page layout and replace only the requested `P{page}-IMG{number}` slot.

## Open-Source-Safe Practical Check

The public Skill should work from text rules and user-provided assets alone:

- Style grammar lives in `references/visual-style-guide.md`.
- Character rules live in `references/character-system.md`.
- Prompt and slot rules live in `references/prompt-template.md` and `references/replaceable-image-slots.md`.
- Private character references, real itinerary screenshots, generated samples, and third-party style images are optional local assets and must be ignored for public release.
