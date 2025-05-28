# Row Row Row Your Boat

A proxy server that leverages the power of peer pressure to keep you from slacking off.

# Getting Started

## Deploy the Server

To start all required services, run:

```bash
docker compose up -d
```

This will launch:

- A proxy server on port 8080
- A frontend server on port 80
- A backend server on port 8000
- A PostgreSQL database

Once started, visit <http://your-server-address/> to create an account.

## Install mitmproxy Certificate Authority (CA)

You can set up the proxy either at the system level or within your browser. For browser-level configuration, we recommend using an extension like [SwitchyOmega](https://chromewebstore.google.com/detail/proxy-switchyomega/padekgcemlokbadohgkifijomclgjgif?hl=zh-TW).

1. Set the proxy address to: `http://your-server-address:8080`
2. Visit <http://mitm.it/>.
3. Follow the instructions to install mitmproxy's CA certificate
4. You should now be able to browse both HTTP and HTTPS websites through the proxy. If prompted to log in while browsing, use the credentials from the account you created earlier.

# Features

- Block sites
- Modes
  - Direct mode: block sites
  - Scrutinized mode: send email to everyone when you slack
  - Mixed mode: block sites and send email to everyone when you slack
- Send slacking report mail to everyone