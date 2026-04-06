'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

interface Trend {
  id: string
  name: string
  description: string
  url: string
  source: string
  category: string
  tropicalization_score: number
  moat_score: number
  recommended_action: string
  metrics: {
    votes?: number
    score?: number
    comments?: number
  }
}

const sampleTrends: Trend[] = [
  {
    id: '1',
    name: 'Cursor AI',
    description: 'IDE com IA integrada para desenvolvimento',
    url: 'https://cursor.sh',
    source: 'product_hunt',
    category: 'developer-tools',
    tropicalization_score: 9.2,
    moat_score: 7.5,
    recommended_action: 'priority',
    metrics: { votes: 4500 }
  },
  {
    id: '2',
    name: 'Perplexity',
    description: 'Motor de busca com IA',
    url: 'https://perplexity.ai',
    source: 'product_hunt',
    category: 'ai-search',
    tropicalization_score: 8.8,
    moat_score: 8.0,
    recommended_action: 'priority',
    metrics: { votes: 3200 }
  },
  {
    id: '3',
    name: 'Midjourney V6',
    description: 'Geração de imagens com IA',
    url: 'https://midjourney.com',
    source: 'hacker_news',
    category: 'ai-art',
    tropicalization_score: 7.5,
    moat_score: 9.0,
    recommended_action: 'medium',
    metrics: { score: 850 }
  },
  {
    id: '4',
    name: 'LangChain',
    description: 'Framework para aplicações com LLMs',
    url: 'https://langchain.com',
    source: 'reddit',
    category: 'developer-tools',
    tropicalization_score: 8.5,
    moat_score: 6.5,
    recommended_action: 'priority',
    metrics: { comments: 420 }
  },
  {
    id: '5',
    name: 'Notion AI',
    description: 'IA integrada ao Notion',
    url: 'https://notion.so',
    source: 'product_hunt',
    category: 'productivity',
    tropicalization_score: 9.5,
    moat_score: 8.5,
    recommended_action: 'priority',
    metrics: { votes: 2800 }
  }
]

