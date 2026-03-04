'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { intakeApi } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { MessageSquare, Send, User, Bot, ArrowRight } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const INTAKE_QUESTIONS = [
  { key: 'policy_number', question: 'What is your policy number?' },
  { key: 'incident_date', question: 'When did the incident occur? (YYYY-MM-DD)' },
  { key: 'incident_location', question: 'Where did the incident occur?' },
  { key: 'claim_type', question: 'What type of claim is this? (e.g., Medical Reimbursement, Auto Collision, Property Damage)' },
  { key: 'amount_estimate', question: 'What is the estimated claim amount in USD?' },
  { key: 'description', question: 'Please describe what happened in detail.' },
]

export default function IntakePage() {
  const router = useRouter()
  const { toast } = useToast()
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Welcome to the FNOL intake. I\'ll help you file your claim. ' + INTAKE_QUESTIONS[0].question },
  ])
  const [currentInput, setCurrentInput] = useState('')
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [isComplete, setIsComplete] = useState(false)

  const submitMutation = useMutation({
    mutationFn: intakeApi.submit,
    onSuccess: (data) => {
      toast({ title: 'Claim created!', description: `Claim ${data.claim_number} is being processed.` })
      router.push(`/claims/${data.claim_id}`)
    },
    onError: () => {
      toast({ title: 'Error', description: 'Failed to submit claim', variant: 'destructive' })
    },
  })

  const handleSend = () => {
    if (!currentInput.trim()) return

    const userMessage: Message = { role: 'user', content: currentInput }
    const newMessages = [...messages, userMessage]
    
    const currentQuestion = INTAKE_QUESTIONS[currentStep]
    const newFormData = { ...formData, [currentQuestion.key]: currentInput }
    setFormData(newFormData)

    if (currentStep < INTAKE_QUESTIONS.length - 1) {
      const nextQuestion = INTAKE_QUESTIONS[currentStep + 1]
      newMessages.push({ role: 'assistant', content: `Got it. ${nextQuestion.question}` })
      setCurrentStep(currentStep + 1)
    } else {
      newMessages.push({ 
        role: 'assistant', 
        content: 'Thank you! I have all the information needed. Please review the details and click "Create Claim & Run Pipeline" to submit.' 
      })
      setIsComplete(true)
    }

    setMessages(newMessages)
    setCurrentInput('')
  }

  const handleSubmit = () => {
    const payload = {
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
      policy_number: formData.policy_number || '',
      incident_date: formData.incident_date || new Date().toISOString().split('T')[0],
      incident_location: formData.incident_location || '',
      claim_type: formData.claim_type || 'General',
      amount_estimate: parseFloat(formData.amount_estimate) || 0,
      description: formData.description || '',
    }
    submitMutation.mutate(payload)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <MessageSquare className="h-8 w-8 text-indigo-400" />
          Conversation Intake
        </h1>
        <p className="text-muted-foreground">File a new claim through guided conversation</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Chat Interface */}
        <Card className="h-[600px] flex flex-col">
          <CardHeader>
            <CardTitle>FNOL Chat</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <div className="flex-1 overflow-auto space-y-4 mb-4">
              {messages.map((message, i) => (
                <div
                  key={i}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                      <Bot className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] p-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary'
                    }`}
                  >
                    {message.content}
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
            </div>
            {!isComplete ? (
              <div className="flex gap-2">
                <Input
                  placeholder="Type your response..."
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                />
                <Button onClick={handleSend}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <Button onClick={handleSubmit} disabled={submitMutation.isPending} className="w-full">
                {submitMutation.isPending ? 'Processing...' : 'Create Claim & Run Pipeline'}
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Live JSON Preview */}
        <Card className="h-[600px]">
          <CardHeader>
            <CardTitle>Extracted Data Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-secondary p-4 rounded-lg h-[500px] overflow-auto text-sm">
              {JSON.stringify(
                {
                  policy_number: formData.policy_number || null,
                  incident_date: formData.incident_date || null,
                  incident_location: formData.incident_location || null,
                  claim_type: formData.claim_type || null,
                  amount_estimate: formData.amount_estimate ? parseFloat(formData.amount_estimate) : null,
                  description: formData.description || null,
                  conversation_length: messages.length,
                  intake_complete: isComplete,
                },
                null,
                2
              )}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
