import type { Owner } from "./owner";

/**
 * Who this is, when nobody says otherwise.
 *
 * Split out of `owner.ts` so it can be read from the browser. That module
 * reads `process.env` at call time and must never reach a bundle; these are
 * four string literals and can go anywhere. The embed needs them because it
 * has no server render to hand it an owner — the host page's attributes are
 * the only channel, and a page that sets none should still get a working chat
 * rather than an undefined name in the header.
 */
export const DEFAULT_OWNER: Owner = {
  name: "Sandra",
  githubUrl: "https://github.com/sandrastephanie",
  linkedinUrl:
    "https://www.linkedin.com/in/sandra-stephanie-raveendran/",
  // Empty means "no such link", not "use a default".
  websiteUrl: "",
};
