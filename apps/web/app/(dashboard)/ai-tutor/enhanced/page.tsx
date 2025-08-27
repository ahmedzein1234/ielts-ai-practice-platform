'use client'

import EnhancedTutorInterface from '@/components/ai-tutor/enhanced-tutor-interface'
import { useState } from 'react'

export default function EnhancedAITutorPage() {
    const [userId] = useState('demo-user-123')

    const handleMessage = (message: any) => {
        console.log('New message:', message)
    }

    const handleSpeechAnalysis = (analysis: any) => {
        console.log('Speech analysis:', analysis)
    }

    const handlePersonalityChange = (personality: any) => {
        console.log('Personality changed:', personality)
    }

    return (
        <div className="container mx-auto p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold">Enhanced AI Tutor</h1>
                <p className="text-muted-foreground">Multi-modal learning with adaptive intelligence</p>
            </div>

            <div className="h-[800px] border rounded-lg">
                <EnhancedTutorInterface
                    userId={userId}
                    onMessage={handleMessage}
                    onSpeechAnalysis={handleSpeechAnalysis}
                    onPersonalityChange={handlePersonalityChange}
                />
            </div>
        </div>
    )
}
