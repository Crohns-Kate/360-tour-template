/**
 * ============================================================
 *  PROPERTY TOUR CONFIG
 *  Edit this file only — no need to touch app.js or index.html
 * ============================================================
 *
 *  HOW TO USE FOR A NEW PROPERTY:
 *  1. Duplicate this entire folder (360-tour/)
 *  2. Drop your equirectangular panorama JPGs into ./images/
 *  3. Edit the values below: title, subtitle, scenes, image paths
 *  4. Open index.html in a browser (or serve via a local server)
 *
 *  PANORAMA IMAGE REQUIREMENTS:
 *  - Format: equirectangular (2:1 aspect ratio), e.g. 6000×3000 px
 *  - File type: JPG or PNG
 *  - Place images in the ./images/ folder beside index.html
 * ============================================================
 */

const TOUR_CONFIG = {

  // ── PROPERTY DETAILS ────────────────────────────────────────
  propertyTitle:    "Arjan Villa",           // Displayed in the top-left badge
  propertySubtitle: "Padonan",               // Shown beneath badge

  // ── DEFAULT SCENE ───────────────────────────────────────────
  // Must match one of the scene `id` values below
  defaultSceneId: "living",

  // ── GLOBAL AUTOROTATE ───────────────────────────────────────
  // Speed in degrees/second. Positive = clockwise. Set 0 to disable.
  autoRotateSpeed: 1.2,

  // ── SCENES ──────────────────────────────────────────────────
  // Add or remove objects in this array to add/remove rooms.
  // Each scene is one panorama image.
  scenes: [
    {
      id:        "living",               // Unique ID (used by hotspots)
      title:     "Front View",           // Shown in the scene selector
      thumbnail: "./images/thumb-1.jpg", // Small preview image (optional)

      // ── REPLACE THIS PATH with your equirectangular panorama ──
      panorama:  "./images/scene-1.jpg",

      // Starting camera angle when this scene loads
      yaw:   0,     // Horizontal angle in degrees  (-180 to 180)
      pitch: 0,     // Vertical angle in degrees   (-90 to 90)
      hfov:  100,   // Horizontal field of view     (50–120 recommended)

      // Hotspots: clickable arrows that jump to another scene.
      // Delete or leave the array empty if you don't want hotspots.
      hotspots: [
        {
          pitch:         -10,       // Where the hotspot dot appears (vertical)
          yaw:            80,       // Where the hotspot dot appears (horizontal)
          targetSceneId: "pool",    // Which scene to switch to on click
          text:          "Pool Deck"// Tooltip label
        },
        {
          pitch:         -5,
          yaw:           -120,
          targetSceneId: "master",
          text:          "Master Suite"
        }
      ]
    },

    {
      id:        "pool",
      title:     "Pool & Outdoor Terrace",
      thumbnail: "./images/thumb-2.jpg",

      // ── REPLACE THIS PATH ──
      panorama:  "./images/scene-2.jpg",

      yaw:   0,
      pitch: 0,
      hfov:  110,

      hotspots: [
        {
          pitch:         -8,
          yaw:            160,
          targetSceneId: "living",
          text:          "Living Area"
        },
        {
          pitch:         -5,
          yaw:           -30,
          targetSceneId: "master",
          text:          "Master Suite"
        }
      ]
    },

    {
      id:        "master",
      title:     "Master Suite",
      thumbnail: "./images/thumb-3.jpg",

      // ── REPLACE THIS PATH ──
      panorama:  "./images/scene-3.jpg",

      yaw:   45,    // Start rotated to face the bed
      pitch: -5,
      hfov:  95,

      hotspots: [
        {
          pitch:         -10,
          yaw:            200,
          targetSceneId: "living",
          text:          "Back to Living"
        }
      ]
    }

    // ── ADD MORE SCENES HERE ────────────────────────────────
    // Copy the block above, give it a unique id, update panorama path.
    // Example:
    // ,{
    //   id:        "kitchen",
    //   title:     "Gourmet Kitchen",
    //   thumbnail: "./images/thumb-4.jpg",
    //   panorama:  "./images/scene-4.jpg",
    //   yaw: 0, pitch: 0, hfov: 100,
    //   hotspots: []
    // }
  ]

};
