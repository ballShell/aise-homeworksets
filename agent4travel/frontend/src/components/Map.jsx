import React, { useEffect, useRef, useCallback, useState } from 'react';
import AMapLoader from '@amap/amap-jsapi-loader';
import PropTypes from 'prop-types';

const Map = ({ activities, highlightedActivity, onActivityClick }) => {
  const mapContainer = useRef(null);
  const mapInstance = useRef(null);
  const markersRef = useRef([]);
  const infoWindowsRef = useRef([]);
  const AMapRef = useRef(null);

  const updateMapMarkers = useCallback(() => {
    if (!mapInstance.current || !activities || !AMapRef.current) return;

    const AMap = AMapRef.current;

    // Clear existing markers and info windows
    mapInstance.current.remove(markersRef.current);
    infoWindowsRef.current.forEach(iw => iw.close());
    markersRef.current = [];
    infoWindowsRef.current = [];

    const validActivities = activities.filter(activity =>
      activity.coordinates &&
      typeof activity.coordinates.lat === 'number' &&
      typeof activity.coordinates.lng === 'number'
    );

    if (validActivities.length > 0) {
      validActivities.forEach((activity, index) => {
        const isHighlighted = highlightedActivity && highlightedActivity.id === activity.id;
        
        const marker = new AMap.Marker({
          position: [activity.coordinates.lng, activity.coordinates.lat],
          title: activity.location_name || activity.activity,
          label: {
            content: `${index + 1}`,
            direction: 'right',
          },
          icon: isHighlighted ? new AMap.Icon({
            size: new AMap.Size(40, 40),
            image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
          }) : undefined,
        });

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
        });

        marker.on('click', () => {
          infoWindowsRef.current.forEach(iw => iw.close());
          infoWindow.open(mapInstance.current, marker.getPosition());
          if (onActivityClick) {
            onActivityClick(activity);
          }
        });

        mapInstance.current.add(marker);
        markersRef.current.push(marker);
        infoWindowsRef.current.push(infoWindow);
      });

      // Fit map to show all markers
      mapInstance.current.setFitView();
    } else {
      console.warn('No valid coordinates found in activities');
    }
  }, [activities, highlightedActivity, onActivityClick]);

  useEffect(() => {
    const initMap = async () => {
      try {
        const AMap = await AMapLoader.load({
          key: import.meta.env.VITE_GAODE_JS_API_KEY,
          version: '2.0',
          plugins: ['AMap.Marker', 'AMap.InfoWindow'],
        });

        AMapRef.current = AMap;

        if (mapContainer.current && !mapInstance.current) {
          mapInstance.current = new AMap.Map(mapContainer.current, {
            zoom: 10,
            center: [116.397428, 39.90923], // Default to Beijing
          });
        }

        updateMapMarkers();
      } catch (error) {
        console.error('Error loading map:', error);
      }
    };

    initMap();
  }, []); // Init map only once

  useEffect(() => {
    updateMapMarkers();
  }, [activities, updateMapMarkers]);

  useEffect(() => {
    if (highlightedActivity && mapInstance.current && AMapRef.current) {
      const { coordinates } = highlightedActivity;
      if (coordinates && typeof coordinates.lat === 'number' && typeof coordinates.lng === 'number') {
        mapInstance.current.setCenter([coordinates.lng, coordinates.lat]);
        mapInstance.current.setZoom(15);

        // Find the corresponding marker and open its info window
        const activityIndex = activities.findIndex(a => a.id === highlightedActivity.id);
        if (activityIndex !== -1 && markersRef.current[activityIndex] && infoWindowsRef.current[activityIndex]) {
          infoWindowsRef.current.forEach(iw => iw.close());
          infoWindowsRef.current[activityIndex].open(mapInstance.current, markersRef.current[activityIndex].getPosition());
        }
      }
    }
  }, [highlightedActivity, activities]);

  return (
    <div
      ref={mapContainer}
      style={{
        width: '100%',
        height: '100%',
        minHeight: '500px',
      }}
    />
  );
};

Map.propTypes = {
  activities: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    activity: PropTypes.string,
    location_name: PropTypes.string,
    time: PropTypes.string,
    description: PropTypes.string,
    coordinates: PropTypes.shape({
      lat: PropTypes.number,
      lng: PropTypes.number,
    }),
  })).isRequired,
  highlightedActivity: PropTypes.object,
  onActivityClick: PropTypes.func,
};

export default Map;

