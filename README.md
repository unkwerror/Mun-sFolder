# Personal password vault

Single-user Vaultwarden deployment. Until a domain and HTTPS are configured,
the service binds only to the server loopback interface and must not be exposed
directly to the Internet.

## First local start

1. Copy `.env.example` to `.env` and review every value.
2. Start with `docker compose up -d`.
3. From your computer, create an SSH tunnel:

   ```sh
   ssh -p 2222 -L 8080:127.0.0.1:8080 mun@109.174.15.132
   ```

4. Open `http://localhost:8080`, create the only account, enable 2FA, then set
   `SIGNUPS_ALLOWED=false` and restart with `docker compose up -d`.

## Public access

Do not publish port 8080. Public access will be added only after a domain points
to the server and a reverse proxy can obtain a valid TLS certificate. The proxy
will be configured after checking existing services and occupied ports.

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
