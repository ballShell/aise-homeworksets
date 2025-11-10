import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error: error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("Uncaught error in Map component:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="flex items-center justify-center h-[500px] bg-gray-100 rounded">
          <div className="text-center">
            <p className="text-red-500 font-semibold">地图加载失败</p>
            <p className="text-gray-500 mt-2">部分活动可能缺少有效的地理位置信息。</p>
            <p className="text-xs text-gray-400 mt-4">Error: {this.state.error?.message}</p>
          </div>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;