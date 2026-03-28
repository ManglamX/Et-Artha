'use client'
import { useState, useEffect } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { ProfileCard } from '@/components/ProfileCard'
import { RecommendationPanel } from '@/components/RecommendationPanel'
import { createSession } from '@/lib/api'
import type { Message, UserProfile, Recommendation } from '@/lib/types'
import { motion, AnimatePresence } from 'framer-motion'

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])

  useEffect(() => {
    createSession().then(id => {
      setSessionId(id)
      setMessages([{
        id: '0',
        role: 'assistant',
        content: "Namaste! I'm ET Artha, your personal guide to everything Economic Times has to offer. I'd love to understand your financial world so I can show you exactly what's right for you. To start — what do you do for work?",
        timestamp: new Date()
      }])
    })
  }, [])

  return (
    <main style={{
      minHeight: '100vh',
      fontFamily: 'Georgia, serif',
      backgroundImage: 'url(https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1400)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed',
    }}>

      {/* Newspaper overlay at 60% opacity */}
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        background: 'rgba(245, 240, 232, 0.62)',
        zIndex: 0, pointerEvents: 'none'
      }} />

      {/* All content above overlay */}
      <div style={{ position: 'relative', zIndex: 1 }}>

        {/* ET red top strip */}
        <div style={{ background: '#E8001C', height: '4px', width: '100%' }} />

        {/* Header */}
        <header style={{ background: 'rgba(255,255,255,0.88)', borderBottom: '1px solid #e0e0e0', backdropFilter: 'blur(8px)' }}>
          {/* Centered branding */}
          <div style={{ textAlign: 'center', padding: '16px 24px 12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px' }}>
              <div style={{
                background: '#E8001C',
                color: 'white',
                fontFamily: 'Georgia, serif',
                fontWeight: 'bold',
                fontSize: '22px',
                width: '52px',
                height: '52px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '4px',
                letterSpacing: '-1px'
              }}>ET</div>
              <div style={{ textAlign: 'left' }}>
                <div style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: '30px',
                  fontWeight: 'bold',
                  color: '#1a1a1a',
                  letterSpacing: '-0.5px',
                  lineHeight: 1
                }}>Artha</div>
                <div style={{
                  fontSize: '11px',
                  color: '#666',
                  letterSpacing: '2px',
                  textTransform: 'uppercase',
                  fontFamily: 'Arial, sans-serif',
                  marginTop: '4px'
                }}>Your ET Concierge</div>
              </div>
            </div>
          </div>

          {/* Nav strip */}
          {/* Nav strip */}
          <div style={{
            borderTop: '1px solid #e0e0e0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '8px 40px',
            background: 'rgba(250,250,250,0.9)'
          }}>
            <span style={{
              fontSize: '12px', color: '#888',
              fontFamily: 'Arial, sans-serif',
              letterSpacing: '1px', textTransform: 'uppercase'
            }}>AI-Powered Concierge</span>

            <a href="/analytics" style={{
              fontSize: '13px', color: '#E8001C',
              fontFamily: 'Arial, sans-serif',
              fontWeight: '600', textDecoration: 'none'
            }}>Impact Dashboard →</a>
          </div>
        </header>

        {/* Main content */}
        <div style={{
          maxWidth: '1100px',
          margin: '0 auto',
          padding: '20px 16px',
          display: 'flex',
          gap: '24px',
          alignItems: 'flex-start'
        }}>

          {/* Chat column */}
          <div style={{ flex: '0 0 580px', maxWidth: '580px', margin: profile ? '0' : '0 auto' }}>

            {/* Chat header bar */}
            <div style={{
              background: 'rgba(255,255,255,0.88)',
              backdropFilter: 'blur(8px)',
              border: '1px solid #e0e0e0',
              borderBottom: 'none',
              borderRadius: '8px 8px 0 0',
              padding: '12px 18px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              <div style={{ width: '9px', height: '9px', borderRadius: '50%', background: '#22c55e' }} />
              <span style={{ fontSize: '13px', fontFamily: 'Arial, sans-serif', color: '#333', fontWeight: '600' }}>
                ET Artha is online
              </span>
              <span style={{ fontSize: '12px', color: '#999', fontFamily: 'Arial, sans-serif' }}>
                · Profiles you in ~3 minutes
              </span>
            </div>

            <ChatInterface
              sessionId={sessionId}
              messages={messages}
              setMessages={setMessages}
              isTyping={isTyping}
              setIsTyping={setIsTyping}
              onProfileReady={(p, r) => { setProfile(p); setRecommendations(r) }}
            />
          </div>

          {/* Right panel */}
          <AnimatePresence>
            {profile && (
              <motion.div
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                style={{ flex: '0 0 320px', display: 'flex', flexDirection: 'column', gap: '16px' }}
              >
                <ProfileCard profile={profile} />
                <RecommendationPanel recommendations={recommendations} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div style={{
          borderTop: '3px solid #E8001C',
          background: 'rgba(26,26,26,0.92)',
          color: '#999',
          textAlign: 'center',
          padding: '14px',
          fontSize: '12px',
          fontFamily: 'Arial, sans-serif',
          marginTop: '20px'
        }}>
          © The Economic Times · ET Artha is an AI-powered concierge · Hackathon Demo
        </div>

      </div>
    </main>
  )
}