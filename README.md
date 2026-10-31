*This project has been created as part of the 42 curriculum by mkneisl, pharbst, and rnauke.*

# ft_transcendence

## Description

**ft_transcendence** is a fully containerized web platform for playing the classic game
**Pong**, built as the final project of the 42 curriculum. It is a single-page application
served by a Django backend: all navigation and interactions happen without full page
reloads, driven by JavaScript modules and WebSockets.

The goal of the project was to build a complete, production-style web application from
scratch, covering every layer of the stack — from the game engine and real-time
networking to authentication, security and DevOps.

Main features:

- **Pong** — playable in local multiplayer, against remote opponents over WebSockets,
  with an automated **matchmaking** queue and **tournaments** (including mid-round
  rankings and lobby views).
- **User management** — remote authentication with **JWT** (SimpleJWT), optional
  **two-factor authentication** (TOTP via pyotp), and sign-in through the **42 intra
  OAuth API**.
- **Social features** — friends list, profiles, avatars and match history.
- **Blockchain integration** — game results are stored on an Ethereum test chain via a
  Solidity smart contract (see `srcs/backend/django-app/web3db/smartContract.sol`),
  deployed and queried with web3.py.
- **Security** — the site is only served over **TLS** through an nginx reverse proxy
  (no plain HTTP), with strong passwords required, hashed credentials, and
  parameterized SQL queries via the Django ORM.

Technical stack:

| Layer      | Technology                                                    |
| ---------- | ------------------------------------------------------------- |
| Backend    | Python · Django 5 · Django REST Framework · Channels/Daphne   |
| Realtime   | WebSockets (Django Channels + Redis channel layer)            |
| Database   | PostgreSQL                                                    |
| Frontend   | Vanilla JavaScript ES modules · Bootstrap 5                  |
| Blockchain | Solidity · web3.py                                            |
| Serving    | nginx (TLS termination, static files)                         |
| DevOps     | Docker · Docker Compose                                       |

## Instructions

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- `openssl` (to generate the self-signed TLS certificate)

### Setup

1. **Environment variables** — create a `.env` file at the repository root:

   ```env
   POSTGRES_USER=your_postgres_user
   POSTGRES_DB=your_database_name
   POSTGRES_PASSWORD=your_postgres_password
   OAUTH_ID=your_42_api_uid
   OAUTH_SECRET=your_42_api_secret
   ETH_PK=your_ethereum_test_account_private_key
   PROJ_MODE=prod
   ```

   - `OAUTH_ID` / `OAUTH_SECRET` come from creating an application on the
     [42 intra](https://profile.intra.42.fr/) (the redirect URI must point to your
     deployment). OAuth login is disabled if they are not set.
   - `ETH_PK` is the private key of the Ethereum test-chain account used to deploy
     the smart contract and persist game scores.
   - `PROJ_MODE` selects how the backend runs inside its container
     (`prod` = daphne/ASGI, anything else = Django dev server).

2. **TLS certificate** — generate a self-signed certificate for nginx:

   ```sh
   make selfsigned-cert
   ```

### Running

Build and start all services (postgres, backend, nginx, redis):

```sh
make up        # build and start in the background
# or
make log       # build and start with logs attached
```

The backend automatically runs migrations and `collectstatic` on startup
(see `srcs/backend/init.sh`).

Once everything is up, open:

> **https://localhost:8001**

(you will need to accept the browser warning caused by the self-signed certificate —
the site is intentionally not served over plain HTTP).

### Useful commands

| Command               | Effect                                              |
| --------------------- | --------------------------------------------------- |
| `make up`             | Build and start all containers (detached)           |
| `make log`            | Start with logs attached                           |
| `make down`           | Stop and remove all containers                      |
| `make migrate`        | Run Django migrations inside the backend container |
| `make collectstatic`  | Re-collect static files                            |
| `make cleandb`        | Delete the local PostgreSQL data volume            |

### Project layout

```
srcs/
├── backend/
│   ├── Dockerfile          # Backend image (Python 3.12)
│   ├── init.sh             # Startup script (migrate, collectstatic, serve)
│   └── django-app/         # Django project
│       ├── backend/        # Settings, ASGI, root URLs
│       ├── api/            # REST API: auth (JWT, 2FA, OAuth), users, friends, matches
│       ├── webclient/      # SPA templates, views and frontend assets
│       ├── tpong/          # Pong game engine and realtime game networking
│       ├── web3db/         # Smart contract + blockchain integration
│       └── static/         # Collected static files (generated)
├── nginx/                  # Reverse-proxy config and TLS certificates
└── pgdata/                 # PostgreSQL data (generated)
```

## Resources

### References used during development

- [Django documentation](https://docs.djangoproject.com/en/5.0/) — ORM, settings,
  static files, deployment checklist.
- [Django REST Framework](https://www.django-rest-framework.org/) — REST API design.
- [Django REST Framework SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) —
  JWT authentication and token refresh.
- [Django Channels](https://channels.readthedocs.io/) — WebSocket consumers, channel
  layers, and serving ASGI applications with [Daphne](https://github.com/django/daphne).
- [Docker & Docker Compose documentation](https://docs.docker.com/) — containerization
  of the full stack.
- [nginx documentation](https://nginx.org/en/docs/) — reverse proxying and TLS.
- [web3.py documentation](https://web3py.readthedocs.io/) and
  [Solidity docs](https://docs.soliditylang.org/) — smart contract development and
  deployment.
- [pyotp](https://github.com/pyotp/pyotp) — TOTP-based two-factor authentication.
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/getting-started/introduction/) —
  frontend styling and components.
- [42 intra API documentation](https://api.intra.42.fr/apidoc) — OAuth sign-in.
- [Django deployment checklist (howto/deployment/checklist)](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
  — security hardening.

### AI usage

This Project was finished before AI coding was good enough to replace humans, AI was mereley used for generating some text for the website
