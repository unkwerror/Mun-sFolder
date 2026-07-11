# Personal password vault

Single-user Vaultwarden deployment behind an Nginx HTTPS reverse proxy. The
container binds only to the server loopback interface.

## Start

1. Copy `.env.example` to `.env` and review every value.
2. Start with `docker compose up -d`.
3. Open the configured HTTPS domain. Keep `SIGNUPS_ALLOWED=false` after the sole
   account has been created.

## Public access

Do not publish port 8080. Nginx terminates TLS and proxies requests to the
loopback-only Vaultwarden port.

## Source data

The original DOCX contains live credentials and deliberately stays outside this
repository. Import tooling must not log secrets and will be written only after a
backup and the initial vault account are ready.

Generate a local Bitwarden CSV with:

```sh
python3 scripts/docx_to_bitwarden_csv.py ../сервера.docx import/bitwarden.csv
```

The generated file is plaintext, has owner-only permissions, and is ignored by
Git. Delete it immediately after a successful import.
