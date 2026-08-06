---
name: prototype
description: "Creates quick, isolated Flutter code for testing juiciness — spin, bounce and glow animations."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
argument-hint: "[mechanic-name] (e.g. spin-bounce, glow-effect)"
---

# `prototype` — the juiciness lab

Gambling games live on visual feedback. This skill creates an isolated animation prototype.

## Instructions

1. Create the file `prototypes/[mechanic-name]/main.dart`.
2. Write a minimal `runApp` with a simple screen.
3. Add a Flame GameWidget if you are testing physics or Flame effects.
4. Add Flutter animations if you are testing UI (glow, popup).
5. Do not use dependencies from `lib/` (prototypes must build on their own).
6. Print the command `flutter run -t prototypes/[mechanic-name]/main.dart -d chrome` to run it.
