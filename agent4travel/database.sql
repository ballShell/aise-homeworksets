-- AI 旅行规划师数据库表结构
-- 公开访问版本：所有数据对所有用户开放

-- 1. 旅行计划 (trips)
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    budget NUMERIC,
    preferences TEXT, -- 存储 "美食, 动漫" 等
    raw_prompt TEXT,  -- 存储用户原始输入
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 每日行程 (itineraries)
CREATE TABLE IF NOT EXISTS itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE NOT NULL,
    day_number INT NOT NULL,
    title TEXT,
    summary TEXT,
    activities JSONB, -- 存储 [{ "time": "09:00", "activity": "...", "location_name": "...", "lat": 12.34, "lng": 56.78 }]
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. 费用记录 (expenses)
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    category TEXT, -- 例如: 餐饮, 交通, 住宿
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. 禁用 RLS (Row Level Security) - 允许所有用户访问所有数据
ALTER TABLE trips DISABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;

-- 5. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_itineraries_trip_id ON itineraries(trip_id);
CREATE INDEX IF NOT EXISTS idx_expenses_trip_id ON expenses(trip_id);
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at DESC);

