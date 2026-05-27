# Grid Auth Taiga

This repository contains an authentication plugin for the [Taiga](https://taiga.io) project management platform that enables single sign-on through a blockchain-based identity system. It is ported from the official GitLab auth plugin and adapted for decentralized authentication flows.

## What this is

The plugin allows users to authenticate to Taiga using a decentralized identity instead of separate Taiga credentials. It consists of a Python backend module (Django/Taiga back) and a JavaScript frontend module (Taiga front) that together handle the OAuth-like authentication flow, identity verification, and user provisioning inside Taiga.

## What this repository contains

- **Backend plugin** (`back/`) — Python package integrating with Taiga's Django backend to handle authentication callbacks, token verification, and user creation
- **Frontend plugin** (`front/`) — JavaScript module adding the SSO login button and handling the frontend authentication flow
- **Docker images** — `threefolddev/taiga-front-threefold` and `threefolddev/taiga-back-threefold` images for easy deployment
- **Helm chart integration** — Configuration for installing Taiga with the plugin via Helm
- **Manual installation instructions** for production and development environments

## Role in the stack

This plugin bridges the Taiga project management application with the decentralized identity layer. It enables teams within the ecosystem to use a single identity for both infrastructure access and project collaboration. It fits into the broader management and collaboration layer of the stack.

## Relation to ThreeFold

This technology is used within the ThreeFold ecosystem and was first deployed on the ThreeFold Grid. The component itself is designed as reusable infrastructure technology and should be understood by its technical function first, independent of any specific deployment.

## Ownership

This repository is owned and maintained by TF-Tech NV, a Belgian company responsible for the development and maintenance of this technology.

## Installation

You can install the plugin using one of three methods:

- Using the Taiga Helm chart
- Using Docker and Docker Compose
- Manual installation

### 1. Taiga Helm Chart Setup

Add the repo to your Helm:

```bash
helm repo add marketplace https://threefoldtech.github.io/vdc-solutions-charts/
helm install marketplace/taiga
```

Install with custom parameters:

```bash
helm install test-helm-charts/taiga \
  --set ingress.host=domain \
  --set threefoldlogin.apiAppSecret=login-api-secret-key \
  --set threefoldlogin.apiAppPublicKey=login-api-public-key \
  --set backendSecretKey=secret \
  --set global.ingress.certresolver=gridca
```

- `backendSecretKey`: A secret key for Django cryptographic signing. Generate one with:
  ```
  TAIGA_SECRET_KEY=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-64};echo;`
  ```
- `threefoldlogin.apiAppSecret` and `threefoldlogin.apiAppPublicKey`: Generate a new key pair:
  ```python
  import nacl
  import nacl.signing
  sk = nacl.signing.SigningKey.generate()
  sk_to_b64 = sk.encode(encoder=nacl.encoding.Base64Encoder).decode()
  vk = sk.verify_key
  pubkey = vk.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()
  ```
- `emailSettings`: Configure SMTP if needed (see original docs for full settings).

### 2. Docker Setup

Compatible with Taiga 4.2.1, 5.x, 6.

Use the following environment settings:

```bash
THREEFOLD_API_APP_SECRET="<APP SECRET>"
THREEFOLD_API_APP_PUBLIC_KEY="<YOUR-APP-PUBLIC-KEY>"
```

Generate the secret and public key as shown above.

Optional overrides:

```bash
THREEFOLD_URL="https://login.threefold.me"
THREEFOLD_OPENKYC_URL="https://openkyc.threefold.me/verification/verify-sei"
THREEFOLD_APP_ID="<YOUR-HOST-NAME>"
```

Build and run:

```bash
make build
docker-compose up -d
```

Visit `http://127.0.0.1:9000/`.

To destroy:

```bash
docker-compose down
```

### 3. Manual Setup

#### Taiga Back

Install the package:

```bash
pip install "git+https://github.com/sameh-farouk/taiga-contrib-threefold-auth.git@${TAIGA_CONTRIB_THREEFOLD_AUTH_TAG}#egg=taiga-contrib-threefold-auth-official&subdirectory=back"
```

Modify `settings/config.py`:

```python
INSTALLED_APPS += ["taiga_contrib_threefold_auth"]
THREEFOLD_API_APP_SECRET = "YOUR-APP-SECRET"
THREEFOLD_URL = "https://login.threefold.me"
THREEFOLD_OPENKYC_URL = "https://openkyc.threefold.me/verification/verify-sei"
```

#### Taiga Front

Download the compiled plugin into `dist/plugins/`:

```bash
cd dist/
mkdir -p plugins
cd plugins
svn export "https://github.com/sameh-farouk/taiga-contrib-threefold-auth.git/tags/${TAIGA_CONTRIB_THREEFOLD_AUTH_TAG}/front/dist" "threefold-auth"
```

Add to `dist/conf.json`:

```json
{
  "threeFoldAppPubKey": "YOUR-APP-PUBLIC-KEY",
  "threeFoldAppId": "YOUR-APP-ID",
  "threeFoldUrl": "https://login.threefold.me",
  "contribPlugins": [
    "plugins/threefold-auth/threefold-auth.json"
  ]
}
```

## Development Setup

### Taiga Back

```bash
cd taiga-contrib-threefold-auth/back
workon taiga
pip install -e .
```

Update `taiga-back/settings/local.py` with the same settings as production.

### Taiga Front

```bash
cd taiga-front/dist
mkdir -p plugins
cd plugins
ln -s ../../../taiga-contrib-threefold-auth/front/dist threefold-auth
```

Add the plugin to `dist/conf.json` as shown above, then in the plugin source directory:

```bash
npm install
gulp       # regenerate and watch
gulp build # regenerate only
```

## Disable default login and registration

To keep only the SSO login and disable the default login and public registration, add to `dist/conf.json`:

```json
{
  "defaultLoginEnabled": false,
  "publicRegisterEnabled": false
}
```

## Taiga Documentation

- **[API](https://docs.taiga.io/api.html)**: API documentation and reference.
- **[Documentation](https://docs.taiga.io/)**: Installation and configuration guides.
- **[Taiga Resources](https://resources.taiga.io)**: Support reference for users.

## Contributions

Thanks to all contributors and the Taiga team, whose GitLab plugin served as the foundation for this work.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
Copyright (c) TFTech NV.
