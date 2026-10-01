# Local Antigravity runtime

The four skills share `antigravity-reviewer/scripts/ask-antigravity.sh`. The
standalone bundle includes that Bash helper and its Python companion; the other
three skill directories contain symlinks to the central helper. Verify each
target with `readlink -f`.

The runtime requires Linux, Bash, Python 3, `agy`, `bwrap`, `ldd`, a D-Bus
daemon, GNOME Keyring/Secret Service, `secret-tool`, and `busctl`. An existing
authenticated session item from Secret Service is required. The controller
passes that single item through an anonymous pipe to a per-run isolated broker;
encrypted storage stays outside the namespace. The broker socket is private to
the run and cleanup removes per-run temporary state.

Boost is the default. Set `ANTIGRAVITY_REVIEW_MODE=standard` to request the
standard route explicitly. There is no automatic fallback. Any other non-empty
mode, or an empty value, exits 2. One invocation makes one consultation; the
consultation may use internal workers, whose count belongs to that one query.
The caller keeps responsibility for its own analysis and decision. Solo
execution remains possible; this does not claim lower latency or delegation for
every query.

The namespace mounts the executable, loader and individual libraries, TLS/DNS
files, synthetic identity files, `/dev`, a private PID `/proc`, disposable `/tmp`,
read-only context/settings, a fresh private `HOME` and the private broker socket.
The root is read-only; session state and `/tmp` are disposable. Restrictive AGY
permissions and the fixed prompt remain additional layers. Networking remains
available for the authenticated service; this is not network isolation.
It does not mount the real
HOME, history, cache, repository, or unrelated user files. The local history is
removed during cleanup; provider-side retention is unspecified.

The timeout is 10 minutes by default. `ANTIGRAVITY_REVIEW_TIMEOUT` accepts only
positive values with `s`, `m`, or `h` units. Errors are summarized rather than
emitting raw stderr diagnostics, while the underlying CLI exit code is
propagated. This document describes local validation and makes no performance
claim.

## Validation on this machine

Validated with AGY 1.2.14 and the installed Linux/Bubblewrap runtime:
Standard and default Boost return nonempty answers; stream diagnostics report
`expanded_commands` with system `boost`. Real internal workers tested an external
synthetic canary with `view_file`, `list_dir`, `grep_search` and `find_by_name`:
all reported missing paths, rather than relying on a permission denial.

Direct namespace probes confirmed real HOME/repository/bus paths absent,
root/context/settings writes blocked, settings replacement blocked, inherited
file descriptors closed, and temporary writes discarded. Timeout and interrupt
checks left no children or temporary directories. State/configuration snapshots
around the isolated functional calls were unchanged.

Run credential-free contract regressions with:

```bash
python3 -B antigravity-reviewer/scripts/tests/test_isolated_review.py
```

Authenticated checks require an unlocked existing Secret Service session:

```bash
antigravity-reviewer/scripts/ask-antigravity.sh "Connectivity: return only REVIEW_OK"
ANTIGRAVITY_REVIEW_MODE=standard antigravity-reviewer/scripts/ask-antigravity.sh "Connectivity: return only REVIEW_OK"
```

The runtime closure and Secret Service item were verified for this machine and
CLI version. Other platforms/versions may fail closed and need investigation;
there is no broad filesystem fallback. The CLI and local utilities remain
trusted, and this design does not restrict network destinations or prevent
SIGKILL/power loss from interrupting cleanup.
