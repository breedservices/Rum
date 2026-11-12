# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

rum is not released on PyPI yet. Install it from the repository, and always run
the latest `master` revision:

```sh
uv pip install "rum @ git+https://github.com/breedservices/Rum.git"
```

## Reporting a Vulnerability

Please report vulnerabilities privately, through GitHub's private vulnerability
reporting for this repository:

- <https://github.com/breedservices/Rum/security/advisories/new>

Do not open a public issue for a vulnerability. You should get a response within
a few days, and a fix will be released as soon as it is ready.

If the vulnerability exists in upstream Pycord or discord.py as well, report it
to them as well so that other users of those libraries are protected.
