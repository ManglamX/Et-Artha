import type { UserProfile } from '@/lib/types'
import { ARCHETYPE_META } from '@/lib/types'
import { motion } from 'framer-motion'

export function ProfileCard({ profile }: { profile: UserProfile }) {
    const meta = ARCHETYPE_META[profile.archetype] || { icon: '✦', color: '#F4801A', tagline: 'Your ET financial profile' }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            className="bg-navy rounded-2xl p-5 text-white overflow-hidden relative"
        >
            <div className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-10 blur-2xl" style={{ background: meta.color }} />
            <div className="relative">
                <p className="text-xs font-mono tracking-widest text-muted mb-3">YOUR PROFILE</p>
                <div className="flex items-start gap-3 mb-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                        style={{ background: `${meta.color}25`, border: `1px solid ${meta.color}40` }}>
                        {meta.icon}
                    </div>
                    <div>
                        <h2 className="font-serif text-xl leading-tight">{profile.archetype.replace('THE ', '')}</h2>
                        <p className="text-xs text-muted mt-1">{meta.tagline}</p>
                    </div>
                </div>
                <div className="space-y-2">
                    {[
                        { label: 'ROLE', value: profile.profession },
                        { label: 'EXPERIENCE', value: profile.experience },
                        { label: 'GOAL', value: profile.goal },
                    ].map(({ label, value }) => value && (
                        <div key={label} className="flex justify-between items-center">
                            <span className="text-xs font-mono text-muted">{label}</span>
                            <span className="text-xs text-white/80 text-right max-w-[60%]">{value}</span>
                        </div>
                    ))}
                </div>
                {profile.interests?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-white/10">
                        {profile.interests.map(tag => (
                            <span key={tag} className="text-xs px-2 py-0.5 rounded-full font-mono"
                                style={{ background: `${meta.color}25`, color: meta.color }}>{tag}</span>
                        ))}
                    </div>
                )}
            </div>
        </motion.div>
    )
}