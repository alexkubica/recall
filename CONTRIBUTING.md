# Contributing

Keep Recall useful as a readable, mobile-friendly, offline library. Explain the problem your change solves and how you checked it.

Content contributions need an explicit source, author, license, and modification note. Write independent briefs and explanations; link to official problem pages instead of copying statements, editorials, or premium content. Do not add images or code merely because another website displays them. For external code, retain its notices and satisfy its own license; for images, document the exact file and license in `public/media-credits.json`.

Original app contributions use MIT. Coding-foundation adaptations use Apache-2.0; Primer adaptations use CC-BY-4.0; original modern exercises and LeetCode study guides use CC-BY-SA-4.0. Existing code references retain their per-entry licenses. Do not change those scopes through a blanket root license.

Keep card IDs stable so personal reading and study progress survives updates. Canonical reviewed deck inputs are the JSON files in `public/`; LeetCode inputs are in `source/leetcode/`. After content edits, rebuild and run the relevant checks described in the README. `npm run verify:publication` must pass before publication. Do not commit personal exports, credentials, raw Anki archives, browser state, or runtime files.
