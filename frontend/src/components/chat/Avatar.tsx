"use client";

import { useState } from "react";

// Drop the photo at frontend/public/sandra.jpg. Until it exists, the
// initials show instead of a broken image.
const PHOTO_SRC = "/sandra.jpg";

export default function Avatar({ size }: { size: number }) {
  const [failed, setFailed] = useState(false);

  return (
    <div
      className="chat-avatar flex shrink-0 items-center justify-center overflow-hidden rounded-full font-semibold"
      style={{ width: size, height: size, fontSize: size * 0.36 }}
    >
      {failed ? (
        "SR"
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={PHOTO_SRC}
          alt="Sandra Stephanie Raveendran"
          className="h-full w-full object-cover"
          onError={() => setFailed(true)}
        />
      )}
    </div>
  );
}
