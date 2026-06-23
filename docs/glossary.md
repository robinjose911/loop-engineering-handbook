# Glossary

Terms used across the handbook. Each term is a unique anchor you can link to.

## Loop engineering

Designing the **outer loop** an agent runs in — prompt, context, harness, and
the loop itself — not just a single prompt. See
[what is loop engineering](01-what-is-loop-engineering.md).

## /goal

A primitive that runs **depth-first toward a single verifiable condition, then
stops**, with a separate evaluator checking the condition each pass.

## /loop

A primitive that runs on an **interval with no built-in end** — a cron in your
terminal. Safe only when governed (stop condition + cost cap).

## Loop contract

The six-field template (Goal / Context / Constraints / Done-when / Evidence /
If-blocked) that specifies a governed loop. See
[the loop contract](the-loop-contract.md).

## Maker-checker

Separating the agent that **produces** work from an **independent** evaluator
that accepts or rejects it on executable evidence (writer ≠ checker).

## Done-when

The single, verifiable stop condition. A separate checker — not the model's
confidence — decides whether it is met.

## Durability ladder

The progression from a one-shot prompt to a fully unattended automation, ordered
by how little babysitting each needs. See
[/goal and /loop basics](02-goal-and-loop-basics.md#the-durability-ladder).

## Context rot

The degradation of an agent's reliability as a single transcript grows. Loops
avoid it by starting each pass from fresh context plus a small memory file.

## LOOP.md

A small, durable **memory spine** file a loop writes/reads across passes so a
fresh-context pass knows what earlier passes already did.

## Circuit-breaker

A governance control that **halts** a loop after N consecutive no-progress or
failing passes, so a stuck loop stops instead of burning budget.

## Cost cap

A hard `$/run` ceiling that stops a loop regardless of progress — the difference
between "run until done" and "run until bankrupt."

---

Back to [the guide index](README.md).
