/**
 * Build-time asset generator.
 * Produces:
 *   - public/og-image.png (1200x630 OG image)
 *   - src/app/favicon.ico (32x32 + 16x16 ICO from atx_gold.svg)
 *   - public/apple-touch-icon.png (180x180)
 * Runs as a prebuild step.
 */

import satori from "satori";
import sharp from "sharp";
import { readFileSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

const fontData = readFileSync(
  join(root, "src", "assets", "fonts", "Inter-SemiBold.ttf")
);

// --- OG Image (1200x630) ---

const WIDTH = 1200;
const HEIGHT = 630;

const svg = await satori(
  {
    type: "div",
    props: {
      style: {
        height: "100%",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#0a0d14",
        position: "relative",
        overflow: "hidden",
      },
      children: [
        // Large indigo radial glow (top center)
        {
          type: "div",
          props: {
            style: {
              position: "absolute",
              top: "-200px",
              left: "50%",
              transform: "translateX(-50%)",
              width: "900px",
              height: "600px",
              borderRadius: "50%",
              background:
                "radial-gradient(ellipse, rgba(79,70,229,0.25) 0%, rgba(79,70,229,0.08) 40%, transparent 70%)",
            },
          },
        },
        // Gold accent glow (bottom right)
        {
          type: "div",
          props: {
            style: {
              position: "absolute",
              bottom: "-150px",
              right: "-100px",
              width: "500px",
              height: "400px",
              borderRadius: "50%",
              background:
                "radial-gradient(ellipse, rgba(225,163,44,0.12) 0%, transparent 60%)",
            },
          },
        },
        // Subtle emerald glow (bottom left)
        {
          type: "div",
          props: {
            style: {
              position: "absolute",
              bottom: "-100px",
              left: "-50px",
              width: "400px",
              height: "300px",
              borderRadius: "50%",
              background:
                "radial-gradient(ellipse, rgba(5,150,105,0.08) 0%, transparent 60%)",
            },
          },
        },
        // Content
        {
          type: "div",
          props: {
            style: {
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              position: "relative",
              padding: "0 80px",
            },
            children: [
              // Brand name
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    fontSize: "72px",
                    fontWeight: 700,
                    letterSpacing: "-0.04em",
                    color: "#E1A32C",
                  },
                  children: "Attestix",
                },
              },
              // Tagline
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    fontSize: "28px",
                    fontWeight: 600,
                    marginTop: "16px",
                    textAlign: "center",
                    color: "rgba(255,255,255,0.9)",
                    letterSpacing: "-0.02em",
                    lineHeight: 1.3,
                  },
                  children: "Attestation Infrastructure for AI Agents",
                },
              },
              // Divider line
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    width: "80px",
                    height: "2px",
                    marginTop: "28px",
                    background:
                      "linear-gradient(90deg, transparent, #4F46E5, transparent)",
                  },
                },
              },
              // Stats strip
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    fontSize: "15px",
                    fontWeight: 500,
                    marginTop: "28px",
                    color: "rgba(255,255,255,0.45)",
                    letterSpacing: "0.04em",
                    gap: "24px",
                  },
                  children: [
                    {
                      type: "span",
                      props: {
                        children: "47 MCP Tools",
                        style: { display: "flex" },
                      },
                    },
                    {
                      type: "span",
                      props: {
                        children: "\u00b7",
                        style: {
                          display: "flex",
                          color: "rgba(79,70,229,0.5)",
                        },
                      },
                    },
                    {
                      type: "span",
                      props: {
                        children: "9 Modules",
                        style: { display: "flex" },
                      },
                    },
                    {
                      type: "span",
                      props: {
                        children: "\u00b7",
                        style: {
                          display: "flex",
                          color: "rgba(79,70,229,0.5)",
                        },
                      },
                    },
                    {
                      type: "span",
                      props: {
                        children: "W3C Compliant",
                        style: { display: "flex" },
                      },
                    },
                    {
                      type: "span",
                      props: {
                        children: "\u00b7",
                        style: {
                          display: "flex",
                          color: "rgba(79,70,229,0.5)",
                        },
                      },
                    },
                    {
                      type: "span",
                      props: {
                        children: "Apache 2.0",
                        style: { display: "flex" },
                      },
                    },
                  ],
                },
              },
              // URL
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    fontSize: "13px",
                    fontWeight: 500,
                    marginTop: "32px",
                    color: "#4F46E5",
                    letterSpacing: "0.06em",
                  },
                  children: "attestix.io",
                },
              },
            ],
          },
        },
      ],
    },
  },
  {
    width: WIDTH,
    height: HEIGHT,
    fonts: [
      {
        name: "Inter",
        data: fontData,
        style: "normal",
      },
    ],
  }
);

