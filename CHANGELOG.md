# Changelog

## v0.2.0 - Policy-driven agent packet verification

- Added IntentASM examples for safe and unsafe agent packets.
- Added IntentBin roundtrip for `.intentasm -> .intentbin -> .intentasm`.
- Added `recv / verify / execute` receiver flow with tagged CLI output.
- Added JSON policy files under `policies/`.
- Added safe vs unsafe demo centered on `make demo-safety`.
- Added trace replay for executed and rejected packets.
