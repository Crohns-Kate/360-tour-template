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
  defaultSceneId: "front",

  // ── DAY / DUSK MODE ─────────────────────────────────────────
  // Default view when the tour loads. Toggle button switches between them.
  // "dusk" = AI-rendered dusk panoramas, "day" = original daytime panoramas
  defaultMode: "dusk",

  // ── GLOBAL AUTOROTATE ───────────────────────────────────────
  // Speed in degrees/second. Positive = clockwise. Set 0 to disable.
  autoRotateSpeed: 1.2,

  // ── SCENES ──────────────────────────────────────────────────
  // Add or remove objects in this array to add/remove rooms.
  // Each scene is one panorama image.
  scenes: [

    // ── Scene 1: Front View (exterior) ──────────────────────
    {
      id:           "front",
      title:        "Front View",
      panorama:     "./images/scene-1-dusk.jpg",
      panoramaDay:  "./images/scene-1-day.jpg",
      panoramaDusk: "./images/scene-1-dusk.jpg",
      yaw: 0, pitch: 0, hfov: 100,
      hotspots: [
        { pitch: -10, yaw: 80,   targetSceneId: "pool",    text: "Pool Deck" },
        { pitch: -8,  yaw: -40,  targetSceneId: "living",  text: "Living & Dining" }
      ]
    },

    // ── Scene 2: Pool Deck (exterior) ───────────────────────
    {
      id:           "pool",
      title:        "Pool Deck",
      panorama:     "./images/scene-2-day.jpg",
      panoramaDay:  "./images/scene-2-day.jpg",
      yaw: 0, pitch: 0, hfov: 105,
      hotspots: [
        { pitch: -8,  yaw: 160,  targetSceneId: "front",   text: "Front View" },
        { pitch: -8,  yaw: -20,  targetSceneId: "garden",  text: "Garden" },
        { pitch: -5,  yaw: 40,   targetSceneId: "living",  text: "Living & Dining" }
      ]
    },

    // ── Scene 3: Garden (exterior) ──────────────────────────
    {
      id:           "garden",
      title:        "Garden",
      panorama:     "./images/scene-3-day.jpg",
      panoramaDay:  "./images/scene-3-day.jpg",
      yaw: 0, pitch: 0, hfov: 105,
      hotspots: [
        { pitch: -10, yaw: -60,  targetSceneId: "pool",    text: "Pool Deck" },
        { pitch: -8,  yaw: 120,  targetSceneId: "front",   text: "Front View" }
      ]
    },

    // ── Scene 4: Living & Dining (interior) ─────────────────
    {
      id:           "living",
      title:        "Living & Dining",
      panorama:     "./images/scene-4-day.jpg",
      panoramaDay:  "./images/scene-4-day.jpg",
      yaw: 90, pitch: 0, hfov: 100,
      hotspots: [
        { pitch: -5,  yaw: -160, targetSceneId: "front",   text: "Front Door" },
        { pitch: -8,  yaw: 60,   targetSceneId: "pool",    text: "Pool Deck" },
        { pitch: -5,  yaw: -60,  targetSceneId: "kitchen", text: "Kitchen" },
        { pitch: -5,  yaw: 140,  targetSceneId: "lounge",  text: "Lounge" }
      ]
    },

    // ── Scene 5: Lounge (interior) ──────────────────────────
    {
      id:           "lounge",
      title:        "Lounge",
      panorama:     "./images/scene-5-day.jpg",
      panoramaDay:  "./images/scene-5-day.jpg",
      yaw: 0, pitch: 0, hfov: 100,
      hotspots: [
        { pitch: -8,  yaw: -80,  targetSceneId: "living",  text: "Living & Dining" },
        { pitch: -8,  yaw: 60,   targetSceneId: "pool",    text: "Pool Deck" },
        { pitch: -5,  yaw: 160,  targetSceneId: "kitchen", text: "Kitchen" }
      ]
    },

    // ── Scene 6: Kitchen & Dining (interior) ────────────────
    {
      id:           "kitchen",
      title:        "Kitchen",
      panorama:     "./images/scene-6-day.jpg",
      panoramaDay:  "./images/scene-6-day.jpg",
      yaw: 90, pitch: 0, hfov: 100,
      hotspots: [
        { pitch: -5,  yaw: -90,  targetSceneId: "living",  text: "Living & Dining" },
        { pitch: -8,  yaw: 30,   targetSceneId: "hallway", text: "Hallway" }
      ]
    },

    // ── Scene 7: Hallway & Staircase (interior) ─────────────
    {
      id:           "hallway",
      title:        "Hallway & Stairs",
      panorama:     "./images/scene-7-day.jpg",
      panoramaDay:  "./images/scene-7-day.jpg",
      yaw: 0, pitch: 0, hfov: 100,
      hotspots: [
        { pitch: -5,  yaw: 160,  targetSceneId: "living",  text: "Living & Dining" },
        { pitch: -5,  yaw: -90,  targetSceneId: "kitchen", text: "Kitchen" }
      ]
    }

  ]

};
