# Recall

A mobile-friendly interview reading library with **533 articles in six collections**, JavaScript and Python references, bookmarks, private notes, and optional flashcard practice. Install it on your phone and read offline.

**[Open Recall](https://alexkubica.github.io/recall/)** · [Credits and licenses](https://alexkubica.github.io/recall/credits.html)

| Collection | Articles |
| --- | ---: |
| Coding foundations | 100 |
| System design concepts | 42 |
| System design exercises | 8 |
| Object-oriented design | 6 |
| Modern interview practice | 30 |
| Popular LeetCode study guides | 347 |

Follow 36 curated chapters, search by topic or problem number, and filter by difficulty, collection, study list, and reading status. The LeetCode selection combines six popular lists with duplicates removed: LeetCode 75, Top Interview 150, Top 100 Liked, Blind 75, NeetCode 150, and NeetCode 250. Membership is a snapshot checked October 17, 2026, not a company-frequency ranking. Each of the 347 guides has a brief, approach, edge cases, and credited JavaScript/Python references. Official prompts and judging are linked externally; seven official problems require Premium.

## Install and use offline

On iPhone/iPad, open the site in Safari and choose **Share → Add to Home Screen**. On Android, use Chrome’s **Install app / Add to Home screen** action. Wait for **Offline ready** before disconnecting. The library, code, exercise diagrams, fonts, and license notices are saved together. External links still need a connection.

Updates download completely before **Update ready → Use updated version** activates them. Progress stays in this browser; the app has no account, analytics, or progress-upload service. GitHub provides hosting and its usual hosting logs. Browsers and operating systems may clear local storage, so keep a backup.

**Moving from another address or device:** in the old app, open **Progress → Export progress**. At the new address, choose **Progress → Import progress**. Ratings, reading markers, bookmarks, notes, and language preference are merged. IDs remain compatible with earlier versions, but browser storage does not automatically move between website addresses.

## Run and build

Requires Node.js 20+. Python 3.9+ is needed only for content generators and Python checks. No package installation is required.

```sh
npm start
# http://127.0.0.1:4173/
```

For a separate preview under a GitHub Pages-style project path:

```sh
PORT=4177 BASE_PATH=/recall/ npm start
# http://127.0.0.1:4177/recall/
```

Reviewed deck inputs live in `public/`. LeetCode metadata, original guides, reference implementations, and provenance are in `source/leetcode/`. To regenerate after editing those snapshots:

```sh
python3 scripts/build-leetcode.py
npm run build
npm run check
npm run verify:publication
node scripts/verify-library.mjs
node scripts/verify-reading-order.mjs
node scripts/verify-reader.mjs
node scripts/verify-leetcode.mjs
node scripts/verify-leetcode-code.mjs
python3 scripts/verify-leetcode-python.py
```

`npm run build` produces the merged library and a versioned offline snapshot. `npm run package` copies only runtime assets into `dist/`, with `.nojekyll`. No secrets, external API, or backend are needed. Additional solution checks are available in `verify-javascript.mjs` and `verify-modern.py`. Syntax and selected oracle checks are not a claim that every community solution has passed every online judge case.

## Free hosting

The live site uses [GitHub Pages for public repositories](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages). The `main` branch contains source; `gh-pages` contains the static output and publishes from its root. There is no running server, paid backend, or dependency on the original developer’s computer.

For your own fork: build, verify, package, push the contents of `dist/` to a `gh-pages` branch, and select that branch with `/ (root)` in Settings → Pages. Relative asset URLs, a scoped manifest, and a scoped service worker support project URLs. You can also serve `dist/` on another HTTPS static host. Hosting plans and usage limits remain subject to the host’s terms.

## Credits and license scope

Original Recall app code is **MIT**. Study content is separately licensed: Donne Martin’s coding challenges **Apache-2.0**, System Design Primer adaptations **CC-BY-4.0**, original study guides and Doocs reference adaptations **CC-BY-SA-4.0**, identified neetcode-gh snippets **MIT**, and fonts **SIL OFL 1.1**. The app license does not relicense these materials.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), [CONTENT_LICENSE.md](CONTENT_LICENSE.md), and the offline credits page for authors, source links, full license texts, changes, and per-image/per-code notices. Retain those notices when reusing material, including share-alike obligations for adapted CC-BY-SA content.

The public edition replaces identified copied external passages with independent writing, omits images without documented redistribution permission, and excludes raw Anki packages and earlier unsanitized history. It retains 20 credited Primer exercise diagrams. This source review reduces known risks; it cannot guarantee rights that an upstream contributor may not own.

Recall is independent and is not affiliated with or endorsed by LeetCode, NeetCode, Anki, Google, or the credited authors. It is educational practice, not an official company curriculum or a collection of actual company interview questions. Historical exercises and community code can contain outdated assumptions; check current primary documentation before applying them in production.
