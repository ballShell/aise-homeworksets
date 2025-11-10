import React, { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiClient from '../lib/apiClient'
import ErrorBoundary from '../components/ErrorBoundary';
import Map from '../components/Map'
import ItineraryTimeline from '../components/ItineraryTimeline'
import VoiceInput from '../components/VoiceInput'

const TripDetail = () => {
  const { tripId } = useParams()
  const navigate = useNavigate()
  const [trip, setTrip] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expenseDescription, setExpenseDescription] = useState('')
  const [expenseLoading, setExpenseLoading] = useState(false)
  const [highlightedActivity, setHighlightedActivity] = useState(null)

  useEffect(() => {
    loadTripDetail()
  }, [tripId])

  const loadTripDetail = async () => {
    try {
      const response = await apiClient.get(`/trips/${tripId}`)
      setTrip(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || '加载行程失败')
    } finally {
      setLoading(false)
    }
  }

  const handleExpenseSubmit = async (e) => {
    e.preventDefault()
    if (!expenseDescription.trim()) {
      return
    }

    setExpenseLoading(true)
    try {
      await apiClient.post('/v1/trips/expense', {
        trip_id: tripId,
        description: expenseDescription,
      })
      setExpenseDescription('')
      // 重新加载行程以更新费用列表
      loadTripDetail()
    } catch (err) {
      setError(err.response?.data?.detail || '记录费用失败')
    } finally {
      setExpenseLoading(false)
    }
  }

  const handleVoiceTranscript = (transcript) => {
    setExpenseDescription((prev) => prev + transcript)
  }

  // 收集所有活动用于地图显示
  const allActivities = useMemo(() => {
      if (!trip || !trip.daily_plan) return [];
      const activities = trip.daily_plan.flatMap(day => day.activities || []);
      return activities.filter(activity => 
          activity.coordinates && 
          typeof activity.coordinates.lat === 'number' && 
          typeof activity.coordinates.lng === 'number'
      );
  }, [trip]);

    return (
        <div className="trip-detail-container">
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          {/* 标题和返回按钮 */}
          <div className="mb-6 flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate('/dashboard')}
                className="text-blue-600 hover:text-blue-800 mb-2 flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                返回
              </button>
              <h1 className="text-3xl font-bold text-gray-900">{trip?.destination}</h1>
              {trip?.budget_analysis && (
                <p className="text-gray-600 mt-2">{trip.budget_analysis}</p>
              )}
            </div>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* 主内容区域：左右分栏 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* 左侧：行程时间线 */}
            <div className="bg-white rounded-lg shadow-md p-6 overflow-y-auto max-h-[800px]">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">行程安排</h2>
              {trip?.daily_plan && trip.daily_plan.length > 0 ? (
                <ItineraryTimeline
                  dailyPlans={trip.daily_plan}
                  onActivityHover={setHighlightedActivity}
                  onActivityClick={setHighlightedActivity}
                />
              ) : (
                <p className="text-gray-500">暂无行程安排</p>
              )}
            </div>

            {/* 右侧：地图 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">地图视图</h2>
              {loading ? (
                <div className="flex items-center justify-center h-[500px] bg-gray-100 rounded">
                  <p className="text-gray-500">地图加载中...</p>
                </div>
              ) : allActivities.length > 0 ? (
                <ErrorBoundary>
                  <Map
                    activities={allActivities}
                    highlightedActivity={highlightedActivity}
                    onActivityClick={setHighlightedActivity}
                  />
                </ErrorBoundary>
              ) : (
                <div className="flex items-center justify-center h-[500px] bg-gray-100 rounded">
                  <p className="text-gray-500">部分活动可能缺少有效的位置信息。</p>
                </div>
              )}
            </div>
          </div>

          {/* 费用记录区域 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">费用记录</h2>
            <form onSubmit={handleExpenseSubmit} className="flex gap-4 mb-4">
              <div className="flex-1 flex gap-2">
                <input
                  type="text"
                  value={expenseDescription}
                  onChange={(e) => setExpenseDescription(e.target.value)}
                  placeholder="例如：拉面 50 元"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <VoiceInput onTranscript={handleVoiceTranscript} disabled={expenseLoading} />
              </div>
              <button
                type="submit"
                disabled={expenseLoading || !expenseDescription.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {expenseLoading ? '记录中...' : '记一笔'}
              </button>
            </form>

            {/* 费用列表 */}
            <div className="mt-4">
              {trip?.expenses && trip.expenses.length > 0 ? (
                <div className="space-y-2">
                  {trip.expenses.map((expense) => (
                    <div
                      key={expense.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-gray-800">{expense.description}</p>
                        {expense.category && (
                          <p className="text-sm text-gray-500">{expense.category}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900">¥{expense.amount}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(expense.created_at).toLocaleDateString('zh-CN')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">暂无费用记录</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TripDetail


    const handleAddExpense = async () => {
        if (!newExpense.description || !newExpense.amount) return
        try {
            await apiClient.post('/trips/expense', {
                trip_id: tripId,
                description: newExpense.description,
            })
            setExpenseDescription('')
            // 重新加载行程以更新费用列表
            loadTripDetail()
        } catch (err) {
            setError(err.response?.data?.detail || '记录费用失败')
        } finally {
            setExpenseLoading(false)
        }
    }

