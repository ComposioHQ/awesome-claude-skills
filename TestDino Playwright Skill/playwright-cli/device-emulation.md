# Device and Environment Emulation

> **When to use**: Testing how your application behaves on different devices, screen sizes, geolocation, locales, timezones, color schemes, and network conditions — all from the CLI without needing physical devices.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage, [running-custom-code.md](running-custom-code.md) for `run-code` syntax

## Quick Reference

```bash
# Device emulation via config
playwright-cli open https://example.com --config=iphone.json

# Viewport resizing
playwright-cli resize 375 812                    # iPhone viewport
playwright-cli resize 1920 1080                  # Desktop viewport

# Geolocation
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 40.7128, longitude: -74.0060 });
}"

# Color scheme
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"
```

## Viewport Emulation

The simplest form of device testing — set the viewport size to match a target device:

### Common Viewport Sizes

```bash
# Desktop
playwright-cli resize 1920 1080    # Full HD monitor
playwright-cli resize 1440 900     # MacBook Pro 15"
playwright-cli resize 1366 768     # Common laptop
playwright-cli resize 2560 1440    # QHD / 2K monitor

# Tablet
playwright-cli resize 1024 768     # iPad landscape
playwright-cli resize 768 1024     # iPad portrait
playwright-cli resize 834 1194     # iPad Pro 11"
playwright-cli resize 1194 834     # iPad Pro 11" landscape
playwright-cli resize 820 1180     # iPad Air

# Mobile
playwright-cli resize 430 932      # iPhone 14 Pro Max
playwright-cli resize 393 852      # iPhone 14 Pro
playwright-cli resize 390 844      # iPhone 14 / 13 / 12
playwright-cli resize 375 812      # iPhone X / 11
playwright-cli resize 360 800      # Samsung Galaxy S21
playwright-cli resize 412 915      # Pixel 7
playwright-cli resize 320 568      # iPhone SE (1st gen)
```

### Test Responsive Breakpoints

```bash
# Common CSS breakpoints
playwright-cli resize 320 568      # xs: Extra small
playwright-cli screenshot --filename=responsive-xs.png

playwright-cli resize 576 768      # sm: Small
playwright-cli screenshot --filename=responsive-sm.png

playwright-cli resize 768 1024     # md: Medium
playwright-cli screenshot --filename=responsive-md.png

playwright-cli resize 992 768      # lg: Large
playwright-cli screenshot --filename=responsive-lg.png

playwright-cli resize 1200 900     # xl: Extra large
playwright-cli screenshot --filename=responsive-xl.png

playwright-cli resize 1400 900     # xxl: Extra extra large
playwright-cli screenshot --filename=responsive-xxl.png
```

## Full Device Emulation

For accurate device testing, you need more than just viewport — device scale factor, user agent, touch support, and mobile behavior. Use a config file or `run-code`.

### Config File Approach

Create a config file for a specific device:

**`iphone14.json`**
```json
{
  "viewport": { "width": 390, "height": 844 },
  "deviceScaleFactor": 3,
  "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
  "isMobile": true,
  "hasTouch": true
}
```

```bash
playwright-cli open https://example.com --config=iphone14.json
```

**`pixel7.json`**
```json
{
  "viewport": { "width": 412, "height": 915 },
  "deviceScaleFactor": 2.625,
  "userAgent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
  "isMobile": true,
  "hasTouch": true
}
```

**`ipad-pro.json`**
```json
{
  "viewport": { "width": 834, "height": 1194 },
  "deviceScaleFactor": 2,
  "userAgent": "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
  "isMobile": true,
  "hasTouch": true
}
```

### Programmatic Device Emulation

Use `run-code` to check or modify device properties:

```bash
# Check current device properties
playwright-cli run-code "async page => {
  return await page.evaluate(() => ({
    userAgent: navigator.userAgent,
    viewport: { width: window.innerWidth, height: window.innerHeight },
    devicePixelRatio: window.devicePixelRatio,
    touchSupport: 'ontouchstart' in window,
    platform: navigator.platform
  }));
}"
```