export default function Dashboard() {
  const [trends, setTrends] = useState<Trend[]>(sampleTrends)
  const [filter, setFilter] = useState<string>('all')
  const [loading, setLoading] = useState(false)

  const filteredTrends = filter === 'all' 
    ? trends 
    : trends.filter(t => t.source === filter)

  const priorityTrends = trends.filter(t => t.recommended_action === 'priority')
  const mediumTrends = trends.filter(t => t.recommended_action === 'medium')
  const lowTrends = trends.filter(t => t.recommended_action === 'low')

  const getActionColor = (action: string) => {
    switch(action) {
      case 'priority': return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      default: return 'bg-green-500/20 text-green-400 border-green-500/30'
    }
  }

  const getSourceColor = (source: string) => {
    switch(source) {
      case 'product_hunt': return 'bg-purple-500/20 text-purple-400'
      case 'hacker_news': return 'bg-orange-500/20 text-orange-400'
      case 'reddit': return 'bg-red-500/20 text-red-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Header */}
      <header className="border-b border-[#262626] bg-[#0a0a0a]/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-emerald-600 rounded-lg flex items-center justify-center">
                <span className="text-lg">🌴</span>
              </div>
              <h1 className="text-xl font-bold text-white">Trend Arbitrage Scout</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-[#a1a1aa]">Última atualização: {new Date().toLocaleDateString('pt-BR')}</span>
              <button 
                onClick={() => setLoading(true)}
                className="px-4 py-2 bg-[#22c55e] text-black rounded-lg font-medium hover:bg-[#16a34a] transition-colors"
              >
                {loading ? 'Atualizando...' : 'Atualizar'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">Total de Tendências</p>
            <p className="text-3xl font-bold text-white mt-1">{trends.length}</p>
          </div>
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">🔥 Priority</p>
            <p className="text-3xl font-bold text-red-400 mt-1">{priorityTrends.length}</p>
          </div>
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">🟡 Medium</p>
            <p className="text-3xl font-bold text-yellow-400 mt-1">{mediumTrends.length}</p>
          </div>
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">Média Score 🌴</p>
            <p className="text-3xl font-bold text-green-400 mt-1">
              {(trends.reduce((a, b) => a + b.tropicalization_score, 0) / trends.length).toFixed(1)}
            </p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Score de Tropicalização</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={trends.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                <XAxis dataKey="name" stroke="#a1a1aa" fontSize={12} tick={{fill: '#a1a1aa'}} />
                <YAxis stroke="#a1a1aa" fontSize={12} tick={{fill: '#a1a1aa'}} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#171717', border: '1px solid #262626', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="tropicalization_score" fill="#22c55e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Por Fonte</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={[
                { name: 'Product Hunt', count: trends.filter(t => t.source === 'product_hunt').length },
                { name: 'Hacker News', count: trends.filter(t => t.source === 'hacker_news').length },
                { name: 'Reddit', count: trends.filter(t => t.source === 'reddit').length }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                <XAxis dataKey="name" stroke="#a1a1aa" fontSize={12} tick={{fill: '#a1a1aa'}} />
                <YAxis stroke="#a1a1aa" fontSize={12} tick={{fill: '#a1a1aa'}} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#171717', border: '1px solid #262626', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all' ? 'bg-[#22c55e] text-black' : 'bg-[#262626] text-[#a1a1aa] hover:text-white'
            }`}
          >
            Todas
          </button>
          <button
            onClick={() => setFilter('product_hunt')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'product_hunt' ? 'bg-purple-500 text-white' : 'bg-[#262626] text-[#a1a1aa] hover:text-white'
            }`}
          >
            Product Hunt
          </button>
          <button
            onClick={() => setFilter('hacker_news')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'hacker_news' ? 'bg-orange-500 text-white' : 'bg-[#262626] text-[#a1a1aa] hover:text-white'
            }`}
          >
            Hacker News
          </button>
          <button
            onClick={() => setFilter('reddit')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'reddit' ? 'bg-red-500 text-white' : 'bg-[#262626] text-[#a1a1aa] hover:text-white'
            }`}
          >
            Reddit
          </button>
        </div>

        {/* Trends List */}
        <div className="space-y-3">
          {filteredTrends.map((trend, index) => (
            <div 
              key={trend.id}
              className="bg-[#171717] border border-[#262626] rounded-xl p-4 hover:border-[#22c55e]/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[#a1a1aa] text-sm">#{index + 1}</span>
                    <h4 className="text-lg font-semibold text-white truncate">{trend.name}</h4>
                    <span className={`px-2 py-0.5 text-xs rounded-full border ${getSourceColor(trend.source)}`}>
                      {trend.source.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-[#a1a1aa] text-sm mb-2 line-clamp-2">{trend.description}</p>
                  <div className="flex items-center gap-4 text-sm">
                    <a 
                      href={trend.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-[#22c55e] hover:underline"
                    >
                      Ver →
                    </a>
                    <span className="text-[#52525b]">|</span>
                    <span className="text-[#a1a1aa]">{trend.category}</span>
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-2">
                  <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getActionColor(trend.recommended_action)}`}>
                    {trend.recommended_action === 'priority' ? '🔥 Priority' : trend.recommended_action === 'medium' ? '🟡 Medium' : '🟢 Low'}
                  </span>
                  <div className="flex gap-4 text-sm">
                    <div className="text-center">
                      <p className="text-[#a1a1aa] text-xs">🌴 Tropicalização</p>
                      <p className="text-lg font-bold text-green-400">{trend.tropicalization_score}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-[#a1a1aa] text-xs">🛡️ Moat</p>
                      <p className="text-lg font-bold text-purple-400">{trend.moat_score}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#262626] py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-[#a1a1aa] text-sm">
          <p>Trend Arbitrage Scout • Dashboard de Oportunidades EUA → Brasil</p>
        </div>
      </footer>
    </div>
  )
}
