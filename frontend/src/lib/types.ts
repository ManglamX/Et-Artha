export interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
}

export interface UserProfile {
    archetype: string
    profession: string
    experience: 'beginner' | 'intermediate' | 'expert'
    goal: string
    interests: string[]
}

export interface Recommendation {
    product: string
    reason: string
    cta: string
    url: string
    priority: number
    category: 'content' | 'finance' | 'education' | 'events' | 'services'
}

export interface SessionState {
    sessionId: string
    messages: Message[]
    profile: UserProfile | null
    recommendations: Recommendation[]
    isProfileComplete: boolean
    isTyping: boolean
}

export const ARCHETYPE_META: Record<string, { icon: string; color: string; tagline: string }> = {
    'THE MARKET MAVERICK': { icon: '📈', color: '#F4801A', tagline: 'Active trader. Market pulse tracker.' },
    'THE WEALTH BUILDER': { icon: '🌱', color: '#059669', tagline: 'Goal-based. Long-term wealth creator.' },
    'THE CORNER OFFICE': { icon: '🏢', color: '#6366F1', tagline: 'CXO. Policy watcher. Global macro.' },
    'THE STARTUP SHERPA': { icon: '🚀', color: '#EC4899', tagline: 'Founder. Ecosystem tracker.' },
    'THE CAREFUL PLANNER': { icon: '🛡️', color: '#0891B2', tagline: 'Conservative. Security focused.' },
    'THE CURIOUS LEARNER': { icon: '📚', color: '#7C3AED', tagline: 'Knowledge seeker. Building literacy.' },
}