Taiga contrib threefold auth
=========================
The Taiga plugin for threefold authentication (Ported from official Gitlab auth).

to install it, you can use one of three ways:
- Using taiga helm chart
- Using Docker and Docker-compose
- Using manual installation

# 1- Taiga Helm Chart Setup

## Installing Taiga chart

-   Adding the repo to your helm 

    ```bash
    helm repo add marketplace https://threefoldtech.github.io/vdc-solutions-charts/
    ```
-   install a chart 

    ```bash
    helm install marketplace/taiga
    ```
    
## installing the chart with different parameters
-   install a chart 
    
    ```bash
    helm install test-helm-charts/taiga --set ingress.host=domain --set threefoldlogin.apiAppSecret=login-api-secret-key --set threefoldlogin.apiAppPublicKey=login-api-public-key --set backendSecretKey=secret --set global.ingress.certresolver=gridca
    ```
-   `backendSecretKey`:
    A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
    
    you can generate one using something like this:
    ```
    TAIGA_SECRET_KEY=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-64};echo;`
    ```
-   `threefoldlogin.apiAppSecret` and `threefoldlogin.apiAppPublicKey `:
    there are default working values in the values.yaml but you should generate new pairs as those should be set to a unique, unpredictable values.
    To get the `threefoldlogin.apiAppSecret` and `threefoldlogin.apiAppPublicKey ` do:

    ```python
    import nacl
    import nacl.signing
    sk = nacl.signing.SigningKey.generate()
    sk_to_b64 = sk.encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the signing key. use it for threefoldlogin.apiAppSecret setting.

    vk = sk.verify_key
    pubkey = vk.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the app public key. you will need it for the front end `threefoldlogin.apiAppPublicKey` setting.
    ```

-   `emailSettings`
    By default, email is configured with the console backend, which means that the emails will be shown in the stdout. If you have an smtp service, make sure to update these values:

     - emailSettings.emailEnabled: true
     - emailSettings.emailFrom: taiga@mycompany.net
     - emailSettings.emailUseTls: "True"
     - emailSettings.emailUseSsl: "False"
     - emailSettings.emailSmtpHost: smtp.gmail.com
     - emailSettings.emailSmtpPort: 587
     - emailSettings.emailSmtpUser: user@gmail.com
     - emailSettings.emailSmtpPassword: your-password

    note : You cannot use both (TLS and SSL) at the same time!

# 2- Docker Setup
Taiga up and running with integrated threefold authentication in a simple two steps, using docker and docker-compose.

Compatible with Taiga 4.2.1, 5.x, 6
## Docker
This plugin is compatible with the official taiga docker images 😃

https://github.com/taigaio/taiga-docker

This project builds 2 images based off the images provided by taiga. This should allow another customizations to continue to work.

The following will show the changes needed to the default docker-compose file to install the threefold plugin.

### Config 
The 2 images:
 - threefolddev/taiga-front-threefold
 - threefolddev/taiga-back-threefold

Use the following environmental settings to configure

```bash
THREEFOLD_API_APP_SECRET : "<APP SECRET>"
THREEFOLD_API_APP_PUBLIC_KEY = "<YOUR-THREEFOLD-APP-PUBLIC-KEY>"
```

To get the `THREEFOLD_API_APP_SECRET` and `THREEFOLD_API_APP_PUBLIC_KEY` do:

```python
import nacl
import nacl.signing
sk = nacl.signing.SigningKey.generate()
sk_to_b64 = sk.encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the signing key. use it for THREEFOLD_API_APP_SECRET setting.

vk = sk.verify_key
pubkey = vk.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the app public key. you will need it for the front end `threeFoldAppPubKey` setting.

``` 

other optionals environmental settings to override when needed

```bash
THREEFOLD_URL : "https://login.threefold.me"  # optional. can be used to override the default url
THREEFOLD_OPENKYC_URL: "https://openkyc.threefold.me/verification/verify-sei"  # optional. can be used to override the default url
THREEFOLD_APP_ID: "<YOUR-HOST-NAME>" # optional as plugin will detect the hostname. can be used to override the default url if needed
```

### Docker building

For Docker building for new release make sure that the following files are coppiced into the docker directory

**Backend:**
Copy https://raw.githubusercontent.com/taigaio/taiga-back/master/docker/config.py

**Frontend:**
copy the config.json and config_env_subst.sh from https://github.com/taigaio/taiga-front/tree/master/docker


# Building

The make file contains the basic blocks to locally build the UI and docker containers. 

```bash
make build
```

you can use `THREEFOLD_TAG` environmental setting to set the tag for the created images before running the below command to build the images. it default to `latest`

you can use `TAIGA_VERSION`environmental setting to set the taiga version, otherwise it will pull the `latest` tag.

for example, to build new `taiga-back-threefold` and `taiga-front-threefold` images with tag `0.0.2` and taiga version set to `6.3.3`

```bash
export THREEFOLD_TAG=0.0.2
export TAIGA_VERSION=6.3.3
make build
```

other commands available, `make publish` will push the images to `threefolddev` Docker Hub with tag `THREEFOLD_TAG` if set, otherwise `latest`

### Docker-compose file (ported from https://github.com/taigaio/taiga-docker)
you can run the Docker-compose file to get Taiga with the plugin enabled up and running.
make sure to set the mandatory env settings `THREEFOLD_API_APP_SECRET`, `THREEFOLD_API_APP_PUBLIC_KEY` in the `docker-compose.yml` file.

- you can create and destroy these environments in just a few commands:

```bash
docker-compose up -d
```

visit `http://127.0.0.1:9000/`
note: on dev setup you will need to replace `https` with `http` in the browser address bar when the browser redirect back to taiga from the threefold auth server after you login successfully

