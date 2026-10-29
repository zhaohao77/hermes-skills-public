# Character System

Load this whenever the user provides character reference images, asks to include traveler/mascot stickers, or generates final scrapbook image prompts.

## Open-Source Boundary

The public Skill must not ship private cartoon IP. Character handling must follow this priority:

1. Use character reference images uploaded by the user in the current request.
2. Use the local private profile at `private/character-profile.local.yaml` if it exists.
3. Otherwise use generic public placeholder companions.

Do not expose private character names, descriptions, or image paths in the public package. See `references/open-source-ip-policy.md` for release rules.

## Local Private Profile

For personal use, a local ignored file may define private characters:

```yaml
characters:
  - id: traveler_a
    display_name: "private name"
    prompt: "private character prompt"
    role: "route/time/luggage reminder"
    assets:
      - "assets/character-references/private-character-sheet.png"
  - id: traveler_b
    display_name: "private name"
    prompt: "private character prompt"
    role: "photo/food/rest reminder"
    assets:
      - "assets/character-references/private-character-sheet.png"
```

This file is ignored by Git and can keep the owner's personal IP active on their own machine.

## Public Placeholder Characters

When no user/private character profile is available, use neutral non-proprietary companions:

### Traveler A

- A simple cute travel companion sticker.
- Neutral hoodie, backpack, sneakers, map or phone in hand.
- Personality: reliable, route-aware, time-aware, lightly humorous.
- Travel role: route checker, schedule reminder, luggage helper, transfer watcher.

Prompt phrase:

`Traveler A: generic cute route-checking travel companion sticker, neutral hoodie, backpack, sneakers, holding map or phone, reliable and lightly humorous`

### Traveler B

- A simple cute travel companion sticker.
- Soft casual travel outfit, camera or tote bag.
- Personality: warm, observant, calm, detail-aware.
- Travel role: photo observer, food finder, rest reminder, mood note keeper.

Prompt phrase:

`Traveler B: generic cute travel companion sticker, casual travel outfit, camera or tote bag, warm observant food-photo-rest reminder`

## Usage Rules

- Treat characters as small scrapbook stickers, not main subjects.
- Keep route, times, hotel, transport, ticket, weather, and reminder cards higher priority than character art.
- Use one to three small character moments per page. Reduce character count first if the layout becomes crowded.
- Do not let characters cover route arrows, train/flight cards, hotel addresses, weather cards, or hard time reminders.
- If using a private profile, preserve the exact identity defined there.
- If using public placeholders, avoid distinctive traits that could be confused with the owner's private IP.

## Action Mapping

| Page Type | Traveler A Action | Traveler B Action |
| --- | --- | --- |
| 出发/抵达 | dragging luggage, checking train/flight card, waving | pulling luggage, waving, adding luggage sticker |
| 赶路/换乘 | checking time, pointing route, running with suitcase | following with suitcase, reminding documents |
| 山水/园林/景点 | pointing at scenery, checking map | taking photos, checking light/weather |
| 海边/慢游 | relaxed walk, holding drink/snack | taking sea photos, eating dessert/snacks |
| 美食 | thumbs-up, holding menu | choosing food, enjoying dessert |
| 返程 | packing luggage, checking documents | organizing souvenirs, waving goodbye |

## Prompt Insertion Pattern

For final image prompts, include one of these blocks.

When user/private references are available:

```text
Character stickers:
Use the provided/local private character reference sheets for consistency.
Add the traveler characters as small corner or route-node stickers, not as main subjects.
Match their actions to the page: [page-specific action].
Do not cover route-critical text, ticket cards, hotel cards, weather cards, or time reminders.
```

When no private references are available:

```text
Character stickers:
Add two generic cute traveler companion stickers as small corner or route-node stickers, not as main subjects.
Traveler A: generic route-checking companion with hoodie, backpack, map/phone.
Traveler B: generic food/photo/rest companion with casual travel outfit, camera/tote bag.
Match their actions to the page: [page-specific action].
Do not use proprietary character names or distinctive private IP features.
```
