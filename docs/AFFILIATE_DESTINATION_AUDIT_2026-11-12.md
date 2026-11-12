# Affiliate destination safety audit — 2026-11-12

## Findings

- Four accessory products remain visible on the Arabic, English and French accessories pages, but their purchase links are now ordinary AliExpress marketplace search URLs. They are not affiliate links and do not imply that a seller or listing has been verified.
- Six additional accessory listings (alarm, side guards, rear footrest, rear-fender hook cover, folding-mechanism retaining ring and full scooter cover) were removed from all three public pages because their final affiliate destinations and exact product compatibility could not be verified.
- All ten historical accessory affiliate short links remain in `data/affiliate-catalog.json` for traceability only. The catalog now marks them as inactive on public pages; it does not claim that any redirect, seller, regional SKU or listing is verified.
- Five additional short links remain in `ride_match_data.json` for affiliate-only iScooter entries. Each remains explicitly marked `affiliateDestinationVerified: false`; Ride Match purchase CTAs continue to use ordinary marketplace search fallback rather than emitting those short links.
- No product specifications, eligibility flags, recommendation scoring, analytics configuration, consent behavior, AdSense code or ad settings were changed.

## Limits

The short-link host `s.click.aliexpress.com` could not be independently resolved through the available inspection route. This audit does not claim the URLs are broken or identify their final destinations. Re-enable an affiliate destination only after checking the final product URL, exact SKU/model, regional market, seller and listing specifications.

## Validation

- All three public accessories pages should contain no `s.click.aliexpress.com` URLs.
- The catalog should retain all ten historical records but show no active affiliate placement.
- The five Ride Match entries should remain unverified and should not be used as direct purchase destinations.
- Run repository site checks and live checks before merge.