to destroy the environments:

```bash
docker-compose down
```

# 3- Manual Setup
## Production env

Take the latest release of this repository, for instance:

```
export TAIGA_CONTRIB_THREEFOLD_AUTH_TAG=1.1.0
```

### Taiga Back

Load the python virtualenv from your Taiga back directory:

```bash
source .venv/bin/activate
```

And install the package `taiga-contrib-threefold-auth-official` with:

```bash
  (taiga-back) pip install "git+https://github.com/sameh-farouk/taiga-contrib-threefold-auth.git@${TAIGA_CONTRIB_THREEFOLD_AUTH_TAG}#egg=taiga-contrib-threefold-auth-official&subdirectory=back"
```

Modify your `settings/config.py` and include the line:

```python
  INSTALLED_APPS += ["taiga_contrib_threefold_auth"]

  THREEFOLD_API_APP_SECRET = "YOUR-THREEFOLD-APP-SECRET"  # required
  THREEFOLD_URL = "https://login.threefold.me"  # optional. can be used to override the default url
  THREEFOLD_OPENKYC_URL ="https://openkyc.threefold.me/verification/verify-sei"  # optional. can be used to override the default url
```

To get the THREEFOLD_API_APP_SECRET do:

```python
import nacl
import nacl.signing
sk = nacl.signing.SigningKey.generate()
sk_to_b64 = sk.encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the signing key. use it for THREEFOLD_API_APP_SECRET setting.

vk = sk.verify_key
pubkey = vk.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the app public key. you will need it for the front end `threeFoldAppPubKey` setting.
``` 
**Tip** the callback url in the Threefold configuration should be the same as the `{TAIGA_URL}/login` environment variable.


### Taiga Front

Download in your `dist/plugins/` directory of Taiga front the `taiga-contrib-threefold-auth` compiled code (you need subversion in your system):

```bash
  cd dist/
  mkdir -p plugins
  cd plugins
  svn export "https://github.com/sameh-farouk/taiga-contrib-threefold-auth.gi/tags/${TAIGA_CONTRIB_THREEFOLD_AUTH_TAG}/front/dist"  "threefold-auth"
```

Include in your `dist/conf.json` in the 'contribPlugins' list the value `"plugins/threefold-auth/threefold-auth.json"`:

```json
...
  "threeFoldAppPubKey": "YOUR-THREEFOLD-APP-PUBLIC-KEY",  // required 
  "threeFoldAppId": "YOUR-THREEFOLD-APP-ID",  // optional, use your hostname ex. circles.threefold.me 
  "threeFoldUrl": "https://login.threefold.me", // optional, can be used to override the default url
  "contribPlugins": [
    (...)
    "plugins/threefold-auth/threefold-auth.json"
  ]
...
```

## Dev env

This configuration should be used only if you're developing this library.

### Taiga Back

Clone the repo and

```bash
  cd taiga-contrib-threefold-auth/back
  workon taiga
  pip install -e .
```

Modify `taiga-back/settings/local.py` and include the line:

```python
  INSTALLED_APPS += ["taiga_contrib_threefold_auth"]

  THREEFOLD_API_APP_SECRET = "YOUR-THREEFOLD-APP-SECRET"  # required
  THREEFOLD_URL = "https://login.threefold.me"  # optional. can be used to override the default url
  THREEFOLD_OPENKYC_URL ="https://openkyc.threefold.me/verification/verify-sei"  # optional. can be used to override the default url
```

To get the THREEFOLD_API_APP_SECRET do:

```python
import nacl
import nacl.signing
sk = nacl.signing.SigningKey.generate()
sk_to_b64 = sk.encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the signing key. use it for THREEFOLD_API_APP_SECRET setting.

vk = sk.verify_key
pubkey = vk.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()  # this is the app public key. you will need it for the front end `threeFoldAppPubKey` setting.

``` 

### Taiga Front

After clone the repo link `dist` in `taiga-front` plugins directory:

```bash
  cd taiga-front/dist
  mkdir -p plugins
  cd plugins
  ln -s ../../../taiga-contrib-threefold-auth/front/dist threefold-auth
```

Include in your `dist/conf.json` in the 'contribPlugins' list the value `"plugins/threefold-auth/threefold-auth.json"`:

```json
...
  "threeFoldAppPubKey": "YOUR-THREEFOLD-APP-PUBLIC-KEY",  // required 
  "threeFoldAppId": "YOUR-THREEFOLD-APP-ID",  // optional, use your hostname ex. circles.threefold.me 
  "threeFoldUrl": "https://login.threefold.me", // optional, can be used to override the default url
  "contribPlugins": [
    (...)
    "plugins/threefold-auth/threefold-auth.json"
  ]
...
```

In the plugin source dir `taiga-contrib-threefold-auth/front` run

```bash
npm install
```
and use:

- `gulp` to regenerate the source and watch for changes.
- `gulp build` to only regenerate the source.

## Running tests

not yet

## disable the normal login and registeration:
If you like to keep only Threefold login and registration and disable the default login and the public registration, include in your `dist/conf.json` these values

```json
  "defaultLoginEnabled": false,
  "publicRegisterEnabled": false,
```

## Taiga Documentation

Currently, we have authored three main documentation hubs:

- **[API](https://docs.taiga.io/api.html)**: Our API documentation and reference for developing from Taiga API.
- **[Documentation](https://docs.taiga.io/)**: If you need to install Taiga on your own server, this is the place to find some guides.
- **[Taiga Resources](https://resources.taiga.io)**: This page is intended to be the support reference page for the users.

## Contributions
My thanks to all the people who have added to the plugin
The whole taiga team who wrote the github plugin that this plugin is based off.
