# Gemini CLI worker contract

This repository uses Gemini CLI only as a read-only development worker in the
Jev experiment branch. Its command wrapper always uses `--approval-mode plan`
and `--sandbox`.

- Work only on `test/jev`.
- Read the nearest `AGENTS.md`, `TASKS.md`, and relevant spec before answering.
- Return evidence, risks, and focused test suggestions. Do not edit files,
  create a worktree, start a service, access credentials, or call a remote
  product service.
- Never decide a robot action, change a ROS contract, choose an intent, or
  relax confirmation, privacy, or safety rules.
- Treat JEV as an unapproved hosted experiment. No API key, audio, image, or
  transcription may be requested or sent by this worker.

The human integrator is the only writer. A Terra reviewer must review the
integrated diff before a safety-relevant change is accepted.
