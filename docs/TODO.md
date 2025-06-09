# TODO: Fix Chaturaji Territory Overlap

- There is still a visual overlap issue between blue and yellow territory highlights in Chaturaji, due to CSS/HTML cascade and pseudo-element rendering.
- A more robust solution is needed to guarantee that only one territory color is ever visible on a square, regardless of CSS order or specificity.
- See `docs/system_prompt.md` for full project context and requirements.
- This does not affect gameplay, but should be addressed for visual polish in a future update. 