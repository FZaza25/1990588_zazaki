const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
const WS_URL = `${WS_BASE_URL}/ws/telemetry`

export class TelemetrySocket {
    constructor({ onMessage, onStatus, onError } = {}) {
        this.ws = null
        this.onMessage = onMessage
        this.onStatus = onStatus
        this.onError = onError
        this.manualClose = false
        this.reconnectDelay = 1000
        this.reconnectTimer = null
    }

    connect() {
        this.manualClose = false
        this._setStatus('connecting')

        this.ws = new WebSocket(WS_URL)

        this.ws.onopen = () => {
            this.reconnectDelay = 1000
            this._setStatus('open')
        }

        this.ws.onmessage = (event) => {
            let data
            try {
                data = JSON.parse(event.data)
            } catch {
                this.onError?.(new Error(`Invalid WS payload: ${event.data}`))
                return
            }

            try {
                this.onMessage?.(data)
            } catch (err) {
                this.onError?.(err)
            }
        }

        this.ws.onerror = (err) => {
            this.onError?.(err)
        }

        this.ws.onclose = () => {
            this._setStatus('closed')
            if (!this.manualClose) this._scheduleReconnect()
        }
    }

    disconnect() {
        this.manualClose = true
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close(1000, 'client disconnect')
        } else if (this.ws) {
            this.ws.close()
        }
    }

    _scheduleReconnect() {
        this._setStatus(`reconnecting in ${this.reconnectDelay}ms`)
        this.reconnectTimer = setTimeout(() => this.connect(), this.reconnectDelay)
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 15000)
    }

    _setStatus(status) {
        this.onStatus?.(status)
    }
}

export function isTelemetryEvent(event) {
    return typeof event?.sensor_id === 'string' && event.sensor_id.length > 0
}

