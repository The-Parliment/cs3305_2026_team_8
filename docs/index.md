# GoClub

**A microservices-based social networking platform for UCC students**

## Overview

GoClub is a location-aware social platform that enables students to build inner circles, create events, form groups, and discover who's nearby in real-time.

## Core Features

**Inner Circles** — Connect with close friends through invitation-based circles. Circle membership is the privacy boundary for location sharing — only accepted circle members can see each other on the proximity map.

**Events** — Create public or private events. Public events are open to anyone; private events require an invite from the host or a join request that the host approves.

**Groups** — Form and join communities around shared interests. Public groups are open to join directly; private groups require a request and owner approval.

**Location Sharing** — Real-time map showing circle members nearby. The proximity service uses Valkey geospatial queries to find who's within a given radius, filtered to your circle.

## Architecture

GoClub uses a microservices architecture with six backend services:

- **Auth Service** — User registration, login, JWT issuance, and profile management
- **Circles Service** — Invitation-based friend circles
- **Groups Service** — Public and private group creation and membership
- **Events Service** — Event creation, invitations, attendance, and geographic search
- **Proximity Service** — Real-time location tracking via Valkey (not PostgreSQL)
- **User Service** — Follow and friend relationships

Built with FastAPI, PostgreSQL, Valkey, Docker, Nginx, and a Jinja2 server-side rendered frontend.

## Documentation Structure

- **System Overview** — [Architecture](Architecture.md) · [Directory Structure](Directory_structrure.md) · [End-to-End Flow](end_to_end_flow.md)
- **Core Concepts** — [The `requests` Table](request_table.md) · [Common Library](common_lib.md)
- **Service Docs** — API reference and design doc for each microservice

| Service | API Reference | Design Doc |
|---------|--------------|------------|
| Auth | [auth_api.md](auth/auth_api.md) | [auth_design.md](auth/auth_design.md) |
| Circles | [circles_api.md](circles/circles_api.md) | [circles_design.md](circles/circles_design.md) |
| Groups | [groups_api.md](groups/groups_api.md) | [groups_design.md](groups/groups_design.md) |
| Events | [events_api.md](events/events_api.md) | [events_design.md](events/events_design.md) |
| Proximity | [proximity_api.md](proximity/proximity_api.md) | [proximity_design.md](proximity/proximity_design.md) |