# egm.dev

Landing site for the Elephant-Goldfish Model, served at https://egm.dev from
GitHub Pages.

| Light | Dark |
| --- | --- |
| ![Hero, light scheme](screenshots/hero-light.png) | ![Hero, dark scheme](screenshots/hero-dark.png) |

<details>
<summary>Full page and mobile</summary>

![Full page, light scheme](screenshots/full-light.png)

![Mobile, 375px wide](screenshots/mobile.png)

</details>

## Stack

- [Astro](https://astro.build) static output, one page, no client framework.
- [gBreeze](https://www.npmjs.com/package/@material/web) (`@material/web`
  `labs/gb`) in its native-element form: the page emits the package's own
  class names (`btn`, `icon-btn`, `list-item`, `badge`, `divider`) and imports the
  package stylesheets. No custom elements, no Lit runtime.
- Google Sans Flex and Google Sans Code, self-hosted under
  `src/assets/fonts/` (OFL).

## Rules

- No analytics, no cookies, no third-party scripts, and no requests to Google
  hosts at runtime. The open-source release depends on it.
- Theme only through gBreeze tokens (`src/styles/tokens.css`) and the
  components' documented custom properties. Do not restyle component boxes.
- Keep skill names and commands identical to the repository README.

## Develop

```sh
npm install
npm run dev      # http://localhost:4321
npm run check    # astro check
npm run build    # writes dist/
npm run capture  # rebuilds, then regenerates public/og.png and screenshots/*.png
```

`npm run capture` needs a local Chrome (set `CHROME_PATH` if it is not found).
The social image comes from `scripts/og.html`; edit that file, not the PNG.
Run `npm run capture` after any visible change so the committed images stay in sync.

## Deploy

`.github/workflows/deploy-site.yml` builds and publishes `dist/` on every push
to `main` that touches `site/`, and on manual dispatch. `public/CNAME` pins the
custom domain.
