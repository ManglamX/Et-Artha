'use client'
import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff } from 'lucide-react'
import { motion } from 'framer-motion'

interface Props {
    onTranscript: (text: string) => void
}

export function VoiceButton({ onTranscript }: Props) {
    const [isListening, setIsListening] = useState(false)
    const [isSupported, setIsSupported] = useState(false)
    const recognitionRef = useRef<any>(null)

    useEffect(() => {
        const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
        setIsSupported(!!SR)
    }, [])

    const startListening = () => {
        const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
        if (!SR) return
        const recognition = new SR()
        recognition.lang = 'en-IN'
        recognition.continuous = false
        recognition.interimResults = false
        recognition.onstart = () => setIsListening(true)
        recognition.onend = () => setIsListening(false)
        recognition.onerror = () => setIsListening(false)
        recognition.onresult = (e: any) => onTranscript(e.results[0][0].transcript)
        recognitionRef.current = recognition
        recognition.start()
    }

    const stopListening = () => {
        recognitionRef.current?.stop()
        setIsListening(false)
    }

    if (!isSupported) return null

    return (
        <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={isListening ? stopListening : startListening}
            className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 text-navy hover:bg-gray-200'
                }`}
            title={isListening ? 'Stop listening' : 'Speak your message'}
        >
            {isListening ? <MicOff size={16} /> : <Mic size={16} />}
        </motion.button>
    )
}