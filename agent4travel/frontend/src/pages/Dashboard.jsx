import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../lib/apiClient'
import VoiceInput from '../components/VoiceInput'

const Dashboard = () => {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [trips, setTrips] = useState([])
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadTrips()
  }, [])

  const loadTrips = async () => {
    try {
      const response = await apiClient.get('/trips')
      setTrips(response.data)
    } catch (error) {
      console.error('Error loading trips:', err)
    }
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('请输入您的旅行需求')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await apiClient.post('/trips/plan', {
        prompt: prompt,
      })
      navigate(`/trip/${response.data.trip_id}`)
    } catch (err) {
      setError(err.response?.data?.detail || '生成行程失败，请重试')
      setLoading(false)
    }
  }

  const handleVoiceTranscript = (transcript) => {
    setPrompt((prev) => prev + transcript)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">AI 旅行规划师</h1>
        <p className="text-gray-600 mb-8">输入您的旅行需求，AI 将为您生成详细的旅行计划。所有行程对所有用户开放。</p>

        {/* 智能输入区域 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            创建新行程
          </h2>
          <div className="space-y-4">
            <div className="flex gap-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="例如：我想去日本，5天，预算1万元，喜欢美食和动漫"
                className="flex-1 min-h-[120px] px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <div className="flex items-start">
                <VoiceInput onTranscript={handleVoiceTranscript} disabled={loading} />
              </div>
            </div>
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            <button
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
              className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  正在生成行程...
                </span>
              ) : (
                '生成行程'
              )}
            </button>
          </div>
        </div>

        {/* 行程列表 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            所有行程
          </h2>
          {trips.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              还没有行程，创建一个新行程开始吧！
            </p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {trips.map((trip) => (
                <div
                  key={trip.id}
                  onClick={() => navigate(`/trip/${trip.id}`)}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">
                    {trip.destination}
                  </h3>
                  <div className="text-sm text-gray-600 space-y-1">
                    {trip.start_date && trip.end_date && (
                      <p>
                        {trip.start_date} - {trip.end_date}
                      </p>
                    )}
                    {trip.budget && <p>预算: ¥{trip.budget}</p>}
                    <p className="text-gray-400">
                      {new Date(trip.created_at).toLocaleDateString('zh-CN')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

