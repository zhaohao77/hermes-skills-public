# Itinerary Feasibility And Supplement Rules

Load this when the user asks whether an itinerary is reasonable, asks for optimization before making scrapbook pages, or asks Codex to supplement scenic/food photo content.

## Core Assessment Pattern

Answer with a direct judgment first:

`整体可行 / 偏赶 / 不建议这样走`

Then explain the practical reason:

- City order and transport direction.
- Fixed train/flight/opening-hour constraints.
- Hotel switch and luggage pressure.
- Distance between route nodes.
- Weather risk and indoor fallback.
- Whether the day can still be read clearly as a travel-flow scrapbook page.

Do not jump straight into image prompt writing when the user first asks `行程合理吗`.

## Feasibility Checks

### Cross-City Movement

- Check whether intercity transport time leaves enough local sightseeing time.
- If arrival is late, treat the day as arrival/rest/light food day.
- If departure is early or return is fixed, keep the final day light.

### Attraction Density

- One major attraction plus one nearby light stop is usually comfortable.
- Two major attractions plus intercity movement is likely tight.
- Three or more major attractions in one day should be flagged unless they are very close and the user wants a fast pace.

### Time And Ticket Constraints

- Highlight opening time, last entry, reservation, ticket price, show time, ferry/train cutoff, and airport buffer.
- If a fixed point depends on weather or reservation, add a backup route.

### Hotel And Luggage

- Hotel switches increase friction.
- If luggage storage is needed, put it into the route as an explicit node.
- Recommend lodging areas that reduce backtracking, not only visually attractive areas.

### Weather

- Rain, heat, cold, wind, and poor visibility should change the route.
- For night views, add an indoor or sheltered fallback when rain is likely.
- For photo-heavy days, add timing, light, footwear, and makeup/clothing notes.

## Page Split Decision

Do not mechanically make every day one page. Use density:

Single page if a day satisfies any two:

- Cross-city transport.
- Explicit train or flight number.
- Two or more core attractions.
- Ticket/opening/cutoff constraint.
- Important hotel switch.
- Opening day or return day with clear travel function.

Merge candidate if most are true:

- Same city slow travel.
- Mostly free activity.
- Few transport nodes.
- Fewer than three core confirmed nodes.
- Works better as a route overview page.

Upgrade a merged page back into separate pages when each day has enough confirmed route nodes, meal nodes, tickets, or hard times to stand alone.

## Supplement Boundary

- Supplement only real, plausible, city-matched scenic/food visuals.
- Label added locations as `建议补充`.
- Never invent booked hotels, train numbers, tickets, reservations, or exact restaurant status.
- Never supplement at the cost of hiding confirmed route/time facts.
- If using platform/social recommendations, mark uncertain shops as `需复核营业` or `只作种草参考`.

## Tight-Day Language

When a day is tight, name the bottleneck directly:

- `这天偏赶，瓶颈是上午拍照 + 下午换乘。`
- `这天不要再加大景点，主线已经够满。`
- `夜景看天气，雨大时改室内湖景/商场晚餐。`

The scrapbook page should visualize this with one strong reminder bubble, not with long explanation.
