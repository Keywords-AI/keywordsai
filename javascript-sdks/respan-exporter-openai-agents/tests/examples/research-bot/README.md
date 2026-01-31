# Research Bot

This example shows how to orchestrate several agents to produce a detailed research report.

## Files

- **main.ts** – CLI entrypoint that asks for a query and runs the workflow using `ResearchManager`.
- **manager.ts** – Coordinates the planning, web searching and report writing stages.
- **agents.ts** – Contains the agents: a planner that suggests search terms, a search agent that summarizes results and a writer that generates the final report.

## Usage

From the repository root run:

```bash
pnpm examples:research-bot
```
