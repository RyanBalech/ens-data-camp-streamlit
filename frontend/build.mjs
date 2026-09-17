import { build } from "esbuild";
await build({
  entryPoints: ["src.jsx"],
  bundle: true,
  minify: true,
  format: "iife",
  target: ["es2020"],
  outfile: "../assets/motion/header.js",
  define: { "process.env.NODE_ENV": '"production"' },
  legalComments: "linked"
});
