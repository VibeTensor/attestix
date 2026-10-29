This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/basic-features/font-optimization) to automatically optimize and load Inter, a custom Google Font.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.


## Static blog navigation regression

Article cards, research links, related posts and the article back link use native
HTML navigation. A failed Next.js static RSC request can otherwise navigate to a
transport `.txt` URL. The generated `public/_redirects` rules recover those shared
URLs on Cloudflare Pages. Text exports elsewhere, including `llms.txt`, remain text.

`npm run build` runs the redirect tests and generates a rule for every published
`content/*.mdx` article. Keep unrelated redirects outside the managed blog block.

For the browser regression, install Python Playwright and its Chromium browser
and install the Wrangler CLI separately (`npm install --global wrangler`). Build
the site, then run these commands in separate terminals from `website/`:

```sh
wrangler pages dev out --ip 127.0.0.1 --port 8797
python scripts/blog-navigation.browser.py http://127.0.0.1:8797
```

This uses local Pages routing and aborts RSC fetches in the test browser. It checks
all published blog/research links, related posts, the back link and old shared TXT
URLs with query strings. It does not publish or change a cloud resource.