const ogPng = await sharp(Buffer.from(svg)).png({ quality: 90 }).toBuffer();
const ogPath = join(root, "public", "og-image.png");
await sharp(ogPng).toFile(ogPath);
console.log(`Generated ${ogPath} (${ogPng.length} bytes)`);

// --- Favicons from atx_gold.svg (transparent background) ---

const logoSvgRaw = readFileSync(join(root, "public", "atx_gold.svg"), "utf-8");
// Remove the dark background rect to get a transparent favicon
const logoSvgTransparent = logoSvgRaw.replace(
  /<rect width="180" height="180" fill="#232c30"\/>/,
  ""
);
const logoSvg = Buffer.from(logoSvgTransparent);

// Apple Touch Icon (180x180) - keep original with background for contrast on iOS
const logoSvgOriginal = readFileSync(join(root, "public", "atx_gold.svg"));
const appleTouchPath = join(root, "public", "apple-touch-icon.png");
await sharp(logoSvgOriginal).resize(180, 180).png().toFile(appleTouchPath);
console.log(`Generated ${appleTouchPath}`);

// Favicon PNGs (transparent background)
const favicon32 = await sharp(logoSvg).resize(32, 32).png().toBuffer();
const favicon16 = await sharp(logoSvg).resize(16, 16).png().toBuffer();

// Build ICO file (contains both 32x32 and 16x16 PNGs)
function buildIco(images) {
  const headerSize = 6;
  const dirEntrySize = 16;
  const dirSize = dirEntrySize * images.length;
  let dataOffset = headerSize + dirSize;

  // Header: reserved(2) + type(2) + count(2)
  const header = Buffer.alloc(headerSize);
  header.writeUInt16LE(0, 0); // reserved
  header.writeUInt16LE(1, 2); // type = ICO
  header.writeUInt16LE(images.length, 4);

  const dirEntries = [];
  const imageBuffers = [];

  for (const { width, height, data } of images) {
    const entry = Buffer.alloc(dirEntrySize);
    entry.writeUInt8(width >= 256 ? 0 : width, 0);
    entry.writeUInt8(height >= 256 ? 0 : height, 1);
    entry.writeUInt8(0, 2); // color palette
    entry.writeUInt8(0, 3); // reserved
    entry.writeUInt16LE(1, 4); // color planes
    entry.writeUInt16LE(32, 6); // bits per pixel
    entry.writeUInt32LE(data.length, 8); // image data size
    entry.writeUInt32LE(dataOffset, 12); // offset
    dirEntries.push(entry);
    imageBuffers.push(data);
    dataOffset += data.length;
  }

  return Buffer.concat([header, ...dirEntries, ...imageBuffers]);
}

const icoBuffer = buildIco([
  { width: 32, height: 32, data: favicon32 },
  { width: 16, height: 16, data: favicon16 },
]);

const faviconPath = join(root, "src", "app", "favicon.ico");
writeFileSync(faviconPath, icoBuffer);
console.log(`Generated ${faviconPath} (${icoBuffer.length} bytes)`);
