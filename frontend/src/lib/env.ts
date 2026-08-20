const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL

if (typeof configuredBaseUrl !== 'string' || configuredBaseUrl.trim().length === 0) {
  throw new Error('VITE_API_BASE_URL must be set in frontend/.env')
}

// Same-origin container builds set VITE_API_BASE_URL=/ so fetches stay relative.
export const apiBaseUrl =
  configuredBaseUrl === '/' ? '' : configuredBaseUrl.replace(/\/$/, '')

export const env = {
  apiBaseUrl,
}
