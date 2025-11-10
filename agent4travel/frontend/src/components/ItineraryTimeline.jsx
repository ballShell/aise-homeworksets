import React, { useState } from 'react'

const ItineraryTimeline = ({ dailyPlans, onActivityHover, onActivityClick }) => {
  const [hoveredActivity, setHoveredActivity] = useState(null)
  const [clickedActivity, setClickedActivity] = useState(null)

  const handleActivityHover = (activity) => {
    setHoveredActivity(activity)
    if (onActivityHover) {
      onActivityHover(activity)
    }
  }

  const handleActivityLeave = () => {
    setHoveredActivity(null)
    if (onActivityHover) {
      onActivityHover(null)
    }
  }

  const handleActivityClick = (activity) => {
    setClickedActivity(activity)
    if (onActivityClick) {
      onActivityClick(activity)
    }
    if (onActivityHover) {
      onActivityHover(activity)
    }
  }

  return (
    <div className="space-y-8">
      {dailyPlans.map((dayPlan) => (
        <div key={dayPlan.day} className="relative">
          {/* 时间线 */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-blue-200"></div>

          {/* 日期标题 */}
          <div className="relative flex items-center mb-4">
            <div className="absolute left-0 w-8 h-8 bg-blue-500 rounded-full border-4 border-white shadow-lg flex items-center justify-center">
              <span className="text-white text-sm font-bold">{dayPlan.day}</span>
            </div>
            <div className="ml-12">
              <h3 className="text-xl font-bold text-gray-800">{dayPlan.title}</h3>
              {dayPlan.summary && (
                <p className="text-gray-600 text-sm mt-1">{dayPlan.summary}</p>
              )}
              {dayPlan.daily_budget && (
                <p className="text-green-600 text-sm font-medium mt-1 flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  每日预算: ¥{dayPlan.daily_budget}
                </p>
              )}
            </div>
          </div>

          {/* 活动列表 */}
          <div className="ml-12 space-y-4">
            {dayPlan.activities.map((activity, index) => (
              <div
                key={index}
                className={`
                  bg-white rounded-lg shadow-md p-4 border-l-4 transition-all
                  ${hoveredActivity === activity || clickedActivity === activity
                    ? 'border-blue-500 shadow-lg transform scale-105' 
                    : 'border-gray-300'
                  }
                  cursor-pointer hover:bg-blue-50
                `}
                onMouseEnter={() => handleActivityHover(activity)}
                onMouseLeave={handleActivityLeave}
                onClick={() => handleActivityClick(activity)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-blue-600 font-semibold">
                        {activity.time}
                      </span>
                      <span className="text-gray-800 font-medium">
                        {activity.activity}
                      </span>
                    </div>
                    {activity.description && (
                      <p className="text-gray-600 text-sm mb-2">
                        {activity.description}
                      </p>
                    )}
                    <p className="text-gray-500 text-sm flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {activity.location_name}
                    </p>
                    {activity.estimated_cost && !isNaN(parseFloat(activity.estimated_cost)) && (
                      <p className="text-green-600 text-sm font-medium flex items-center gap-1 mt-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        预估花费: ¥{parseFloat(activity.estimated_cost).toFixed(2)}
                      </p>
                    )}
                  </div>
                  {activity.lat && activity.lng && (
                    <div className="ml-2 text-green-500">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ItineraryTimeline

