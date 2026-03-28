import type { Recommendation } from '@/lib/types'
import { motion } from 'framer-motion'
import { ExternalLink } from 'lucide-react'

const CATEGORY_COLORS: Record<string, string> = {
    content: '#F4801A', finance: '#059669', education: '#6366F1', events: '#EC4899', services: '#0891B2',
}

export function RecommendationPanel({ recommendations }: { recommendations: Recommendation[] }) {
    if (!recommendations.length) return null
    return (
        <div className="space-y-3">
            <p className="text-xs font-mono tracking-widest text-muted px-1">RECOMMENDED FOR YOU</p>
            {recommendations.map((rec, i) => (
                <motion.a
                    key={rec.product}
                    href={rec.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="block bg-white border border-gray-100 rounded-xl p-4 hover:border-saffron/40 hover:shadow-sm transition-all group"
                >
                    <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full flex-shrink-0 mt-0.5"
                                style={{ background: CATEGORY_COLORS[rec.category] || '#F4801A' }} />
                            <h3 className="font-sans font-medium text-sm text-navy">{rec.product}</h3>
                        </div>
                        <ExternalLink size={12} className="text-muted group-hover:text-saffron transition-colors flex-shrink-0 mt-0.5" />
                    </div>
                    <p className="text-xs text-muted leading-relaxed mb-3">{rec.reason}</p>
                    <span className="text-xs font-medium px-3 py-1 rounded-full inline-block"
                        style={{ background: `${CATEGORY_COLORS[rec.category] || '#F4801A'}15`, color: CATEGORY_COLORS[rec.category] || '#F4801A' }}>
                        {rec.cta} →
                    </span>
                </motion.a>
            ))}
        </div>
    )
}