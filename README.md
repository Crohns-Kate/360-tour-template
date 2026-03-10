# 360 Property Tour — Reusable Starter Kit

A production-ready static web app for luxury real estate virtual tours,
powered by [Pannellum](https://pannellum.org). No build tools, no frameworks —
just open `index.html`.

---

## Quick Start

```
360-tour/
├── index.html      ← tour page (do not edit for reuse)
├── styles.css      ← styling (edit for branding)
├── app.js          ← tour logic (do not edit for reuse)
├── config.js       ← ✏ EDIT THIS to configure a property
├── images/
│   ├── scene-1.jpg ← equirectangular panorama images
│   ├── scene-2.jpg
│   ├── scene-3.jpg
│   ├── thumb-1.jpg ← optional small thumbnails (200×130 px)
│   ├── thumb-2.jpg
│   └── thumb-3.jpg
└── README.md
```

### Run locally

Because browsers block local `file://` image loading, serve via a simple HTTP server:

```bash
# Python 3
cd 360-tour
python3 -m http.server 8080
# then open http://localhost:8080
```

Or use VS Code Live Server, MAMP, Caddy, Nginx — any static file server works.

---

## Replacing Images (New Property)

1. Shoot or process equirectangular 360° photos (2:1 ratio, JPG recommended, 4000–8000 px wide).
2. Drop them into the `images/` folder.
3. In `config.js`, update each scene's `panorama` path:

```js
panorama: "./images/your-photo.jpg",
```

4. Optionally add small 200×130 thumbnail previews:

```js
thumbnail: "./images/your-thumb.jpg",
```

---

## Editing config.js

Everything you need to change lives in `config.js`.

### Property title & subtitle

```js
propertyTitle:    "Villa Serene",
propertySubtitle: "Private Estate · Byron Bay, NSW",
```

### Default opening scene

```js
defaultSceneId: "living",   // must match an id in the scenes array
```

### Autorotate speed

```js
autoRotateSpeed: 1.5,   // degrees/second. Set 0 to disable.
```

### Starting camera angle per scene

```js
yaw:   45,    // horizontal angle (-180 to 180)
pitch: -5,    // vertical angle (-90 to 90)
hfov:  100,   // field of view in degrees (80–120 recommended)
```

---

## Adding More Scenes

Copy and paste a scene block inside the `scenes: []` array:

```js
{
  id:        "kitchen",             // must be unique
  title:     "Gourmet Kitchen",     // shown in scene buttons
  thumbnail: "./images/thumb-4.jpg",
  panorama:  "./images/scene-4.jpg",
  yaw: 0, pitch: 0, hfov: 100,
  hotspots: []
}
```

Then add hotspots in other scenes pointing to `"kitchen"` if you want arrow links.

---

## Hotspots

Hotspots are clickable arrows inside the panorama that jump to another scene.

```js
hotspots: [
  {
    pitch:         -10,       // vertical position of the arrow dot
    yaw:            80,       // horizontal position of the arrow dot
    targetSceneId: "pool",    // scene id to jump to on click
    text:          "Pool Deck" // tooltip label on hover
  }
]
```

To find good `yaw`/`pitch` values, temporarily enable Pannellum's debug mode by
setting `hotSpotDebug: true` in `app.js` under the `default` config block,
then click inside the viewer to log coordinates in the browser console.

---

## Creating a New Property (Duplicate Template)

1. Copy the entire `360-tour/` folder and rename it, e.g. `villa-sunrise/`.
2. Drop your new panorama images into `villa-sunrise/images/`.
3. Edit `villa-sunrise/config.js` — update title, images, scenes.
4. That's it. `app.js` and `index.html` are identical across all properties.

---

## Embedding in a Listing Page (iframe)

```html
<iframe
  src="https://your-domain.com/villa-oceana/"
  width="100%"
  height="600"
  frameborder="0"
  allowfullscreen
  loading="lazy"
  title="Villa Oceana 360 Tour"
></iframe>
```

Deploy the folder to any static host: Netlify, Vercel, GitHub Pages, Cloudflare Pages, or your own server.

---

## Image Processing Tips (Twilight / HDR Effect)

For the premium twilight look (bright interior + warm exterior dusk):

- **Lightroom / Photoshop**: Use luminosity masks to separately adjust interior
  lights and exterior sky. Blend two exposures.
- **PTGui**: Stitch multi-row 360 bracket shots with HDR blending.
- **AI enhancement**: Upload raw panoramas to tools like Midjourney (img2img),
  Gemini Advanced image editing, or Adobe Firefly for twilight relighting.
  Then use the enhanced equirectangular output in this app.
- **BoxBrownie API**: Their day-to-dusk and virtual twilight service returns
  processed equirectangular images you can drop straight into `images/`.

---

## Browser Support

Chrome, Firefox, Safari, Edge (all modern versions). Requires WebGL.

---

## License

MIT — free to use and modify for commercial property listings.
