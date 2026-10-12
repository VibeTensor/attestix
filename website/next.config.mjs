import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { createMDX } from "fumadocs-mdx/next";

const __dirname = dirname(fileURLToPath(import.meta.url));

function getAttestixVersion() {
  try {
    const pyproject = readFileSync(
      resolve(__dirname, "..", "pyproject.toml"),
      "utf-8"
    );
    const match = pyproject.match(/^version\s*=\s*"([^"]+)"/m);
    return match?.[1] || "0.0.0";
  } catch {
    return "0.0.0";
  }
}

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  // prebuild runs Oxlint before every build; do not invoke the removed ESLint stack.
  eslint: { ignoreDuringBuilds: true },
  images: {
    unoptimized: true,
  },
  transpilePackages: ["geist"],
  env: {
    NEXT_PUBLIC_ATTESTIX_VERSION: getAttestixVersion(),
  },
};

export default withMDX(nextConfig);
