/**
 * Smart GPU Finder with AI Assistant
 * AI-powered GPU search and recommendations
 */

import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Search, MessageSquare, Send, Sparkles, CheckCircle, X, Zap } from 'lucide-react';
import ReservationBooking from './ReservationBooking';

export default function SmartGPUFinder({ gpus, onBook }) {
  const { darkMode, currentTheme, textColor, cardBg, borderColor } = useTheme();
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', text: "👋 Hi! I'm your GPU assistant. Tell me about your project and I'll find the perfect GPU for you!" }
  ]);
  const [userInput, setUserInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGPU, setSelectedGPU] = useState(null);
  const [sortBy, setSortBy] = useState('recommended');

  const handleChatSend = () => {
    if (!userInput.trim()) return;

    const newMessages = [...chatMessages, { role: 'user', text: userInput }];
    let aiResponse = '';
    const input = userInput.toLowerCase();

    if (input.includes('train') && (input.includes('llm') || input.includes('language model'))) {
      aiResponse = "🎯 For LLM training, I recommend GPUs with 24GB+ VRAM like the **RTX 4090** or **A100**. These are perfect for models up to 13B parameters. I'll filter the results to show you the best options!";
      setSearchQuery('4090');
    } else if (input.includes('render') || input.includes('blender') || input.includes('3d')) {
      aiResponse = "🎨 For 3D rendering, the **RTX 4090** gives you the best performance. You'll get fast ray tracing and excellent CUDA support. Check out the options below!";
      setSearchQuery('4090');
    } else if (input.includes('cheap') || input.includes('budget') || input.includes('affordable')) {
      aiResponse = "💰 Looking to save money? I'll show you the most affordable options that still deliver great performance!";
      setSortBy('price-low');
    } else if (input.includes('stable diffusion') || input.includes('image generation')) {
      aiResponse = "🖼️ For Stable Diffusion and image generation, you'll want 24GB VRAM. The **RTX 3090** or **RTX 4090** are perfect! Showing you the best options...";
      setSearchQuery('3090');
    } else {
      aiResponse = "I can help you find the perfect GPU! Tell me more:\n\n• What's your project? (LLM training, 3D rendering, gaming, etc.)\n• What's your budget? ($/hour)\n• Any specific requirements? (VRAM, location, etc.)\n\nOr just browse the options below and I can explain any GPU!";
    }

    newMessages.push({ role: 'assistant', text: aiResponse });
    setChatMessages(newMessages);
    setUserInput('');
  };

  const filteredGPUs = searchQuery
    ? gpus.filter(gpu =>
      gpu.model.toLowerCase().includes(searchQuery.toLowerCase()) ||
      gpu.provider.toLowerCase().includes(searchQuery.toLowerCase())
    )
    : gpus;

  const sortedGPUs = [...filteredGPUs].sort((a, b) => {
    if (sortBy === 'price-low') return parseFloat(a.price_per_hour) - parseFloat(b.price_per_hour);
    if (sortBy === 'price-high') return parseFloat(b.price_per_hour) - parseFloat(a.price_per_hour);
    if (sortBy === 'vram') return b.vram_gb - a.vram_gb;
    return 0;
  });

  return (
    <div className="space-y-6">
      {/* Search & AI Assistant Bar */}
      <div className={`${cardBg} rounded-xl p-4 border ${borderColor}`}>
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search GPU (RTX 4090, 24GB VRAM, etc.)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full pl-12 pr-4 py-3 text-lg border-2 ${darkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200 bg-white'} rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-200 outline-none transition-all ${textColor}`}
            />
          </div>

          <button
            onClick={() => setShowChat(!showChat)}
            className={`px-6 py-3 bg-gradient-to-r ${currentTheme.gradient} text-white font-bold rounded-xl hover:opacity-90 transition-all shadow-lg flex items-center gap-2`}
          >
            <MessageSquare className="w-5 h-5" />
            AI Assistant
            {showChat && <X className="w-4 h-4" />}
          </button>
        </div>

        {/* Sort Options */}
        <div className="mt-4 flex items-center gap-2">
          <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} font-medium`}>Sort by:</span>
          <div className="flex gap-2">
            {[
              { value: 'recommended', label: '⭐ Recommended' },
              { value: 'price-low', label: '💰 Lowest Price' },
              { value: 'vram', label: '🚀 Most VRAM' }
            ].map(option => (
              <button
                key={option.value}
                onClick={() => setSortBy(option.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${sortBy === option.value
                    ? `${currentTheme.primary} text-white`
                    : `${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-700'} hover:bg-opacity-80`
                  }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* GPU List */}
        <div className="col-span-2 space-y-4">
          {sortedGPUs.map((gpu) => (
            <div
              key={gpu.id}
              className={`${cardBg} rounded-xl p-6 border ${borderColor} hover:border-blue-500 transition-all hover:shadow-lg`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className={`text-2xl font-bold ${textColor} mb-2`}>{gpu.model}</h3>
                  <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                    <div>
                      <div className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>VRAM</div>
                      <div className={`font-bold ${textColor}`}>{gpu.vram_gb}GB</div>
                    </div>
                    <div>
                      <div className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Provider</div>
                      <div className={`font-bold ${textColor}`}>{gpu.provider}</div>
                    </div>
                    <div>
                      <div className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Location</div>
                      <div className={`font-bold ${textColor}`}>{gpu.location}</div>
                    </div>
                  </div>

                  <div className={`bg-gradient-to-r ${darkMode ? 'from-purple-900/20 to-blue-900/20 border-purple-700' : 'from-purple-50 to-blue-50 border-purple-200'} rounded-lg p-4 border-2`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-1`}>Price</div>
                        <div className="text-3xl font-bold text-purple-600">
                          ${parseFloat(gpu.price_per_hour).toFixed(2)}<span className="text-lg text-gray-500">/hr</span>
                        </div>
                      </div>
                      <button
                        onClick={() => onBook(gpu)}
                        disabled={!gpu.available}
                        className={`px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        <Zap className="w-5 h-5" />
                        Connect Now
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* AI Chat Assistant */}
        <div className={`sticky top-8 transition-all ${showChat ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
          <div className={`${cardBg} rounded-xl shadow-2xl overflow-hidden border ${borderColor}`} style={{ height: '600px' }}>
            {/* Chat Header */}
            <div className={`bg-gradient-to-r ${currentTheme.gradient} p-4 text-white`}>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div>
                  <div className="font-bold">AI GPU Assistant</div>
                  <div className="text-xs opacity-90">Powered by GP4U Intelligence</div>
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="p-4 overflow-y-auto" style={{ height: 'calc(100% - 140px)' }}>
              {chatMessages.map((msg, i) => (
                <div key={i} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block max-w-[80%] p-3 rounded-xl ${msg.role === 'user'
                      ? `${currentTheme.primary} text-white`
                      : `${darkMode ? 'bg-gray-700' : 'bg-gray-100'} ${textColor}`
                    }`}>
                    <div className="text-sm whitespace-pre-wrap">{msg.text}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <div className={`p-4 border-t ${borderColor}`}>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Describe your project..."
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
                  className={`flex-1 px-4 py-2 border-2 ${darkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200'} rounded-lg focus:border-blue-500 outline-none ${textColor}`}
                />
                <button
                  onClick={handleChatSend}
                  className={`px-4 py-2 ${currentTheme.primary} text-white rounded-lg hover:opacity-90 transition-colors`}
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                {['Train LLM', 'Render 3D', 'Budget option', 'Image AI'].map(suggestion => (
                  <button
                    key={suggestion}
                    onClick={() => {
                      setUserInput(suggestion);
                      setTimeout(() => handleChatSend(), 100);
                    }}
                    className={`text-xs px-3 py-1 ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} ${currentTheme.accent} rounded-full hover:opacity-80`}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
