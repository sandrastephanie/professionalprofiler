import type { Metadata, Viewport } from "next";
import { connection } from "next/server";
import { Bebas_Neue, DM_Sans } from "next/font/google";

import { readOwner } from "@/lib/owner";
import "./globals.css";
// After globals.css, so this site's look overrides the plain defaults.
import "./theme.css";

// The chat's face in this fork: DM Sans, as Sandra's first version had. A
// variable font, so no weights are listed and `globals.css` can ask for any.
// Michael's original loads Nunito from `fonts/nunito/`; the files are still
// there, unused, so going back is this block and one line in theme.css.
const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
});

// A single weight, and capitals only — there is no bold to ask for (see
// `--chat-font-title-weight` in theme.css). From Google rather than a file in
// `fonts/`: the Fontshare copy's licence forbids putting it in a public
// repository, and Google's is the same Dharma Type design under the OFL.
const bebas = Bebas_Neue({
  variable: "--font-bebas",
  weight: "400",
  subsets: ["latin"],
});

/**
 * Why a viewport export exists at all.
 *
 * Next's default meta tag is fine for width and scale, but says nothing about
 * the two things this page needs on a phone. `colorScheme` tells the browser to
 * paint its own surfaces — the canvas behind the document, the overscroll area,
 * the scrollbars — to match the page. Michael's navy original says dark; this
 * fork's theme.css is a light page, so it says light. `interactiveWidget` asks for the on-screen keyboard to shorten the
 * layout viewport, so the `dvh` the layout is built on keeps meaning what the
 * layout assumes it means while someone is typing.
 *
 * Deliberately no `maximumScale` / `userScalable: false`. They are the usual
 * reflex against iOS zooming when a small field takes focus, but they take
 * pinch-zoom away from everyone; the composer asks for 16px on phones instead,
 * which fixes the same thing and costs nobody anything.
 */
export const viewport: Viewport = {
  colorScheme: "light",

  // theme.css's --chat-bg, so the browser chrome is the page's own colour
  // rather than a shade off it. Hardcoded because a meta tag cannot read a custom
  // property — if that `--chat-bg` moves, this has to move with it.
  themeColor: "#f4f5f7",

  interactiveWidget: "resizes-content",

  // No `viewportFit: "cover"`. It painted the old steel-blue bar up under
  // the notch; with the bar the page's navy, the browser's own fill around
  // the page is the same colour, so nothing is lost. And it cost a blank row:
  // DuckDuckGo on Android reports the status bar as `safe-area-inset-top`
  // even with the page below it, and the bar padded itself down by that much
  // — fixed the same way on mringdal.com. Without it every inset is 0, so the
  // `.shell-*` rules' env() terms are simply inert.
};

export async function generateMetadata(): Promise<Metadata> {
  // `await connection()` is not ceremony. A layout uses no request-time API of
  // its own, so without this Next may prerender the metadata and freeze the
  // title at build — which is exactly the baking this change exists to avoid.
  // Opting into dynamic rendering is what makes the environment readable here.
  await connection();

  const owner = readOwner();

  const title = `Workchat with ${owner.name}`;
  // Sandra's own line, in her voice: this is what a link preview says under
  // the title when the page is shared.
  const description =
    "Ask me about my work. Product manager, fintech & B2B SaaS.";

  // A preview image has to be an absolute URL, and only the server knows the
  // site's address (SITE_URL, set from SITE_DOMAIN in docker-compose.prod.yaml).
  // Unset, as in development and the tests, the preview goes without its image
  // base rather than pointing at a guess.
  const siteUrl = process.env.SITE_URL;

  return {
    title,
    description,
    metadataBase: siteUrl ? new URL(siteUrl) : undefined,
    openGraph: {
      type: "website",
      title,
      description,
      // 400 x 400, so a small square preview rather than a wide banner.
      images: [
        {
          url: "/sandra.jpg",
          width: 400,
          height: 400,
          alt: "Sandra Stephanie Raveendran",
        },
      ],
    },
    twitter: {
      card: "summary",
      title,
      description,
      images: ["/sandra.jpg"],
    },
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${dmSans.variable} ${bebas.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
