# Tracking & Pixel Setup Instructions

**For:** Margaret
**Page to track:** `canggu-villas.html` (the landing page Facebook ads link to)
**Time needed:** ~30 minutes total

---

## Overview

We need 3 things set up so we can measure ad performance:

| Tool | What it does | Cost |
|------|-------------|------|
| **Meta Pixel** | Tracks who visits from Facebook/Instagram ads, and who clicks WhatsApp/Call/Email | Free |
| **Hotjar** | Records visitor sessions + heatmaps so we can see where people look and click | Free (up to 35 sessions/day) |
| **Google Analytics (GA4)** | General website analytics — where visitors come from, how long they stay | Free |

---

## STEP 1: Meta (Facebook) Pixel

This is the most important one. It lets Facebook Ads know when someone from our ad actually enquires.

### Create the Pixel

1. Go to **[Meta Events Manager](https://business.facebook.com/events_manager)**
2. Log in with the Facebook account that runs the ads
3. Click the green **"Connect Data Sources"** button
4. Select **"Web"** and click **"Connect"**
5. Name it **"North Canggu Villas"**
6. Click **"Create Pixel"**
7. Choose **"Install code manually"** (NOT the partner option)
8. You'll see a block of code — we don't need to copy it ourselves
9. **Just note down the Pixel ID** — it's a long number like `1234567890123456`
   - You can find it at the top of Events Manager next to the pixel name

### What to send back

Just the **Pixel ID number**. That's all we need. Example: `549283716204835`

---

## STEP 2: Hotjar

Hotjar records actual visitor sessions so we can watch what they do on the page — where they scroll, what they tap, where they drop off.

### Create the account

1. Go to **[hotjar.com](https://www.hotjar.com)** and click **"Start free"**
2. Sign up with email (use whichever email you prefer)
3. When asked for your website URL, enter: `crohns-kate.github.io`
4. Choose the **"Basic"** plan (free — 35 sessions/day is plenty for now)
5. It will show you a tracking code — we don't need to copy it
6. **Just note down the Site ID** — it's a number like `3456789`
   - You can find it in Settings > Sites & Organizations

### What to send back

Just the **Hotjar Site ID number**. Example: `3847261`

---

## STEP 3: Google Analytics (GA4)

Optional but recommended. Gives us traffic data beyond just Facebook.

### Create the property

1. Go to **[analytics.google.com](https://analytics.google.com)**
2. Log in with a Google account
3. Click the gear icon (Admin) at the bottom left
4. Click **"Create"** > **"Property"**
5. Property name: **"North Canggu Villas"**
6. Timezone: **Australia** (or wherever makes sense)
7. Click through the setup steps
8. When asked about platform, choose **"Web"**
9. Website URL: `crohns-kate.github.io/360-tour-template/canggu-villas.html`
10. Stream name: **"Landing Page"**
11. Click **"Create stream"**
12. You'll see a **Measurement ID** that looks like `G-XXXXXXXXXX`

### What to send back

Just the **Measurement ID**. Example: `G-AB1CD2EF3G`

---

## What happens next

Once you send back these 3 values, we'll add them to the landing page code. The tracking will then:

- **Meta Pixel:** Automatically track every visitor from Facebook/Instagram ads. When someone taps WhatsApp, Call, or Email, it fires a "Lead" conversion event back to Facebook — so we can see cost-per-enquiry in Ads Manager
- **Hotjar:** Start recording visitor sessions automatically. You can watch recordings and see heatmaps at hotjar.com
- **GA4:** Track all visitors, traffic sources, time on page, bounce rate

### Conversions we'll track

| Action | What fires | Where you see it |
|--------|-----------|-----------------|
| Someone lands on page from ad | `PageView` | Meta Events Manager + GA4 |
| Someone taps **WhatsApp** button | `Lead` event (value: "whatsapp") | Meta Events Manager — shows as conversion |
| Someone taps **Call** button | `Lead` event (value: "phone") | Meta Events Manager — shows as conversion |
| Someone taps **Email** button | `Lead` event (value: "email") | Meta Events Manager — shows as conversion |
| Someone taps **Enquire** sticky button | `Lead` event (value: "enquire") | Meta Events Manager — shows as conversion |
| Someone opens the **360 tour** | `ViewContent` event | Meta Events Manager |

### Setting up conversions in Facebook Ads Manager

After the pixel is live and getting events, you'll need to:

1. Go to **Events Manager** > select the pixel
2. Click **"Custom Conversions"** in the left sidebar
3. Create a custom conversion for **"Lead"** events
4. When creating ad campaigns, select this as your **conversion event**
5. Facebook will then optimize delivery to find people most likely to enquire

---

## Summary — what to send back

| Item | What it looks like |
|------|--------------------|
| Meta Pixel ID | A long number: `549283716204835` |
| Hotjar Site ID | A shorter number: `3847261` |
| GA4 Measurement ID | Starts with G-: `G-AB1CD2EF3G` |

Send all 3 and we'll have tracking live within minutes.
