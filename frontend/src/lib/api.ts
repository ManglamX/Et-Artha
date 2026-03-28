const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

// ─── MOCK (swap these out when Manglam's backend is live) ───────────────────
let mockMessageCount = 0

export async function createSession(): Promise<string> {
    mockMessageCount = 0
    return "mock-session-123"
}

export async function* streamChat(sessionId: string, message: string) {
    mockMessageCount++
    const mockReply = mockMessageCount < 4
        ? "Thanks for sharing! As a software engineer, I'd love to understand your investing goals. Are you currently investing in SIPs or stocks, or is this fairly new territory for you?"
        : "Perfect — I now have a clear picture of your financial world. Let me put together your personalized ET profile!"

    for (const char of mockReply) {
        yield { token: char, done: false }
        await new Promise(r => setTimeout(r, 18))
    }
    yield { token: '', done: true, profile_ready: mockMessageCount >= 4 }
}

export async function getProfile(sessionId: string) {
    if (mockMessageCount < 4) return { profile: null, recommendations: [] }
    return {
        profile: {
            archetype: "THE WEALTH BUILDER",
            profession: "Software Engineer",
            experience: "beginner" as const,
            goal: "Build long-term wealth through SIPs",
            interests: ["SIP", "mutual funds", "tax saving"]
        },
        recommendations: [
            { product: "ET Wealth", reason: "Best beginner guides on SIPs and goal-based investing", cta: "Plan your finances free", url: "https://economictimes.indiatimes.com/wealth", priority: 1, category: "finance" as const },
            { product: "ET Money", reason: "Direct mutual funds with 0% commission", cta: "Start SIP with ₹500", url: "https://www.etmoney.com", priority: 2, category: "services" as const },
            { product: "ET Prime", reason: "Weekend reads on personal finance strategy", cta: "Start 30-day free trial", url: "https://economictimes.indiatimes.com/prime", priority: 3, category: "content" as const }
        ]
    }
}
// ─── When Manglam's backend is ready, replace everything above with ─────────
// export async function createSession(): Promise<string> {
//   const res = await fetch(`${BACKEND_URL}/api/session/new`, { method: 'POST' })
//   if (!res.ok) throw new Error('Failed to create session')
//   const data = await res.json()
//   return data.session_id
// }
// (see README for full real implementation)