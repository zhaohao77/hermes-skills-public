# Replaceable Image Slot Rules

Load this whenever final scrapbook images are generated, edited, or regenerated. The user's standing improvement request is: scrapbook photo images should be replaceable.

## Product Requirement

Keep the hand-drawn travel scrapbook layout, route clarity, Day badge, handwritten labels, character stickers, weather cards, and reminder cards stable. Make the scenic/food/hotel/transport photos replaceable.

This Skill should output a replacement map for every page, even when the final deliverable is only image prompts.

## Slot Principles

- Treat every photo sticker as a replaceable slot.
- Give each slot a stable ID: `P{page}-IMG{number}`.
- Do not treat character stickers, Day badges, route lines, reminder bubbles, weather cards, or text cards as replaceable photo slots.
- Keep the slot's role and label stable even if the image changes.
- Preserve white border, sticker cutout shape, tilt angle, and approximate position when replacing a photo.
- Replacement must not cover route arrows, train/flight numbers, hotel addresses, ticket prices, weather cards, or hard reminders.
- If exact local/user images are unavailable, use generated or searched representative visuals and mark them as `建议补充图`.

## Slot Manifest Contract

For each page, include a compact `可替换图片槽位` list in the page planning:

| Slot ID | Page Area | Current/Default Visual | Purpose | Replacement Rule |
| --- | --- | --- | --- | --- |
| P1-IMG1 | upper route node | arrival station / airport | arrival proof and route node | Replace with user's station/airport photo; keep label and route position. |

Use this manifest to support:

- Whole-page regeneration with the same layout and one or more replaced images.
- Local editing in a design tool.
- API-based image editing with mask/region replacement if available.

## Prompt Addition For Replaceable Photos

Add this sentence to final page prompts:

```text
Design each scenic/food/hotel/transport photo as a distinct replaceable sticker photo slot with clear white border, stable label, and enough spacing so the image can be swapped later without changing the route map or text cards.
```

When a specific replacement is requested:

```text
Keep the same 9:16 scrapbook layout, route order, text cards, Day badge, character stickers, weather cards, and reminder bubbles. Replace only slot [Slot ID] ([slot label]) with [new image description or uploaded image], preserving the same sticker shape, white border, scale, and label position.
```

## Generic Slot Suggestions

### Arrival / Opening Page

- `P1-IMG1`: arrival station or airport.
- `P1-IMG2`: hotel exterior or lodging-area card.
- `P1-IMG3`: first meal or local snack.
- `P1-IMG4`: light first walk / nearby landmark.

### Core Sightseeing Page

- `P2-IMG1`: main attraction.
- `P2-IMG2`: secondary attraction or photo scene.
- `P2-IMG3`: ticket/reservation visual or landmark detail.
- `P2-IMG4`: meal/snack near the attraction.
- `P2-IMG5`: hotel or next route node if relevant.

### Transfer / Tight Day Page

- `P3-IMG1`: morning attraction.
- `P3-IMG2`: station/transport node.
- `P3-IMG3`: transfer station or vehicle.
- `P3-IMG4`: arrival city.
- `P3-IMG5`: hotel / luggage node.
- `P3-IMG6`: compact food option if it does not crowd the route.

### Slow City / Food Page

- `P4-IMG1`: relaxed scenic node.
- `P4-IMG2`: neighborhood walk.
- `P4-IMG3`: local meal.
- `P4-IMG4`: dessert/snack.
- `P4-IMG5`: evening view or return transport.

### Return Page

- `P5-IMG1`: hotel / packing visual.
- `P5-IMG2`: final meal or souvenir.
- `P5-IMG3`: airport/station.
- `P5-IMG4`: plane/train.
- `P5-IMG5`: small memory photo slot.

## Regeneration Rule

If the user says a generated scrapbook is good but wants to replace images, do not redesign the page from scratch. Keep the successful baseline and target the requested slot(s).

If multiple replacement slots are requested, process page by page and keep the slot manifest stable.
