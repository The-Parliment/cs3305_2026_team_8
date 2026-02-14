
> **⚠ NOTE **
>
> I had a look through a few chapters of The AOSA — worth a glance if you have not seen it. 
> The thing that struck me is that it is not an architecture spec. The system gets 
> described, but only enough to set up the interesting part: why things were done the way 
> they were, what went wrong, what got reconsidered. The lessons are the point. The tech 
> is just the story they hang off.
> That is what I think we should aim for here. The stuff that is still worth reading in 
> five years is not "we used FastAPI and Docker" — it is the thinking behind the decisions 
> we made under pressure with the constraints we had.
---

# Introduction

> **Intent:** Distinguish GoClub from a typical student project, name the three engineering problems the report covers, and signal that this is a story about decisions — not a feature description.


---

# Requirements and Constraints

> **Intent:** Establish the forces that shaped every decision so the reader can evaluate the choices that follow.

## Functional Requirements

> **Intent:** Name the five capabilities and flag proximity as the one that breaks the standard assumptions.


## Non-Functional Constraints

> **Intent:** Cover team size, deployment environment, privacy, and scope — each linked forward to where it becomes a real decision.


---

# System Overview

> **Intent:** Give the reader a map of the full stack before the detailed sections begin.


---

# Challenge One — Coordinating Parallel Development

> **Intent:** Tell the story of how four developers built five services in parallel without integration becoming a bottleneck.

## Agile Process and the Mapping of Stories to Services

> **Intent:** Show how keeping story boundaries inside service boundaries enabled parallel work — and what went wrong before that discipline existed.


## Git Discipline and the Pull Request as Integration Gate

> **Intent:** Explain why the PR was the integration gate and why maintaining that discipline under deadline pressure mattered.


## MkDocs as a Development Contract

> **Intent:** Argue that documentation written during development is a design tool that enables parallel work — not a deliverable produced at the end.


> **Key insight:** Documentation written *during* development is a design
> tool. Documentation written *after* development is a historical record.
> Only the former enables parallel work.

---

# Challenge Two — Reproducible Deployment of a Multi-Service Stack

> **Intent:** Explain the deployment problem and the discipline behind the Docker Compose solution — not what Docker is, but why it mattered here.

## Container-Per-Service and the Isolation Benefit

> **Intent:** Explain what containerisation bought the team in terms of consistency, isolation, and conflict-free collaboration.


## NGINX as the Unifying Gateway

> **Intent:** Explain why a single gateway — single origin, extensible by addition — was the right choice.


## The Two-Phase Development Loop

> **Intent:** Describe the local-dev/full-stack-dev split and why keeping both modes viable avoided slow feedback loops.


## The Nuclear Option

> **Intent:** Frame the full state-reset command as a first-class operational tool, not an admission of failure.


---

# The Core Services

> **Intent:** Describe each service through the lens of its boundary decisions and notable design choices — not its API.

## Auth Service

> **Intent:** Explain the identity-only scope and why local JWT verification removes both a latency cost and a single point of failure.


## Circles Service

> **Intent:** Explain the invitation state machine as the core design decision and why the circle boundary is also the privacy boundary.


## Groups Service

> **Intent:** Contrast Groups with Circles and explain the public/private flag and the deliberately simple owner-only permission model.


## Events Service

> **Intent:** Describe the visibility model and how Events delegates membership resolution rather than duplicating it.


---

# Challenge Three — When the Database Is the Wrong Tool

> **Intent:** Tell the story of discovering that GPS data does not fit a relational store, characterising the mismatch precisely, and finding Valkey as the purpose-built solution.

## The Problem with Location in a Relational Database

> **Intent:** Identify the three specific mismatches precisely — this is the diagnosis that justifies everything that follows.


> **Three specific mismatches identified:** high write frequency against a
> single-writer store; spatial calculation against a relational query engine;
> volatile state forced into durable storage. Each pointed toward the same
> conclusion: location data needs a different tool.

## The Research Process and the Discovery of Valkey

> **Intent:** Show how characterising data properties first led to finding an existing tool rather than building a custom solution.


## The Resulting Two-Tier Data Architecture

> **Intent:** Name the pattern and summarise the role of each tier.


> **The transferable lesson:** The most valuable engineering move in this
> project was the decision not to write code. Recognising that a problem has
> prior art — and knowing how to search for it — is a more valuable skill
> than the ability to implement a solution from scratch.

---

# Cross-Cutting Concerns

> **Intent:** Cover the two elements that span all services and explain the trade-offs of each choice.

## The Common Library

> **Intent:** Justify centralised shared code as the right coupling decision at this scale, while honestly acknowledging the trade-off.


## JWT and Distributed Authentication

> **Intent:** Explain local token verification and what was deliberately left out of scope.


---

# Future Improvements

> **Intent:** Record the honest backlog as evidence the team understands the gap between academic scope and production readiness — not as apologies.


## User Lifecycle Event Bus

> **Intent:** Identify the user-deletion cleanup problem and describe an event bus as the correct solution using existing infrastructure.


## Priority Two API Completion

> **Intent:** Note that descoped work is documented and intentional, not a gap.


---

# Lessons Learned


## On Deployment: Make the Environment a First-Class Artefact

> **Intent:** Argue that containerising early and treating docker-compose.yml as canonical saved the team from an entire class of failures.


---

# Conclusion

> **Intent:** Close by arguing that the problems encountered — and the thinking required — are the same ones that appear at any scale.


- **GitHub:** <https://github.com/The-Parliment/cs3305_2026_team_8>
- **Documentation:** <https://the-parliment.github.io/cs3305_2026_team_8/>
