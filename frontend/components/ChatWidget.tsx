import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, Bot, User } from 'lucide-react';

export function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<{ role: 'user' | 'agent', text: string }[]>([
        { role: 'agent', text: "Hello! I am the **Satark AI Agent**. I have mastered the **Enrolment**, **Biometric**, and **Demographic** datasets.\n\nAsk me about a district status (e.g. 'Status of Lucknow') or check my sync status ('Are you synced?')." }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setInput("");
        setLoading(true);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
            const res = await fetch(`${apiUrl}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMsg })
            });
            const data = await res.json();
            setMessages(prev => [...prev, { role: 'agent', text: data.answer || "Sorry, I couldn't process that." }]);
        } catch (e) {
            setMessages(prev => [...prev, { role: 'agent', text: "⚠️ Error connecting to AI Agent. Is the backend running?" }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end print:hidden">
            {/* Chat Body */}
            {isOpen && (
                <div className="bg-white rounded-lg shadow-2xl border border-slate-200 w-[450px] h-[600px] max-h-[80vh] mb-4 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-10">
                    <div className="bg-indigo-600 p-4 flex justify-between items-center text-white">
                        <div className="flex items-center gap-2">
                            <Bot className="w-5 h-5" />
                            <div>
                                <div className="font-bold text-sm">Satark AI Assistant</div>
                                <div className="text-[10px] text-indigo-200">Local RAG • Python Backend</div>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)}><X className="w-4 h-4" /></button>
                    </div>

                    <div className="flex-1 p-4 overflow-y-auto bg-slate-50 space-y-3 custom-scrollbar" ref={scrollRef}>
                        {messages.map((m, i) => (
                            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[85%] p-3 rounded-lg text-sm ${m.role === 'user'
                                    ? 'bg-indigo-600 text-white rounded-tr-none'
                                    : 'bg-white border border-slate-200 text-slate-700 rounded-tl-none shadow-sm'
                                    }`}>
                                    {/* Handle basic markdown bold/newline */}
                                    <div dangerouslySetInnerHTML={{
                                        __html: m.text
                                            .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
                                            .replace(/> (.*)/g, '<blockquote class="border-l-2 border-indigo-500 pl-2 italic text-slate-600">$1</blockquote>')
                                            .replace(/\n/g, '<br />')
                                    }} />
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-white border border-slate-100 px-3 py-2 rounded-lg rounded-tl-none shadow-sm">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-75"></div>
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-150"></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="p-3 bg-white border-t border-slate-200 flex gap-2">
                        <input
                            className="flex-1 border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            placeholder="Ask query..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSend()}
                        />
                        <button onClick={handleSend} disabled={loading} className="bg-indigo-600 text-white p-2 rounded-md hover:bg-indigo-700 disabled:opacity-50">
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="bg-indigo-600 text-white p-4 rounded-full shadow-lg hover:bg-indigo-700 transition-all hover:scale-105 active:scale-95 group relative"
            >
                {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
                {!isOpen && (
                    <span className="absolute -top-1 -right-1 flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                )}
            </button>
        </div>
    );
}
