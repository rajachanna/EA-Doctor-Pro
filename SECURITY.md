# Security and data boundaries

EA Doctor Pro analyzes pasted text only. It never runs the pasted MQL, compiles source, connects to brokers, executes remote programs or sends scans to remote APIs.

**Browser analyzer:** file.text() and text area only; the downloadable JSON contains findings, synthesized fixes and selected metadata. It does **not** include raw pasted source or journal text. No input upload is implemented. Do not use the diagnostic report as a substitute for verifying the entire system.

**CLI:** scans local files in the current user's process; never opens sockets or executes MQL. Scan only files you are authorized to access. Use a dedicated environment for untrusted repositories.

**Heuristics:** warnings are deliberately conservative in some cases, but are not proof of attack, compile-time correctness, production stability, positive returns or total source safety.

**Size limits:** browser and CLI enforce 2 MB; trade rows are capped; journal parsing is bounded.

**Sensitive data:** source code may contain tokens; the reports suppress candidate secret values. Users must still avoid publishing raw account logs and credentials on GitHub issues.

To report a vulnerability, open a repository issue without including credentials, private code, account numbers or customer data. For sensitive reports, use GitHub private vulnerability reporting if enabled.
