'use client'

import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Trend {
  source: string
  source_id: string
  name: string
  description: string
  url: string
  category: string
  metrics: { score?: number; comments?: number }
  moat_score: number
  tropicalization_score: number
  recommended_action: string
  brief_analysis: string
}

export default function Dashboard() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [filter, setFilter] = useState<string>('all')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/data/analyzed_trends.json')
      .then(res => res.json())
      .then(data => {
        setTrends(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Erro:', err)
        setLoading(false)
      })
  }, [])

  const filteredTrends = filter === 'all' ? trends : trends.filter(t => t.source === filter)
  const priorityTrends = trends.filter(t => t.recommended_action === 'priority')
  const mediumTrends = trends.filter(t => t.recommended_action === 'medium')
  const avgScore = trends.length > 0 ? (trends.reduce((a, b) => a + b.tropicalization_score, 0) / trends.length).toFixed(1) : '0'

  const getActionColor = (action: string) => {
    switch(action) {
      case 'priority': return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      default: return 'bg-green-500/20 text-green-400 border-green-500/30'
    }
  }

  const getSourceColor = (source: string) => {
    switch(source) {
      case 'hackernews': return 'bg-orange-500/20 text-orange-400'
      case 'reddit': return 'bg-red-500/20 text-red-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <header className="border-b border-[#262626] bg-[#0a0a0a]/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-emerald-600 rounded-lg flex items-center justify-center">
                <span className="text-lg">T</span>
              </div>
              <h1 className="text-xl font-bold text-white">Trend Arbitrage Scout</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-[#a1a1aa]">Ultima atualizacao: {new Date().toLocaleDateString('pt-BR')}</span>
              <button onClick={() => setLoading(true)} className="px-4 py-2 bg-[#22c55e] text-black rounded-lg font-medium hover:bg-[#16a34a]">
                {loading ? 'Atualizando...' : 'Atualizar'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">Total de Tendencias</p>
            <p className="text-3xl font-bold text-white mt-1">{trends.length}</p>
          </div>
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">Priority</p>
            <p className="text-3xl font-bold text-red-400 mt-1">{priorityTrends.length}</p>
          </div>
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">Medium</p>
            <p className="text-3xl font-bold text-yellow-400 mt-1">{mediumTrends.length}</p>
          </div>
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <p className="text-[#a1a1aa] text-sm">Media Score</p>
            <p className="text-3xl font-bold text-green-400 mt-1">{avgScore}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Score de Tropicalizacao</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={trends.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                <XAxis dataKey="name" stroke="#a1a1aa" fontSize={12} />
                <YAxis stroke="#a1a1aa" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#171717', border: '1px solid #262626' }} />
                <Bar dataKey="tropicalization_score" fill="#22c55e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-[#171717] border border-[#262626] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Por Fonte</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={[
                { name: 'Hacker News', count: trends.filter(t => t.source === 'hackernews').length },
                { name: 'Reddit', count: trends.filter(t => t.source === 'reddit').length }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                <XAxis dataKey="name" stroke="#a1a1aa" fontSize={12} />
                <YAxis stroke="#a1a1aa" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#171717', border: '1px solid #262626' }} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="flex gap-2 mb-6">
          {['all', 'hackernews', 'reddit'].map(f => (
            <button key={f} onClick={() => setFilter(f)} className={`px-4 py-2 rounded-lg font-medium ${
              filter === f ? 'bg-[#22c55e] text-black' : 'bg-[#262626] text-[#a1a1aa]'
            }`}>
              {f === 'all' ? 'Todas' : f}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          {filteredTrends.map((trend, index) => (
            <div key={`${trend.source}-${trend.source_id}`} className="bg-[#171717] border border-[#262626] rounded-xl p-4 hover:border-[#22c55e]/30">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[#a1a1aa] text-sm">#{index + 1}</span>
                    <h4 className="text-lg font-semibold text-white truncate">{trend.name}</h4>
                    <span className={`px-2 py-0.5 text-xs rounded-full ${getSourceColor(trend.source)}`}>{trend.source}</span>
                  </div>
                  <p className="text-[#a1a1aa] text-sm mb-2 line-clamp-2">{trend.description}</p>
                  <a href={trend.url} target="_blank" rel="noopener" className="text-[#22c55e] text-sm hover:underline">Ver &rarr;</a>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span className={`px-3 py-1 text-xs rounded-full border ${getActionColor(trend.recommended_action)}`}>
                    {trend.recommended_action}
                  </span>
                  <div className="text-right">
                    <p className="text-[#a1a1aa] text-xs">Tropicalizacao</p>
                    <p className="text-lg font-bold text-green-400">{trend.tropicalization_score}</p>
                    <p className="text-[#a1a1aa] text-xs">Moat</p>
                    <p className="text-lg font-bold text-purple-400">{trend.moat_score}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}