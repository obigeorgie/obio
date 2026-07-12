import { useState } from 'react';
import { api } from '../api';
import { MessageCircle, BookOpen, HelpCircle, Lightbulb, Send, Loader2, GraduationCap } from 'lucide-react';

interface ChatMessage {
  role: 'user' | 'tutor';
  content: string;
  type?: 'explain' | 'practice' | 'ask' | 'hint';
}

export default function Tutor() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'tutor', content: 'Hi! I\'m your AI tutor. Ask me anything about your learning topics, or I can explain concepts, generate practice problems, or give you hints!' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'ask' | 'explain' | 'practice'>('ask');
  const [topicId, setTopicId] = useState('');
  const [age, setAge] = useState(8);
  const [error, setError] = useState('');

  const sendMessage = async () => {
    if (!input.trim() && mode === 'ask') return;
    setLoading(true);
    setError('');

    const userMsg: ChatMessage = { role: 'user', content: input, type: mode };
    setMessages(prev => [...prev, userMsg]);

    try {
      let response = '';
      
      if (mode === 'ask') {
        const res = await api.tutorAsk({ question: input, age, topic_id: topicId || undefined });
        response = res.answer;
      } else if (mode === 'explain' && topicId) {
        const res = await api.tutorExplain({ topic_id: topicId, age });
        response = res.explanation;
      } else if (mode === 'practice' && topicId) {
        const res = await api.tutorPractice({ topic_id: topicId, age, difficulty: 'medium', count: 3 });
        response = res.problems;
      } else {
        response = 'Please select a topic first.';
      }

      setMessages(prev => [...prev, { role: 'tutor', content: response, type: mode }]);
    } catch (err: any) {
      if (err.message?.includes('503') || err.message?.includes('not configured')) {
        setError('AI tutor is not yet configured. Contact admin to enable this feature.');
      } else {
        setError(err.message || 'Failed to get response');
      }
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  const quickActions = [
    { label: 'Explain a topic', icon: <BookOpen className="w-4 h-4" />, mode: 'explain' as const },
    { label: 'Practice problems', icon: <GraduationCap className="w-4 h-4" />, mode: 'practice' as const },
    { label: 'Ask a question', icon: <HelpCircle className="w-4 h-4" />, mode: 'ask' as const },
  ];

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      <div className="border-b bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-bold">AI Tutor</h1>
          </div>
          <div className="flex items-center gap-2">
            {quickActions.map(action => (
              <button
                key={action.mode}
                onClick={() => setMode(action.mode)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mode === action.mode
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {action.icon}
                {action.label}
              </button>
            ))}
          </div>
        </div>

        {(mode === 'explain' || mode === 'practice') && (
          <div className="mt-4 flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Topic ID</label>
              <input
                type="text"
                value={topicId}
                onChange={(e) => setTopicId(e.target.value)}
                placeholder="e.g., math-counting-1"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="w-32">
              <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                min={4}
                max={11}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-auto px-6 py-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border shadow-sm'
              }`}
            >
              {msg.type === 'explain' && msg.role === 'tutor' && (
                <div className="flex items-center gap-2 mb-2 text-sm text-blue-600 font-medium">
                  <BookOpen className="w-4 h-4" />
                  Explanation
                </div>
              )}
              {msg.type === 'practice' && msg.role === 'tutor' && (
                <div className="flex items-center gap-2 mb-2 text-sm text-green-600 font-medium">
                  <GraduationCap className="w-4 h-4" />
                  Practice Problems
                </div>
              )}
              <div className="whitespace-pre-wrap">{msg.content}</div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm rounded-2xl px-4 py-3 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <span className="text-sm text-gray-500">AI tutor is thinking...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center gap-3">
            <Lightbulb className="w-5 h-5 text-yellow-600" />
            <p className="text-yellow-800">{error}</p>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t bg-white px-6 py-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
            placeholder={
              mode === 'ask' ? 'Ask me anything...' :
              mode === 'explain' ? 'Press send to get explanation for this topic' :
              'Press send to generate practice problems'
            }
            className="flex-1 px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || (!input.trim() && mode === 'ask')}
            className="px-4 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
