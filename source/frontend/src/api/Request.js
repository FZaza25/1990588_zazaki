const API_BASE_URL = 'http://localhost:8000'
const DEFAULT_TIMEOUT = 10000

export class ApiError extends Error {
    constructor(message, { status, data, url, method }) {
        super(message)
        this.name = 'ApiError'
        this.status = status
        this.data = data
        this.url = url
        this.method = method
    }
}

function buildUrl(path, query) {
    const url = new URL(path, API_BASE_URL)
    if (query) {
        Object.entries(query).forEach(([k, v]) => {
            if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
        })
    }
    return url.toString()
}

async function parseResponse(res) {
    const contentType = res.headers.get('content-type') || ''
    if (contentType.includes('application/json')) return res.json()
    return res.text()
}

export async function request(path, options = {}) {
    const {
        method = 'GET',
        query,
        body,
        headers = {},
        timeout = DEFAULT_TIMEOUT,
    } = options

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeout)

    try {
        const isFormData = body instanceof FormData
        const res = await fetch(buildUrl(path, query), {
            method,
            signal: controller.signal,
            headers: {
                ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
                ...headers,
            },
            body: body == null ? undefined : (isFormData ? body : JSON.stringify(body)),
        })

        const data = await parseResponse(res)

        if (!res.ok) {
            throw new ApiError(`HTTP ${res.status}`, {
                status: res.status,
                data,
                url: path,
                method,
            })
        }

        return data
    } finally {
        clearTimeout(timer)
    }
}

export const api = {
    get: (path, query, options = {}) => request(path, { ...options, method: 'GET', query }),
    post: (path, body, options = {}) => request(path, { ...options, method: 'POST', body }),
    put: (path, body, options = {}) => request(path, { ...options, method: 'PUT', body }),
    patch: (path, body, options = {}) => request(path, { ...options, method: 'PATCH', body }),
    delete: (path, options = {}) => request(path, { ...options, method: 'DELETE' }),
}
