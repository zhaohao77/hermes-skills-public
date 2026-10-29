# Itinerary Structure Rules

Load this when the user provides a screenshot/OCR itinerary, pasted plan, table itinerary, or asks to first decompose the trip without generating images.

## Parsing Goal

Convert messy itinerary input into stable travel-flow fields. Preserve user-provided facts exactly and do not invent missing bookings.

Extract:

- City and area.
- Date and Day number.
- Origin and destination.
- Flight number or train number.
- Departure and arrival time.
- Hotel name and address.
- Attractions.
- Tickets, reservation, opening hours.
- Food or restaurant notes.
- Time cutoffs and fixed nodes.
- Traffic mode.
- User notes.
- Day type: `赶路日`, `轻松游玩日`, `重点提醒日`.

## OCR/Screenshot Rules

- Treat OCR screenshots as valid itinerary sources.
- Normalize spacing, punctuation, line breaks, and half-width/full-width symbols before extraction.
- Preserve route-critical facts hidden in lines: train number, station, time, ticket price, hotel address, and hard cutoff.
- If a day only has city and hotel, keep it as a sparse day and mark missing attractions/food as `待补充`.
- If the user says `先不要生图`, output structure, page advice, and planning only; do not write final image prompts unless the user asks.
- Use `待补卡片` for missing confirmed information.
- Add optional places only as `建议补充`, never as confirmed facts.

## Structure Table Contract

Output a compact table:

| Day | 城市 | 交通 | 景点 | 酒店 | 美食 | 关键提醒 |
| --- | --- | --- | --- | --- | --- | --- |

Each cell should use short route-first phrases, not long prose.

## Density Notes

After parsing, mark each day:

- `高密度`: cross-city move, explicit train/flight, hotel switch, multiple attractions, or hard time/ticket constraints.
- `中密度`: same-city sightseeing with several route nodes but few hard constraints.
- `低密度`: free activity, rest, light food walk, or return buffer.

This density note feeds page splitting. Do not blindly follow the calendar if adjacent low-density days can merge into a clearer phone-readable page.

## Useful Output Pattern When Only Decomposing

When the user asks to decompose first:

1. Give the structured trip table.
2. State page split candidates and density judgment.
3. Mark missing information, especially sparse days and incomplete train/flight details.
4. Give page planning without final image prompts.
5. Use generic character placeholders unless the user has supplied character assets or a local private profile exists.
