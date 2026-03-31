const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

// ─── Real backend implementation ─────────────────────────────────────────────

export async function createSession(): Promise<string> {
    const res = await fetch(`${BACKEND_URL}/api/session/new`, { method: 'POST' })
    if (!res.ok) throw new Error('Failed to create session')
    const data = await res.json()
    return data.session_id
}

export async function* streamChat(sessionId: string, message: string) {
    const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message }),
    })

    if (!res.ok) throw new Error(`Chat request failed: ${res.status}`)
    if (!res.body) throw new Error('No response body')

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''   // keep incomplete last line in buffer

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6))
                    yield data
                } catch {
                    // skip malformed SSE lines
                }
            }
        }
    }

    // flush remaining buffer
    if (buffer.startsWith('data: ')) {
        try {
            const data = JSON.parse(buffer.slice(6))
            yield data
        } catch {
            // ignore
        }
    }
}

export async function getProfile(sessionId: string) {
    const res = await fetch(`${BACKEND_URL}/api/profile/${sessionId}`)
    if (!res.ok) return { profile: null, recommendations: [] }
    return res.json()
}