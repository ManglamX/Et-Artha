'use client'
import { motion } from 'framer-motion'
import clsx from 'clsx'
import type { Message } from '@/lib/types'

export function MessageBubble({ message }: { message: Message }) {
    const isUser = message.role === 'user'
    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx('flex items-end gap-2', isUser && 'flex-row-reverse')}
        >
            {!isUser && (
                <div className="w-7 h-7 bg-navy rounded-full flex-shrink-0 flex items-center justify-center text-white text-xs font-serif">अ</div>
            )}
            <div className={clsx(
                'max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed',
                isUser
                    ? 'bg-navy text-white rounded-br-sm'
                    : 'bg-gray-50 border border-gray-100 text-navy rounded-bl-sm'
            )}>
                {message.content}
            </div>
        </motion.div>
    )
}