## Purpose / Tujuan

Describe the problem and why this change belongs in the SANRO Hermes toolkit.

## Scope

- [ ] No SANRO internal code, tenant data, credentials or real server paths
- [ ] Existing SANRO / Ario Guswara attribution and Hermes Agent / Nous Research credit retained
- [ ] Optional provider compatibility is labeled accurately (proposed/experimental/tested)
- [ ] No automatic merge or production deploy privileges introduced

## Testing

- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Negative cases for scope/permissions when appropriate
- [ ] Tests are reproducible without billable model/API usage (or separately documented and opt-in)

## Cost and security impact

Describe new services/costs/authentication, resource limits, sandbox assumptions and rollback procedure.

## Evidence

Link task, commit, CI and Draft PR. **Do not call a mock or CLI preview a working autonomous model run.**
