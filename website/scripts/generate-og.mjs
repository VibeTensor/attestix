/**
 * Build-time OG image generator.
 * Produces public/og-image.png (1200x630) using satori + sharp.
 * Runs as a prebuild step so static export has a real OG image.
 */

import satori from "satori";
import sharp from "sharp";
import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

const fontData = readFileSync(
  join(root, "src", "assets", "fonts", "Inter-SemiBold.ttf")
);

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
        backgroundColor: "#0f1219",
        fontSize: 32,
        fontWeight: 600,
        position: "relative",
      },
      children: [
        // Subtle grid overlay
        {
          type: "div",
          props: {
            style: {
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundImage:
                "linear-gradient(rgba(79,70,229,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(79,70,229,0.06) 1px, transparent 1px)",
              backgroundSize: "60px 60px",
            },
          },
        },
        // Indigo accent glow
        {
          type: "div",
          props: {
            style: {
              position: "absolute",
              top: "-300px",
              left: "50%",
              transform: "translateX(-50%)",
              width: "600px",
              height: "600px",
              borderRadius: "50%",
              background:
                "radial-gradient(circle, rgba(79,70,229,0.2) 0%, transparent 70%)",
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
            },
            children: [
              // Gold shield icon
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    width: "64px",
                    height: "64px",
                    borderRadius: "16px",
                    background: "linear-gradient(135deg, #E1A32C, #d4922a)",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "32px",
                    color: "#0f1219",
                    fontWeight: 800,
                  },
                  children: "A",
                },
              },
              // Title
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    fontSize: "56px",
                    fontWeight: 700,
                    marginTop: "24px",
                    textAlign: "center",
                    color: "#ffffff",
                    letterSpacing: "-0.04em",
                    lineHeight: 1.1,
                  },
                  children: "Attestation Infrastructure for AI Agents",
                },
              },
              // Brand name
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    fontSize: "18px",
                    fontWeight: 500,
                    marginTop: "20px",
                    color: "#4F46E5",
                    letterSpacing: "0.05em",
                  },
                  children: "Attestix",
                },
              },
              // Stats strip
              {
                type: "div",
                props: {
                  style: {
                    display: "flex",
                    fontSize: "14px",
                    fontWeight: 400,
                    marginTop: "8px",
                    color: "rgba(255,255,255,0.5)",
                  },
                  children:
                    "47 MCP Tools  |  9 Modules  |  W3C Compliant  |  Apache 2.0",
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

const png = await sharp(Buffer.from(svg)).png({ quality: 90 }).toBuffer();

const outPath = join(root, "public", "og-image.png");
await sharp(png).toFile(outPath);

console.log(`Generated ${outPath} (${png.length} bytes)`);