## Geolocation

Override the browser's reported GPS location — test store locators, delivery zones, location-based content.

### Set Location

```bash
# New York
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 40.7128, longitude: -74.0060 });
}"

# London
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 51.5074, longitude: -0.1278 });
}"

# Tokyo
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 35.6762, longitude: 139.6503 });
}"

# Sydney
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: -33.8688, longitude: 151.2093 });
}"

# São Paulo
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: -23.5505, longitude: -46.6333 });
}"
```

### Update Location Mid-Session

Simulate a user moving between locations:

```bash
# Start in San Francisco
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
}"

playwright-cli goto https://example.com/nearby-stores
playwright-cli screenshot --filename=sf-stores.png

# Move to Los Angeles
playwright-cli run-code "async page => {
  await page.context().setGeolocation({ latitude: 34.0522, longitude: -118.2437 });
}"

playwright-cli reload
playwright-cli screenshot --filename=la-stores.png
```

### Clear Geolocation Override

```bash
playwright-cli run-code "async page => {
  await page.context().clearPermissions();
}"
```

### Geolocation via Config

Set geolocation when opening the browser:

**`geo-nyc.json`**
```json
{
  "geolocation": { "latitude": 40.7128, "longitude": -74.0060 },
  "permissions": ["geolocation"]
}
```

```bash
playwright-cli open https://example.com --config=geo-nyc.json
```

## Locale and Timezone

Test internationalization by changing the browser's locale and timezone.

### Via Config File

**`locale-de.json`**
```json
{
  "locale": "de-DE",
  "timezoneId": "Europe/Berlin"
}
```

**`locale-ja.json`**
```json
{
  "locale": "ja-JP",
  "timezoneId": "Asia/Tokyo"
}
```

```bash
playwright-cli open https://example.com --config=locale-de.json
```

### Verify Locale and Timezone

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(() => ({
    language: navigator.language,
    languages: navigator.languages,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    dateFormat: new Date('2024-01-15').toLocaleDateString(),
    numberFormat: (1234567.89).toLocaleString(),
    currencyFormat: new Intl.NumberFormat(navigator.language, {
      style: 'currency',
      currency: 'USD'
    }).format(1234.56)
  }));
}"
```

### Common Locale + Timezone Combinations

| Region | Locale | Timezone |
|--------|--------|----------|
| US East | `en-US` | `America/New_York` |
| US West | `en-US` | `America/Los_Angeles` |
| UK | `en-GB` | `Europe/London` |
| Germany | `de-DE` | `Europe/Berlin` |
| France | `fr-FR` | `Europe/Paris` |
| Japan | `ja-JP` | `Asia/Tokyo` |
| China | `zh-CN` | `Asia/Shanghai` |
| India | `hi-IN` | `Asia/Kolkata` |
| Brazil | `pt-BR` | `America/Sao_Paulo` |
| Australia | `en-AU` | `Australia/Sydney` |
| Arabia | `ar-SA` | `Asia/Riyadh` |

## Color Scheme

Test dark mode, light mode, and high contrast:

```bash
# Dark mode
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"
playwright-cli screenshot --filename=dark-mode.png

# Light mode
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'light' });
}"
playwright-cli screenshot --filename=light-mode.png

# System preference (no override)
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'no-preference' });
}"
```

## Reduced Motion

Test accessibility for users who prefer reduced motion:

```bash
# Enable reduced motion
playwright-cli run-code "async page => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
}"

# Check if your CSS respects it
playwright-cli run-code "async page => {
  return await page.evaluate(() =>
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
}"
```

## Forced Colors (High Contrast)

Test Windows High Contrast mode:

```bash
playwright-cli run-code "async page => {
  await page.emulateMedia({ forcedColors: 'active' });
}"
playwright-cli screenshot --filename=high-contrast.png
```

## Permissions

Grant or deny browser permissions:

```bash
# Grant multiple permissions
playwright-cli run-code "async page => {
  await page.context().grantPermissions([
    'geolocation',
    'notifications',
    'camera',
    'microphone'
  ]);
}"

