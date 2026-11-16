---
title: About this chat (built by Michael Ringdal)
type: about-this-app
tags: [about-this-chat, workchat, michael-ringdal, credits, who-built-this, how-it-works]
summary: "This chat application is Michael Ringdal's build, a project of his called workchat. I use a copy of it with my own CV content and design. The engineering described here is Michael's work, not mine."
---

## Who built this
Michael Ringdal designed and built this application end to end. It is his own project, workchat (github.com/buzzgreyday/workchat), and the original runs on his own site, mringdal.com. I'm using a copy of it and fine-tuning it for my needs: the CV content is mine, and I changed the colours and added my photo. If you ask who made this chat, the answer is Michael. The sections below describe his work.

## Technologies
Backend: Python, FastAPI, SQLAlchemy (async), Alembic migrations, PostgreSQL, JWT-based access tokens, OpenAI tool-calling.
Frontend: Next.js, React, TypeScript, plain CSS (built with Tailwind CSS until October 2026).
Infrastructure: Docker Compose, Caddy reverse proxy with automatic HTTPS.

## What it does
- The chat interface a hiring manager is using right now: questions are answered by an LLM agent that calls retrieval tools (search_cv, get_full_entry) over these CV records, rather than a static PDF resume.
- Backend: FastAPI serving a streaming chat endpoint, async PostgreSQL access via SQLAlchemy, Alembic-managed schema migrations, and per-hirer JWT access tokens scoped by expiry and query count.
- Frontend: Next.js/TypeScript chat UI with streamed responses, styled in plain CSS. It began on Tailwind CSS and moved off it in October 2026, to keep button and effect work in readable stylesheets.
- Guest trial: a visitor without a link can be offered a few questions, earned with an invisible proof-of-work in the browser and limited to one trial per IP address per day. Addresses are never stored, only a keyed hash that is deleted when its day ends.
- Infrastructure: containerized with Docker Compose; Caddy handles TLS and reverse proxying in production.

## Engineering details
- **Security.** Per-hirer JWT access tokens, scoped by both expiry and a query
  count, with tokens stored hashed rather than in plain text. The system prompt
  is added server-side only and stripped from both the JSON and streaming
  responses, so it never reaches the client; a `system` message arriving in a
  request is dropped rather than forwarded to the model. Tool-call rounds are
  bounded so a misbehaving model cannot loop indefinitely.
- **Streaming.** Replies arrive token by token over server-sent events (SSE),
  parsed incrementally on the client and rendered as they land.
- **Asynchronous throughout.** Async FastAPI handlers, async SQLAlchemy against
  PostgreSQL, and async file access, so streaming a long reply does not block
  other requests. Concurrency is the normal case here, not an afterthought.
- **Shell scripting.** Bash underpins the operational side: the container
  entrypoint that applies Alembic migrations on start, and the backup scripts
  that dump the database and pull the private resources off the server.
- **Caching.** The tool schema and CV index are loaded once and shared across
  every conversation rather than re-read per request.
- **Idempotent retries.** Every question carries an idempotency key, and the
  server also hashes the message, so a dropped connection can be retried
  without spending a second question, and a key can never buy a different one.
  Two sends in the same instant ask once.
- **Atomic spending.** One conditional `UPDATE` checks that the token is not
  revoked or expired and still has questions left, and spends one, so
  concurrent requests cannot overspend. Each request runs in a single
  transaction that commits or rolls back as a whole.
- **Tamper-proof history.** The server signs the conversation history it
  returns and accepts only history it signed, so a client cannot pad or
  rewrite the context sent to the model.
- **Abuse protection with privacy by design.** Guests earn a trial with an
  invisible proof-of-work, limited per IP address and per day. Addresses are
  never stored, only a keyed hash under a key that changes daily, and
  scheduled purges delete what is no longer needed.
- **Clean layering.** The chat turn is a pipeline of generators: the model loop
  knows nothing of SSE, and the route knows nothing of OpenAI. Auth is a
  FastAPI dependency rather than middleware, so each endpoint gets the check
  it needs, and tests can swap it in one place.
- **Progress without leaking.** While a reply is pending, the stream sends
  fixed status codes ("thinking", "searching the CV"), which the frontend turns
  into words. What the model searched for never reaches the browser.
- **Embeddable by contract.** The frontend also ships as a `<workchat-chat>` web
  component that Michael's own site, mringdal.com, loads at runtime. Its attributes, event, custom
  state (on while it works, for the host to style), shadow parts and CSS
  variables are a documented public API, and a contract test runs the website's
  own end-to-end suite against the freshly built component to catch drift.
- **Measured quality.** An eval suite drives the live chat with real questions
  and measures how often it wrongly denies something the CV contains, so a
  prompt or model change is judged by a number.
- **Checked in CI.** Typed Python (mypy), tests, a check that the database
  schema matches its migrations, and a production deploy that waits for
  approval.
