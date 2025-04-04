const http = require('http');
const https = require('https');
const httpProxy = require('http-proxy');
const kerberos = require('kerberos');
const { URL } = require('url');

const TARGET_PROXY = 'http://your-corp-proxy.example.com:8080';
const PROXY_HOSTNAME = new URL(TARGET_PROXY).hostname;

async function getKerberosToken() {
  return new Promise((resolve, reject) => {
    kerberos.initializeClient(`HTTP@${PROXY_HOSTNAME}`, {}, (err, client) => {
      if (err) return reject(err);

      client.step('', (err, token) => {
        if (err) return reject(err);
        resolve(`Negotiate ${token}`);
      });
    });
  });
}

async function startProxy() {
  const proxy = httpProxy.createProxyServer({});
  const kerberosToken = await getKerberosToken();

  const server = http.createServer((req, res) => {
    const target = req.url.startsWith('https') ? 'https:' : 'http:';

    req.headers['proxy-authorization'] = kerberosToken;

    proxy.web(req, res, {
      target: req.url,
      agent: new (target === 'https:' ? https.Agent : http.Agent)({ keepAlive: true }),
      secure: false,
      headers: {
        'Proxy-Authorization': kerberosToken,
      },
      prependPath: false,
      changeOrigin: true,
      toProxy: true,
    });
  });

  const PORT = 3129;
  server.listen(PORT, () => {
    console.log(`Local Kerberos proxy running at http://localhost:${PORT}`);
  });
}

startProxy().catch((err) => {
  console.error('Failed to start Kerberos proxy:', err);
});

