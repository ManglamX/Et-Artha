'use client'
import { useState, useRef, useEffect } from 'react'
import { nanoid } from 'nanoid'
import { streamChat, getProfile } from '@/lib/api'
import { MessageBubble } from './MessageBubble'
import { VoiceButton } from './VoiceButton'
import type { Message, UserProfile, Recommendation } from '@/lib/types'
import { Send } from 'lucide-react'

interface Props {
    sessionId: string | null
    messages: Message[]
    setMessages: (msgs: Message[] | ((prev: Message[]) => Message[])) => void
    isTyping: boolean
    setIsTyping: (v: boolean) => void
    onProfileReady: (profile: UserProfile, recs: Recommendation[]) => void
}

export function ChatInterface({ sessionId, messages, setMessages, isTyping, setIsTyping, onProfileReady }: Props) {
    const [input, setInput] = useState('')
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isTyping])

    const sendMessage = async (text: string) => {
        if (!text.trim() || !sessionId) return

        const userMsg: Message = { id: nanoid(), role: 'user', content: text, timestamp: new Date() }
        setMessages((prev: Message[]) => [...prev, userMsg])
        setInput('')
        setIsTyping(true)

        const assistantId = nanoid()
        let fullResponse = ''

        try {
            for await (const data of streamChat(sessionId, text)) {
                if (data.token) {
                    fullResponse += data.token
                    setMessages((prev: Message[]) => {
                        const existing = prev.find((m: Message) => m.id === assistantId)
                        if (existing) {
                            return prev.map((m: Message) => m.id === assistantId ? { ...m, content: fullResponse } : m)
                        } else {
                            return [...prev, { id: assistantId, role: 'assistant' as const, content: fullResponse, timestamp: new Date() }]
                        }
                    })
                }
                if (data.done) {
                    setIsTyping(false)
                    if (data.profile_ready) {
                        const profileData = await getProfile(sessionId)
                        if (profileData?.profile) {
                            onProfileReady(profileData.profile, profileData.recommendations || [])
                        }
                    }
                }
            }
        } catch (err) {
            setIsTyping(false)
            console.error('Chat error:', err)
        }
    }

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            height: 'calc(100vh - 290px)',
            minHeight: '380px',
            background: 'rgba(255,255,255,0.82)',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(224,224,224,0.8)',
            borderRadius: '0 0 8px 8px',
            overflow: 'hidden'
        }}>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}

                {/* Typing indicator */}
                {isTyping && (
                    <div className="flex items-end gap-2">
                        <div className="w-7 h-7 bg-navy rounded-full flex-shrink-0 flex items-center justify-center text-white text-xs font-serif">अ</div>
                        <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1">
                            <div className="typing-dot w-1.5 h-1.5 bg-muted rounded-full" />
                            <div className="typing-dot w-1.5 h-1.5 bg-muted rounded-full" />
                            <div className="typing-dot w-1.5 h-1.5 bg-muted rounded-full" />
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input bar */}
            <div className="border-t border-gray-100 p-3 flex items-center gap-2">
                <VoiceButton onTranscript={(t) => setInput(t)} />
                <input
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
                    placeholder="Type your message..."
                    className="flex-1 bg-gray-50 rounded-xl px-4 py-2.5 text-sm text-navy placeholder:text-muted outline-none focus:ring-1 focus:ring-red-200"
                />
                <button
                    onClick={() => sendMessage(input)}
                    disabled={!input.trim() || !sessionId}
                    className="w-10 h-10 style={{ background: '#E8001C' }} rounded-xl flex items-center justify-center text-white hover:bg-saffron-dark transition-colors disabled:opacity-40"
                >
                    <Send size={16} />
                </button>
            </div>
        </div>
    )
}