# Simulated World

Free, interactive miniature worlds for your browser. **BAYPORT** is a Bay Area-inspired airport on an oak workbench; **BAYLINE** is a San Francisco-inspired model railway. Operate physical tabletop controls, explore the details and watch day turn to night.

[Open the collection](https://tianxinzh.github.io/simulated-world/) · [BAYPORT airport](https://tianxinzh.github.io/simulated-world/worlds/bayport/) · [BAYLINE railway](https://tianxinzh.github.io/simulated-world/worlds/bayline/) · [中文](https://tianxinzh.github.io/simulated-world/zh/)

![BAYPORT miniature airport](assets/previews/bayport.webp)

## Play or download

The world pages include an on-demand player, requirements and controls. Nothing loads a WebGL context until you request a world. Download `airport.html` or `bayline.html` and open it in Chrome for the standalone experience. These files load only Three.js remotely; geometry, textures, signs and synthesized sound are generated locally. An internet connection for Three.js is still required. No analytics script is included in the standalone files.

[Field guides](https://tianxinzh.github.io/simulated-world/guides/) cover both control panels, the source architecture and a day-night airport tour. These are artistic dioramas, not exact maps, cockpit simulators or professional training tools. Development used AI assistance and iterative browser testing.

## Site and source organization

- `airport.html`, `bayline.html`: complete standalone worlds; shared-style controls and local-only parent event messages.
- `worlds/`, `guides/`, `about/`, `privacy/`, `zh/`: generated search-readable English/Chinese pages.
- `tools/build_growth.py`: static page/content generator, metadata and sitemap. No Python packages required.
- `tools/templates/home.html`: editable source for the existing gallery design; generated `index.html` is not the template.
- `assets/growth.js`: hosted-page playback, consent-gated GA4 integration, local event inspection and campaign tools.
- `site-config.json`: public site URL, optional GA4 measurement ID and ownership verification values. **Never store credentials or API secrets here.**
- `tests/growth-check.cjs`: Chromium tests for pages, layout, actual WebGL controls, event timing and privacy.
- `tools/package_site.py`: copies only public runtime assets to `_site/` for deployment.

This public repository contains the demo gallery and its discovery/measurement integration. The separate private website repository remains separate; no private application code or secrets have been copied here.

## Build and test

```sh
python3 tools/build_growth.py
python3 tools/package_site.py
npm install --no-save --no-package-lock playwright@1.55.1
npx playwright install chromium
mkdir -p /tmp/sw-site
ln -s "$PWD" /tmp/sw-site/simulated-world
python3 -m http.server 8765 --directory /tmp/sw-site
# In another terminal:
node tests/growth-check.cjs
```

The test server path mirrors the current GitHub Pages project path. Generated pages are committed for compatibility with branch-based Pages, and the deployment workflow also rebuilds the packaged site. Content and language links use `baseUrl` from the versioned configuration.

## Traffic and search setup

[Setup instructions](docs/TRAFFIC_SETUP.md) · [Launch kit](docs/LAUNCH_KIT.md) · [Integration inspector](https://tianxinzh.github.io/simulated-world/monitor/) · [Campaign link builder](https://tianxinzh.github.io/simulated-world/tools/campaign-builder/)

**Without a real measurement ID there is no remote traffic collection.** The inspector shows local diagnostics, not aggregate visitor counts. Use Actions → **Configure traffic integrations** to add the public GA4 and Google/Bing verification values, then complete verification and sitemap submission in those provider accounts. Consent is required before the Google tag loads. No indexing, citations, visitor counts or rankings are guaranteed.

The project-path `robots.txt` is a host-root deployment template, not control of `tianxinzh.github.io/robots.txt`. See the setup instructions before a custom-domain migration.

## License

MIT. Retain the license notice when reusing code. Three.js is provided by its CDN and retains its own license.
