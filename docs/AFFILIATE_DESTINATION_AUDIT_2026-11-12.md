# Affiliate destination safety audit — 2026-11-12

## Findings

- Four AliExpress short links were embedded as direct purchase CTAs on the Arabic, English and French accessories pages. Their final product destinations and seller listings could not be independently resolved or verified during this audit.
- These four live CTAs have been replaced in all three locales with ordinary AliExpress marketplace search URLs. The links no longer use the `sponsored` relation, and the copy now clearly says they are search results rather than verified listings.
- Five additional short links remain in `ride_match_data.json` for affiliate-only iScooter entries. Each remains explicitly marked `affiliateDestinationVerified: false`; the Ride Match purchase CTA continues to use ordinary marketplace search fallback rather than emitting those short links.
- No product specifications, eligibility flags, recommendation scoring, analytics configuration, consent behavior, AdSense code or ad settings were changed.

## Limits

The short-link host `s.click.aliexpress.com` could not be opened by the available inspection route, so this audit does not claim the URLs are broken or identify their final destinations. Re-enable an affiliate destination only after checking the final product URL, exact SKU/model, regional market, seller and listing specifications.

## Validation expected

- Confirm all three accessories pages contain no `s.click.aliexpress.com` URLs.
- Confirm the five Ride Match entries remain unverified and are not used as direct purchase destinations.
- Run the repository site checks and live checks after merge.
