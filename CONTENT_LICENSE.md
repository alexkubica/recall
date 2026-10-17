# License scope

The root MIT license applies to Recall's original application code, interface styles, original UI icons, build/server tools, and original project documentation. It is **not** a blanket license for the bundled study collection, fonts, or upstream reference implementations.

| Material | Location | License |
| --- | --- | --- |
| Original Recall application | `public/*.js`, `public/*.css`, `public/*.html`, `server.mjs`, original tools | MIT; third-party notices embedded in generated files are retained |
| Coding foundations and JavaScript adaptations | `public/deck.json`, `public/javascript-solutions.json` | Apache-2.0, Donne Martin; independent replacement briefs/adaptations by Recall are also Apache-2.0 |
| System Design Primer and OO adaptations | `public/primer-decks.json`, `public/oo-javascript-solutions.json` | CC-BY-4.0, Donne Martin; modifications are identified in card credits |
| Modern exercises and independent LeetCode study guides | `public/modern-deck.json`, `source/leetcode/guides.json` | CC-BY-SA-4.0, Recall contributors |
| LeetCode reference implementations | `source/leetcode/reference-solutions.json` | Each language entry's `license`, `author`, `sourceUrl`, and `adaptation` fields control: CC-BY-SA-4.0 (Doocs and identified Recall implementations) or MIT (neetcode-gh) |
| Fonts | `public/fonts/*` | SIL Open Font License 1.1, with each font's copyright/license file |
| Generated collections | `public/library.json`, `public/leetcode-deck.json`, offline caches | Aggregates retaining the component licenses above; not relicensed wholesale under MIT |

Problem titles, IDs, URLs, difficulty labels, and source-list identifiers are reference metadata. References identify external services and their authors; this project does not assert ownership of those names or grant rights to their problem statements, editorials, logos, or other content. External material reached through links is not covered by Recall's licenses.

All complete license texts and copyright notices are bundled in `public/licenses/` (font notices are also in `public/fonts/`). The app's [credits page](public/credits.html) and per-card/per-snippet credits link to them and identify changes. Preserve those notices when redistributing. Adaptations of CC-BY-SA-4.0 material remain CC-BY-SA-4.0; the separable app code remains MIT.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for sources, changes, exclusions, and attribution details. This is a licensing inventory and publication policy, not a representation that an upstream license can grant rights owned by someone else.
