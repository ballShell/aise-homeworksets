import React from 'react'
import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link to="/dashboard" className="text-xl font-bold">
            AI 旅行规划师
          </Link>
          <div className="text-sm text-blue-100">
            公开访问 - 所有用户共享行程
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

