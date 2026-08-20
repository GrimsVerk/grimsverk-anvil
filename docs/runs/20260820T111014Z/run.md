# Delivery run 20260820T111014Z

Started 2026-08-20T11:10:14Z.
Base branch: run/local (branch suffix '--run-local').

- 11:10:16Z budget: weekly at 10% (model 9%), allowance 20 points, window resets Aug 27, 11am (Europe/Amsterdam)
- 11:10:18Z budget: weekly at 10% (model 9%), spent 0 of 20 points on the per-model weekly limit
- 11:10:19Z iteration 1: phase ORACLE
- 11:10:19Z dispatch oracle worker (oracle-20260820111019)

Landed post-mortem 2026-08-20T11:13:28Z by --land-evidence:
the run stopped without its exit landing firing, so its stop and
its exit code were never recorded. The last lines above are the
closest thing to a cause of death this report can offer.