# Grant for specific origin
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['notifications'], {
    origin: 'https://example.com'
  });
}"

# Clear all permissions (reset to defaults)
playwright-cli run-code "async page => {
  await page.context().clearPermissions();
}"
```

Available permissions: `geolocation`, `notifications`, `camera`, `microphone`, `clipboard-read`, `clipboard-write`, `payment-handler`, `midi`, `midi-sysex`, `ambient-light-sensor`, `accelerometer`, `gyroscope`, `magnetometer`, `background-sync`

## Network Condition Emulation

Simulate slow networks to test loading states and performance:

```bash
# Simulate slow 3G
playwright-cli run-code "async page => {
  const client = await page.context().newCDPSession(page);
  await client.send('Network.emulateNetworkConditions', {
    offline: false,
    downloadThroughput: 500 * 1024 / 8,     // 500 kbps
    uploadThroughput: 500 * 1024 / 8,        // 500 kbps
    latency: 400                              // 400ms RTT
  });
}"

# Simulate offline mode
playwright-cli run-code "async page => {
  const client = await page.context().newCDPSession(page);
  await client.send('Network.emulateNetworkConditions', {
    offline: true,
    downloadThroughput: 0,
    uploadThroughput: 0,
    latency: 0
  });
}"

# Restore normal network
playwright-cli run-code "async page => {
  const client = await page.context().newCDPSession(page);
  await client.send('Network.emulateNetworkConditions', {
    offline: false,
    downloadThroughput: -1,
    uploadThroughput: -1,
    latency: 0
  });
}"
```

**Note**: CDP sessions only work with Chromium-based browsers.

## Common Patterns

### Multi-Device Screenshot Suite

```bash
#!/bin/bash
URL="https://example.com"
playwright-cli open $URL

devices=("1920:1080:desktop" "768:1024:tablet" "375:812:mobile")
for device in "${devices[@]}"; do
  IFS=':' read -r w h name <<< "$device"
  playwright-cli resize $w $h
  playwright-cli screenshot --filename="device-$name.png"
done

playwright-cli close
```

### Geo-Based Content Testing

```bash
locations=("40.7128:-74.0060:nyc" "51.5074:-0.1278:london" "35.6762:139.6503:tokyo")

for loc in "${locations[@]}"; do
  IFS=':' read -r lat lng name <<< "$loc"
  playwright-cli run-code "async page => {
    await page.context().grantPermissions(['geolocation']);
    await page.context().setGeolocation({ latitude: $lat, longitude: $lng });
  }"
  playwright-cli reload
  playwright-cli screenshot --filename="geo-$name.png"
done
```

### Accessibility Emulation Suite

```bash
playwright-cli open https://example.com

# Standard view
playwright-cli screenshot --filename=a11y-standard.png

# Dark mode
playwright-cli run-code "async page => { await page.emulateMedia({ colorScheme: 'dark' }); }"
playwright-cli screenshot --filename=a11y-dark.png

# High contrast
playwright-cli run-code "async page => { await page.emulateMedia({ forcedColors: 'active' }); }"
playwright-cli screenshot --filename=a11y-high-contrast.png

# Reduced motion
playwright-cli run-code "async page => { await page.emulateMedia({ reducedMotion: 'reduce', forcedColors: 'none' }); }"
playwright-cli screenshot --filename=a11y-reduced-motion.png

playwright-cli close
```

## Tips

- **Viewport alone isn't device emulation** — real device testing needs user agent, touch support, and device scale factor via config files
- **Geolocation requires permission** — always `grantPermissions(['geolocation'])` before `setGeolocation()`
- **Locale/timezone must be set at open time** — use config files since they can't be changed mid-session
- **CDP features are Chromium-only** — network throttling via CDP doesn't work in Firefox or WebKit
- **Test the combination** — dark mode + reduced motion + specific locale together reveals issues that each alone won't catch
