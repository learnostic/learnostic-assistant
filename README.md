# Learnostic Assistant

AI-powered Q&A assistant for Learnostic staff. Ask questions about students in
plain English and get instant, read-only answers pulled from the database —
powered by Claude and text-to-SQL.

## What it does (current scope)

- Staff type a natural-language question about student data (e.g. "which
  students haven't logged in for 2 weeks?").
- Claude translates the question into a **read-only** SQL query against the
  Learnostic database.
- The query runs, and the result is turned back into a plain-English answer.
- No write access, no side effects — this is a query/insight tool only.

## Future direction

This repo is the foundation for Learnostic's broader internal AI system:
agents that turn student data into insight and action — expanding from
natural-language Q&A into things like renewal-risk scoring and other staff
workflows. The text-to-SQL assistant is the first building block; later
phases will layer additional agents on top of the same data access and
reasoning core.

## Status

Early setup — scaffolding only, no implementation yet.

## Tech stack

- Claude (Anthropic API) for natural language → SQL translation and
  answer generation
- Read-only connection to the Learnostic database
- (Backend/frontend framework TBD)

## Getting started

TBD — project scaffolding in progress.
