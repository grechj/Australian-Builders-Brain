---
type: Reference
title: Trade sequence
description: Which trades usually have to finish before the next can start, for booking and readiness checks.
tags: [phases, trades, scheduling]
status: draft
sources:
  - id: beam_phase_engine
    resource: beam_agent/prompts/phase_engine.py
    title: Construction sequence by Joshua Grech
    author: human:grechj
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

A rule of thumb for booking trades. Use it to check a trade is ready before
confirming a booking. It's a typical residential sequence, not a rule; the
job's program wins.[^beam_phase_engine]

| Trade | Usually waits for |
|---|---|
| Concreter | nothing (can start early) |
| Plumber | nothing (can start early) |
| Steel fixer | concreter |
| Carpenter | concreter |
| Bricklayer | carpenter |
| Roofer | carpenter |
| Electrician | carpenter, roofer |
| Waterproofer | plumber |
| Plasterer | electrician, plumber |
| Tiler | plasterer, waterproofer |
| Painter | plasterer, carpenter |
| Joiner | plasterer |
| Cabinet maker | plasterer |
| Carpet layer | painter |
| Landscaper | concreter, plumber |
| Glazier | carpenter |
| Renderer | bricklayer |
| Fire services | electrician |

Consultants who aren't on this list but gate progress: architect, engineer, certifier.

Track bookings in the [Trade Booking and Lead Time Tracker](/documents/trade_booking_lead_time_tracker.md).

[^beam_phase_engine]: Construction sequence by Joshua Grech
