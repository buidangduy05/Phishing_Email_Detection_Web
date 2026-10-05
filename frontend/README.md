# Mailguard frontend

## Run locally

From this directory, install dependencies and start the Vite development server:

```sh
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in a local `.env` file to the backend origin if it is
different from the frontend origin. The default is same-origin.

## Source structure

- `src/pages/` contains the homepage, email export guides, and analyzer page.
- `src/components/` contains shared layout and icon components.
- `src/data/emailGuides.js` holds the mail-provider export instructions.
- `src/api/emailApi.js` sends email files to the backend analysis endpoint.

## Analysis API

The frontend sends `POST /api/analyze` as `multipart/form-data` with the EML
file in the `file` field. The service should return JSON containing a boolean
`isPhishing` and an optional `features` array. Each feature can be a string or
an object with `title`/`name` and optional `description`/`detail` fields.
An optional `summary` string is also displayed. `is_phishing` and `phishing`
are accepted as alternatives to `isPhishing`.

The FastAPI backend lives in `../backend`. See its README for setup, model
artifact requirements, and the `/health` endpoint.
