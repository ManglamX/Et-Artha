'use client'
import { motion } from 'framer-motion'

const stats = [
    { label: 'Users Profiled Today', value: '3,847', change: '+12%' },
    { label: 'ET Prime Conversions', value: '34%', change: 'vs 4% baseline' },
    { label: 'Products Discovered', value: '4.2×', change: 'vs homepage' },
    { label: 'Avg Session Length', value: '3m 12s', change: 'profiling time' },
]

const archetypes = [
    { name: 'Wealth Builder', pct: 32, color: '#059669' },
    { name: 'Market Maverick', pct: 24, color: '#E8001C' },
    { name: 'Corner Office', pct: 18, color: '#6366F1' },
    { name: 'Startup Sherpa', pct: 14, color: '#EC4899' },
    { name: 'Careful Planner', pct: 8, color: '#0891B2' },
    { name: 'Curious Learner', pct: 4, color: '#7C3AED' },
]

export default function Analytics() {
    return (
        <main style={{ minHeight: '100vh', background: '#f5f0eb', fontFamily: 'Georgia, serif' }}>

            {/* ET red top strip */}
            <div style={{ background: '#E8001C', height: '4px', width: '100%' }} />

            {/* Header */}
            <header style={{ background: 'rgba(255,255,255,0.95)', borderBottom: '1px solid #e0e0e0' }}>
                <div style={{ textAlign: 'center', padding: '16px 24px 12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px' }}>
                        <div style={{
                            background: '#E8001C', color: 'white',
                            fontFamily: 'Georgia, serif', fontWeight: 'bold',
                            fontSize: '22px', width: '52px', height: '52px',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            borderRadius: '4px', letterSpacing: '-1px'
                        }}>ET</div>
                        <div style={{ textAlign: 'left' }}>
                            <div style={{
                                fontFamily: 'Georgia, serif', fontSize: '30px',
                                fontWeight: 'bold', color: '#1a1a1a',
                                letterSpacing: '-0.5px', lineHeight: '1'
                            }}>Artha</div>
                            <div style={{
                                fontSize: '11px', color: '#666',
                                letterSpacing: '2px', textTransform: 'uppercase',
                                fontFamily: 'Arial, sans-serif', marginTop: '4px'
                            }}>Impact Dashboard</div>
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
                    background: '#fafafa'
                }}>
                    <span style={{
                        fontSize: '12px', color: '#888',
                        fontFamily: 'Arial, sans-serif',
                        letterSpacing: '1px', textTransform: 'uppercase'
                    }}>Analytics · Live Demo</span>

                    <a href="/" style={{
                        fontSize: '13px', color: '#E8001C',
                        fontFamily: 'Arial, sans-serif',
                        fontWeight: '600', textDecoration: 'none'
                    }}>← Back to Chat</a>
                </div>
            </header>

            {/* Main content */}
            <div style={{
                maxWidth: '1100px', margin: '0 auto',
                padding: '24px 16px', display: 'flex',
                gap: '24px', alignItems: 'flex-start'
            }}>

                {/* LEFT — 4 stat cards stacked */}
                <div style={{ flex: '0 0 300px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {stats.map((s, i) => (
                        <motion.div
                            key={s.label}
                            initial={{ opacity: 0, x: -16 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            style={{
                                background: 'rgba(255,255,255,0.92)',
                                border: '1px solid #e0e0e0',
                                borderRadius: '8px',
                                padding: '20px 24px',
                                borderLeft: '4px solid #E8001C'
                            }}
                        >
                            <p style={{
                                fontSize: '11px', color: '#888',
                                fontFamily: 'Arial, sans-serif',
                                textTransform: 'uppercase', letterSpacing: '1px',
                                marginBottom: '8px'
                            }}>{s.label}</p>
                            <p style={{
                                fontFamily: 'Georgia, serif', fontSize: '36px',
                                color: '#1a1a1a', lineHeight: '1', marginBottom: '6px'
                            }}>{s.value}</p>
                            <p style={{
                                fontSize: '12px', color: '#059669',
                                fontFamily: 'Arial, sans-serif', fontWeight: '600'
                            }}>{s.change}</p>
                        </motion.div>
                    ))}

                    {/* Business impact callout */}
                    <motion.div
                        initial={{ opacity: 0, x: -16 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                        style={{
                            background: '#1a1a1a',
                            border: '1px solid #333',
                            borderRadius: '8px',
                            padding: '16px 20px',
                            borderLeft: '4px solid #E8001C',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '6px',
                        }}
                    >
                        <p style={{
                            fontSize: '10px', color: '#E8001C',
                            fontFamily: 'Arial, sans-serif',
                            textTransform: 'uppercase', letterSpacing: '2px',
                            fontWeight: '700', margin: 0
                        }}>Business Impact</p>
                        <p style={{
                            fontFamily: 'Georgia, serif', fontSize: '13px',
                            color: '#fff', lineHeight: '1.5', margin: 0
                        }}>"A 1% improvement in ET Prime conversion = crores in additional ARR."</p>
                        <p style={{
                            fontSize: '11px', color: '#888',
                            fontFamily: 'Arial, sans-serif', lineHeight: '1.5', margin: 0
                        }}>ET Artha delivers 4.2× product discovery vs the standard homepage.</p>
                    </motion.div>
                </div>

                {/* RIGHT — Archetype distribution */}
                <div style={{ flex: 1 }}>
                    <motion.div
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        style={{
                            background: 'rgba(255,255,255,0.92)',
                            border: '1px solid #e0e0e0',
                            borderRadius: '8px',
                            padding: '28px 32px',
                        }}
                    >
                        {/* Section header */}
                        <div style={{
                            borderBottom: '2px solid #E8001C',
                            paddingBottom: '12px', marginBottom: '28px',
                            display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'
                        }}>
                            <h2 style={{
                                fontFamily: 'Georgia, serif', fontSize: '22px',
                                color: '#1a1a1a', margin: 0
                            }}>User Archetype Distribution</h2>
                            <span style={{
                                fontSize: '11px', color: '#888',
                                fontFamily: 'Arial, sans-serif',
                                textTransform: 'uppercase', letterSpacing: '1px'
                            }}>Last 24 hours</span>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            {archetypes.map((a, i) => (
                                <motion.div
                                    key={a.name}
                                    initial={{ opacity: 0, x: 10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.3 + i * 0.08 }}
                                >
                                    <div style={{
                                        display: 'flex', justifyContent: 'space-between',
                                        marginBottom: '8px', alignItems: 'center'
                                    }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <div style={{
                                                width: '10px', height: '10px',
                                                borderRadius: '50%', background: a.color,
                                                flexShrink: 0
                                            }} />
                                            <span style={{
                                                fontSize: '15px', color: '#1a1a1a',
                                                fontFamily: 'Georgia, serif'
                                            }}>{a.name}</span>
                                        </div>
                                        <span style={{
                                            fontSize: '13px', color: '#888',
                                            fontFamily: 'Arial, sans-serif', fontWeight: '600'
                                        }}>{a.pct}%</span>
                                    </div>
                                    <div style={{
                                        height: '8px', background: '#f0f0f0',
                                        borderRadius: '4px', overflow: 'hidden'
                                    }}>
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${a.pct}%` }}
                                            transition={{ delay: 0.5 + i * 0.08, duration: 0.7, ease: 'easeOut' }}
                                            style={{
                                                height: '100%', borderRadius: '4px',
                                                background: a.color
                                            }}
                                        />
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Demo note */}
                        <div style={{
                            marginTop: '28px', paddingTop: '20px',
                            borderTop: '1px solid #e0e0e0',
                            display: 'flex', alignItems: 'center', gap: '8px'
                        }}>
                            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e' }} />
                            <span style={{
                                fontSize: '12px', color: '#888',
                                fontFamily: 'Arial, sans-serif'
                            }}>Live data · 3,847 users profiled · Profiling completion rate: 89%</span>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Footer */}
            <div style={{
                borderTop: '3px solid #E8001C',
                background: 'rgba(26,26,26,0.95)',
                color: '#999', textAlign: 'center',
                padding: '14px', fontSize: '12px',
                fontFamily: 'Arial, sans-serif', marginTop: '20px'
            }}>
                © The Economic Times · ET Artha is an AI-powered concierge · Hackathon Demo
            </div>

        </main>
    )
}