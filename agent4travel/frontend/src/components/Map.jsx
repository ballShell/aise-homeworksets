import React, { useEffect, useRef, useCallback } from 'react'
import AMapLoader from '@amap/amap-jsapi-loader'

const Map = ({ activities, onActivityHover, highlightedActivity, onActivityClick }) => {
  const mapContainer = useRef(null)
  const mapInstance = useRef(null)
  const markersRef = useRef([])
  const infoWindowsRef = useRef([])
  const AMapRef = useRef(null)

  // 更新地图标记函数
  const updateMapMarkers = useCallback((AMap, currentActivities, currentHighlightedActivity = null) => {
    if (!mapInstance.current || !AMap) return

    // 清除现有标记和信息窗口
    markersRef.current.forEach(marker => {
      mapInstance.current.remove(marker)
    })
    infoWindowsRef.current.forEach(infoWindow => {
      infoWindow.close()
    })
    markersRef.current = []
    infoWindowsRef.current = []

    // 添加新标记
    if (currentActivities && currentActivities.length > 0) {
      const validActivities = currentActivities.filter(
        a => a.lat != null && a.lng != null && !isNaN(a.lat) && !isNaN(a.lng)
      )

      if (validActivities.length > 0) {
        // 如果没有高亮活动，设置地图中心为第一个有效活动
        if (!currentHighlightedActivity) {
          const firstActivity = validActivities[0]
          mapInstance.current.setCenter([firstActivity.lng, firstActivity.lat])

          // 如果只有一个活动，设置合适的缩放级别
          if (validActivities.length === 1) {
            mapInstance.current.setZoom(15)
          } else {
            // 多个活动，使用包含所有点的视图
            const bounds = new AMap.Bounds()
            validActivities.forEach(activity => {
              bounds.extend([activity.lng, activity.lat])
            })
            mapInstance.current.setBounds(bounds)
          }
        }

        // 创建标记
        validActivities.forEach((activity, index) => {
          // 检查是否是高亮活动（通过坐标和位置名称匹配）
          const isHighlighted = currentHighlightedActivity && 
            currentHighlightedActivity.lat === activity.lat &&
            currentHighlightedActivity.lng === activity.lng &&
            currentHighlightedActivity.location_name === activity.location_name

          const marker = new AMap.Marker({
            position: [activity.lng, activity.lat],
            title: activity.location_name || activity.activity,
            label: {
              content: `${index + 1}`,
              direction: 'right',
            },
            // 高亮显示使用红色图标
            icon: isHighlighted ? new AMap.Icon({
              size: new AMap.Size(40, 40),
              image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
            }) : undefined,
          })

          // 创建信息窗口
          const infoWindow = new AMap.InfoWindow({
            content: `
              <div style="padding: 10px; min-width: 200px;">
                <h3 style="margin: 0 0 5px 0; font-size: 16px; font-weight: bold;">${activity.activity || '活动'}</h3>
                <p style="margin: 0; color: #666; font-size: 14px;">📍 ${activity.location_name || '未知位置'}</p>
                ${activity.time ? `<p style="margin: 5px 0 0 0; color: #999; font-size: 12px;">🕐 ${activity.time}</p>` : ''}
                ${activity.description ? `<p style="margin: 5px 0 0 0; color: #666; font-size: 12px;">${activity.description}</p>` : ''}
              </div>
            `,
            offset: new AMap.Pixel(0, -30),
          })

          marker.on('click', () => {
            // 关闭其他信息窗口
            infoWindowsRef.current.forEach(iw => iw.close())
            // 打开当前信息窗口
            infoWindow.open(mapInstance.current, marker.getPosition())
            // 通知父组件
            if (onActivityClick) {
              onActivityClick(activity)
            }
          })

          mapInstance.current.add(marker)
          markersRef.current.push(marker)
          infoWindowsRef.current.push(infoWindow)
        })
      } else {
        // 没有有效坐标，显示提示
        console.warn('No valid coordinates found in activities')
      }
    }
  }, []) // useCallback 依赖项为空，因为函数内部使用的都是参数

  // 初始化地图
  useEffect(() => {
    const initMap = async () => {
      try {
        const AMap = await AMapLoader.load({
          key: import.meta.env.VITE_GAODE_JS_API_KEY,
          version: '2.0',
          plugins: ['AMap.Marker', 'AMap.InfoWindow'],
        })

        AMapRef.current = AMap

        if (mapContainer.current && !mapInstance.current) {
          mapInstance.current = new AMap.Map(mapContainer.current, {
            zoom: 10,
            center: [139.6917, 35.6895], // 默认东京（而不是北京）
          })
        }

        // 初始化时更新标记（如果有活动数据）
        if (activities && activities.length > 0) {
          updateMapMarkers(AMap, activities, highlightedActivity)
        }
      } catch (error) {
        console.error('Error loading map:', error)
      }
    }

    initMap()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // 只在组件挂载时初始化一次

  // 当活动列表变化时更新地图
  useEffect(() => {
    if (AMapRef.current) {
      updateMapMarkers(AMapRef.current, activities, highlightedActivity)
    }
  }, [activities, updateMapMarkers, highlightedActivity])

  // 处理活动高亮和点击定位
  useEffect(() => {
    if (highlightedActivity && mapInstance.current && AMapRef.current && activities) {
      const lat = highlightedActivity.lat
      const lng = highlightedActivity.lng
      
      if (lat != null && lng != null && !isNaN(lat) && !isNaN(lng)) {
        // 平滑移动到目标位置
        mapInstance.current.setCenter([lng, lat])
        mapInstance.current.setZoom(15)
        
        // 找到对应的标记并高亮
        markersRef.current.forEach((marker, index) => {
          // 通过坐标匹配找到对应的活动
          const activity = activities.find(a => 
            a.lat === lat && 
            a.lng === lng &&
            a.location_name === highlightedActivity.location_name
          )
          
          if (activity) {
            // 更新所有标记：高亮当前，恢复其他
            markersRef.current.forEach((m, i) => {
              if (i === index) {
                // 高亮当前标记
                m.setIcon(new AMapRef.current.Icon({
                  size: new AMapRef.current.Size(40, 40),
                  image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
                }))
                // 打开信息窗口
                if (infoWindowsRef.current[i]) {
                  infoWindowsRef.current.forEach(iw => iw.close())
                  infoWindowsRef.current[i].open(mapInstance.current, m.getPosition())
                }
              } else {
                // 恢复其他标记为默认样式
                m.setIcon(undefined)
              }
            })
          }
        })
      }
    } else if (!highlightedActivity && mapInstance.current && AMapRef.current) {
      // 取消高亮时，恢复所有标记为默认样式
      markersRef.current.forEach(marker => {
        marker.setIcon(undefined)
      })
      // 关闭所有信息窗口
      infoWindowsRef.current.forEach(iw => iw.close())
    }
  }, [highlightedActivity, activities])

  return (
    <div
      ref={mapContainer}
      style={{
        width: '100%',
        height: '100%',
        minHeight: '500px',
      }}
    />
  )
}

export default Map

