# InkFig Main System

InkFig is a graduation project for Hebron University. It is a web platform where students can create accounts, publish their artwork, discover work created by other students, and interact with it.

This repository contains the main backend service for InkFig's business features and workflows.

## Product vision

InkFig is an art-focused community platform with some similarities to Pinterest, while remaining tailored to the university context. Each student has an account and a personal body of work. Students can upload and display different kinds of art, including digital artwork made with tools such as Photoshop, hand-created artwork, and other art forms.

The platform will support multiple ways of presenting and discovering artwork. The exact presentation modes will be designed later. Students will be able to view one another's work and interact with it through likes.

## Planned capabilities

- Student account creation, authentication, and profiles.
- Artwork uploads across multiple art types and media.
- Personal student portfolios and shared artwork discovery.
- Likes and other appropriate community interactions.
- Preference and recommendation algorithms for personalized discovery.
- Natural-language image search: a user enters a text description and a model returns artwork that matches it.
- Teacher-created events in which students can participate by submitting artwork.
- Event submission moderation: a submitted work remains pending until the teacher accepts or rejects it.
- Rejection feedback: when a teacher rejects an event submission, the teacher provides a reason.
- Multiple roles and granular permissions.
- Account administration, including activating and deactivating accounts.

## Event workflow

1. A teacher creates an event.
2. A student submits artwork to the event.
3. The submission remains pending and is not included in the event yet.
4. The teacher reviews the submission.
5. If accepted, the artwork becomes part of the event.
6. If rejected, the student receives the teacher's rejection reason.

## Project status

This document records the initial product direction, not a complete specification. Detailed requirements, artwork presentation modes, algorithms, roles, permissions, and additional workflows will be defined as the project develops.
