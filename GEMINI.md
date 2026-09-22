# Gemini model worker contract

This repository uses Antigravity CLI (`agy`) with a Gemini model only as a
read-only development worker in the Jev experiment branch. Its command wrapper
always uses `--sandbox` and `--print-timeout 2m`.

Run the worker from the operator's authenticated desktop terminal. A headless
runner without access to the Antigravity keyring can report that it is not
logged in; do not copy tokens or loosen permissions to work around that.

In headless mode, the wrapper supplies a small context bundle from tracked
files. The worker must not inspect the workspace with native file tools or run
shell commands. Extra context is added only through `--file <relative-path>`;
paths containing secret-like names are rejected before the request is sent.

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
