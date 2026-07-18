<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# ADR-004: Media-Type Strategy

**Status:** Accepted for `v0.1.0-alpha.1`.

## Decision

Project-specific media types remain provisional and unregistered during Alpha.1. Documentation states this explicitly and does not imply IANA registration.

The signature protected header uses `typ = atp+jws` and the provisional `cty = application/agent-trust-passport+json`.
