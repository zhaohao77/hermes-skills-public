# Open-Source IP Policy

Load this when preparing the Skill for public release, packaging, licensing, or handling character ownership.

## Release Principle

Open-source the engine, not the owner's private visual IP.

The public package may include:

- `SKILL.md`
- Prompt templates
- Text style rules
- Itinerary parsing and page-splitting rules
- Replaceable image slot rules
- Public configuration schema
- Generic placeholder character rules

The public package must not include:

- Private cartoon character sheets or pose sheets.
- Generated sample pages containing private characters.
- Real itinerary screenshots, hotel addresses, tickets, or personal travel records.
- Third-party style reference images unless their license explicitly allows redistribution.
- API keys, cookies, platform tokens, or paid data exports.

## Recommended Repo Shape

```text
travel-scrapbook-itinerary/
  SKILL.md
  agents/openai.yaml
  references/
    character-system.md
    character-profile.example.yaml
    default-config.yaml
    prompt-template.md
    visual-style-guide.md
    ...
  assets/
    character-references/.gitkeep
    generated-samples/.gitkeep
    source-itineraries/.gitkeep
    style-references/.gitkeep
  private/                 # ignored by Git
```

## Private Character Pack

For the owner's local machine, keep private characters in ignored paths:

```text
travel-scrapbook-itinerary/private/character-profile.local.yaml
travel-scrapbook-itinerary/assets/character-references/*.png
```

The local profile can map private names, prompts, and image files. Other users should create their own local profile or upload their own character images.

## Public Prompt Behavior

When public users do not upload characters:

- Use generic traveler companion stickers.
- Do not mention the owner's private names.
- Do not describe distinctive private traits.
- Do not imply bundled character references exist.

When public users upload their own characters:

- Use their references as the sticker identity.
- Keep those characters small and secondary.
- Preserve travel flow priority over character art.

## Licensing Recommendation

Use a split license:

- Code, prompts, and workflow docs: MIT or Apache-2.0.
- Private assets: not licensed, not distributed.
- Third-party reference images: not distributed unless separately licensed.
- Generated outputs: clarify ownership depends on the image model/platform terms and any uploaded assets.

## Release Checklist

Before publishing:

1. Run `git status --short` and confirm ignored private assets are not staged.
2. Run `git check-ignore -v` on private character images and generated samples.
3. Search for private names, image paths, hotel addresses, and real itinerary records.
4. Confirm public defaults use generic placeholder characters.
5. Confirm `private/character-profile.local.yaml` is not tracked.
