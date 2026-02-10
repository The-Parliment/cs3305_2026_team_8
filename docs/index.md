# The Parliament

**A microservices-based social networking platform for UCC students**

## Overview

The Parliament is a location-aware social platform that enables students to build inner circles, create events, form groups, and discover who's nearby in real-time.

## Core Features

**Inner Circles** - Connect with close friends through invitation-based circles where you can share location and events exclusively.

**Events** - Create and RSVP to events with flexible visibility (public, private, inner circle, or group-specific). Organize gatherings with attendee limits and automated invitations.

**Groups** - Form and join communities around shared interests. Public groups for discovery, private groups for exclusivity.

**Location Sharing** - Real-time map showing friends' locations with granular privacy controls. See who's nearby and gauge distances to meet up.


## Architecture

The Parliament uses a microservices architecture with six core services:

- **Auth Service** - User registration, authentication, and profile management
- **Circle Service** - Inner circle invitations and friend connections
- **Groups Service** - Group creation, membership, and discovery
- **Events Service** - Event management and RSVP tracking
- **Proximity Service** - Real-time location sharing and map functionality

Built with FastAPI, PostgreSQL, Docker, NGINX,  and Jinja frontend.

## Documentation Structure

- **System Overview** - Architecture diagrams, end-to-end flows, and directory structure
- **Service Documentation** - API references and design docs for each microservice
- **Development Guide** - Setup instructions, testing, and deployment

## Quick Links

- [Architecture Overview](Architecture.md)
- [End-to-End Flow](end_to_end_flow.md)
- [API Reference - Auth](auth/auth_api.md)

---

