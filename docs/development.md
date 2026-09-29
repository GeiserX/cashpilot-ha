# Development

[![codecov](https://codecov.io/gh/GeiserX/cashpilot-ha/graph/badge.svg)](https://codecov.io/gh/GeiserX/cashpilot-ha)

The tests live in [`tests/`](../tests) and run in [`tests.yml`](../.github/workflows/tests.yml) on every pull request and push to `main`:

```sh
pip install -r requirements-test.txt
pytest tests/ -v --cov=custom_components --cov-report=xml
```

Coverage is uploaded to Codecov on pushes to `main`.
