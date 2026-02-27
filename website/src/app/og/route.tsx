import { siteConfig } from "@/lib/config";
import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const postTitle = searchParams.get("title") || siteConfig.description;
  const font = fetch(
    new URL("../../assets/fonts/Inter-SemiBold.ttf", import.meta.url)
  ).then((res) => res.arrayBuffer());
  const fontData = await font;

  return new ImageResponse(
    (
      <div
        style={{
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
        }}
      >
        {/* Subtle grid background */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "linear-gradient(rgba(79,70,229,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(79,70,229,0.06) 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />

        {/* Indigo accent glow */}
        <div
          style={{
            position: "absolute",
            top: "-50%",
            left: "50%",
            transform: "translateX(-50%)",
            width: "600px",
            height: "600px",
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(79,70,229,0.2) 0%, transparent 70%)",
          }}
        />

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            position: "relative",
          }}
        >
          {/* Gold shield icon */}
          <div
            style={{
              display: "flex",
              width: "64px",
              height: "64px",
              borderRadius: "16px",
              background: "linear-gradient(135deg, #E1A32C, #d4922a)",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "32px",
              color: "#0f1219",
              fontWeight: "800",
            }}
          >
            A
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              fontSize: "56px",
              fontWeight: "700",
              marginTop: "24px",
              textAlign: "center",
              color: "#ffffff",
              width: "80%",
              letterSpacing: "-0.04em",
              lineHeight: 1.1,
            }}
          >
            {postTitle}
          </div>
          <div
            style={{
              display: "flex",
              fontSize: "18px",
              fontWeight: "500",
              marginTop: "20px",
              color: "#4F46E5",
              letterSpacing: "0.05em",
            }}
          >
            {siteConfig.name}
          </div>
          <div
            style={{
              display: "flex",
              fontSize: "14px",
              fontWeight: "400",
              marginTop: "8px",
              color: "rgba(255,255,255,0.5)",
            }}
          >
            47 MCP Tools | 9 Modules | W3C Compliant | EU AI Act Ready
          </div>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
      fonts: [
        {
          name: "Inter",
          data: fontData,
          style: "normal",
        },
      ],
    }
  );
}
