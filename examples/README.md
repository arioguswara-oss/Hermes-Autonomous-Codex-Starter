# SANRO Hermes example task

`task.template.json` is a **non-executable template** and **intentionally fails validation** until a current UTC expiration is supplied. Never paste an API key, raw ChatGPT token or SSH credential into a task.

For a runnable sample without time/date guessing:

```bash
python3 -m sanro_hermes.cli init-task > /tmp/sanro-task.json
python3 -m sanro_hermes.cli validate /tmp/sanro-task.json
python3 -m sanro_hermes.cli demo /tmp/sanro-task.json
```

The mock demo deliberately makes no GitHub calls and does not change code. The `owner` field is not proof of identity; a real implementation must independently check GitHub issue authorship using GitHub APIs.
