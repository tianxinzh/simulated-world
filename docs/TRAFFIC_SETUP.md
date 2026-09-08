# Traffic operations — Simulated World

## Actual activation state

The website code, consent interface and event hooks are installed. An empty measurement ID means **no remote analytics collection**. `/monitor/` is an integration-status and local event inspector, NOT an aggregate traffic dashboard. No credentials or account ownership were fabricated. Configuration belongs to `site-config.json`; never put API secrets, access tokens or passwords there.

## Activate the three account services

### Google Analytics 4

1. In your Google Analytics account, create or select the **Simulated World** property. Use **America/Los_Angeles** as its reporting timezone and create a Web stream for the public site.
2. Copy its **G-... measurement ID**, not the numeric property ID and not an API secret.
3. In this repo, open **Actions → Configure traffic integrations → Run workflow**. Enter the measurement ID. Optional Google/Bing verification fields accept ONLY the content value, not a whole HTML tag. Blank fields keep existing values; use the disable-analytics checkbox to remove the ID explicitly.
4. Open `/monitor/`, review Analytics choices, and allow analytics. Enable the local inspector; play the embedded world and use a physical control. Confirm the events in **GA4 Realtime / DebugView**. A local queued event is not proof of provider delivery.
5. Turn OFF enhanced measurement for this stream: this implementation explicitly sends page views and the named events below. This avoids extra automatic form, scroll, outbound-click or history events, and keeps URL reporting constrained. Advertising features, Google signals and ad personalization are disabled in the installed tag.
6. Register event-scoped custom dimensions: `world`, `release`, `entry_point`, `control`, `error_code`, `acq_source`, `acq_medium`, `acq_campaign`, `acq_content`. Use the built-in language field; custom numeric parameters `load_ms` and `visible_seconds` can be registered as custom metrics.
7. Mark **engaged_play** as a key event. Do not mark `world_open` as an engaged player. Choose a retention period in GA4 deliberately (for example the shortest useful setting) and review the provider's data-sharing settings.

GA4 will only observe visitors who consent and whose browser/network permits collection. This is not a census of all visitors, and installation cannot recover earlier traffic.

### Google Search Console

Create the URL-prefix property `https://tianxinzh.github.io/simulated-world/`. Choose HTML tag verification and copy the `google-site-verification` content token into the configuration workflow. After deployment, click Verify in Search Console, then submit `sitemap.xml`. Inspect the homepage and both `/worlds/` pages. A deployed tag is not the same thing as a verified property or an indexed URL.

### Bing Webmaster Tools

Add the same public site, use its HTML meta verification value (`msvalidate.01`) in the workflow, complete verification in Bing, and submit the sitemap. Use the supported AI Performance report for citation visibility. This repository does not send automatic IndexNow submissions or claim ownership of a Bing account.

## What is measured

| Event | Definition |
|---|---|
| page_view | One manually configured top-level page view after consent; no pre-consent event replay. |
| world_open | A requested embedded world, once per player instance. |
| world_ready | The child world has drawn its first rendered frame; validated same-origin/source message. |
| world_interaction | First named control action after ready and recent trusted user input. Camera orbit alone does not count. |
| watched_play | 60 seconds of visible, at least 25%-onscreen play after ready, regardless of interaction. |
| engaged_play | The same 60 seconds plus a genuine control action; once per player instance. |
| world_error | A generic scene error or 45-second readiness timeout. Full exception messages are never sent. |
| world_end | Player unmounted, with visible seconds. Closing the browser is not guaranteed to send an end event. |
| share | Successful native share or copied canonical link. |
| github_click / download | Source or single-file download link activation; not proof of a completed download or GitHub star. |

These are play instances, not unique people. A reload/reopen is a new instance. Timers pause when the top-level document is hidden or the iframe is offscreen. They do not infer attention, and background CPU throttling may undercount. Auto-running traffic is not itself interaction. Dropped analytics due to consent or blockers must not be interpreted as simulator failure.

Standalone `airport.html` and `bayline.html` load no analytics tag. They only emit local messages to an explicitly same-origin parent. Direct standalone sessions are therefore unmeasured. Use the searchable world pages in promotional links.

## Weekly dashboard in your private GA4 account

Use an Exploration funnel: `world_open → world_ready → world_interaction → engaged_play`, broken down by world, entry point, source/medium, campaign and device. Compare non-branded Search Console clicks and impressions separately. Watch errors and load time before deciding whether a channel is low quality. For channel reporting use Traffic acquisition plus key events; the four `acq_*` dimensions preserve explicit campaign labels on the landing page but are not a cross-device attribution system.

Review each week: visitors by source; load success rate; engaged play instances; engaged play rate; visible play duration; errors by device; non-brand search clicks; AI-referred sessions. The numerator and denominator must use the same consenting population and date range. GitHub Insights counts repository activity, not Pages sessions.

## Local testing and privacy

`/monitor/` is public and noindex. It displays configuration readiness and only the current tab's optional in-memory diagnostic log. It contains no visitor database, login or private API connection. Debug preference uses sessionStorage and expires with the tab; turn it off before normal play. Consent preference uses localStorage. Browser Global Privacy Control/Do Not Track disables optional analytics. Consent can be reviewed from page footers. Revocation reloads to unload a previously running tag; it cannot delete historical provider data.

No analytics script is loaded before consent, even with an ID configured. No ads, session replay or fingerprinting were installed. Review privacy wording and provider settings for your deployment; the implementation is not a blanket legal-compliance certification.

## SEO/GEO operations

The indexable collection consists of the homepages, world pages, field guides, About and Privacy in English and Simplified Chinese. Each has its own canonical, return hreflang links, descriptive title, text and matching structured data. Raw full-screen player files are intentionally `noindex,follow`; they remain compatible download/play entry points. `/monitor/` and the campaign tool are also noindex, and are excluded from the sitemap.

`robots.txt` only applies at the HOST ROOT. Our file at `/simulated-world/robots.txt` does not control `tianxinzh.github.io`; do not claim it does. `docs/robots-host-root.txt` is a deployment template for an owned domain. We did not modify another repository or its host-wide policy. OAI-SearchBot search access is distinct from GPTBot training access; the template adds search access and does not invent a training opt-out decision. Indexing and AI citations are not guaranteed. No paid links, doorway pages, fake ratings or mass keyword pages were added.

Choose a permanent custom domain before a large publicity campaign. Configure DNS/HTTPS deliberately, then update `baseUrl`, the Pages custom domain and old redirects together. No domain was purchased or DNS changed in this release.

## References

- Google: https://developers.google.com/tag-platform/security/concepts/consent-mode
- GA4 events: https://developers.google.com/analytics/devguides/collection/ga4/events
- GA4 configuration: https://developers.google.com/analytics/devguides/collection/ga4/reference/config
- Search ownership: https://support.google.com/webmasters/answer/9008080
- Sitemaps: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Localized pages: https://developers.google.com/search/docs/specialty/international/localized-versions
- Google AI search guidance: https://developers.google.com/search/docs/appearance/ai-features
- OpenAI crawler controls: https://developers.openai.com/api/docs/bots
