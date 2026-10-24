-- Circuit outline in drawing order, with corner names on the corner points. Feeds the map.
-- x_m / y_m: metres from the start line in the TV orientation (north points left, east up),
-- because Tableau's own maps can't rotate. Plot with equal axis ranges to keep the shape.
create or replace table poster.track as
with origin as (
    select lon as lon0, lat as lat0 from stg_track_points where point_idx = 0
),

local_m as (
    select
        t.*,
        radians(t.lat - o.lat0) * 6371008.8 as north_m,
        radians(t.lon - o.lon0) * cos(radians(o.lat0)) * 6371008.8 as east_m
    from stg_track_points as t, origin as o
)

select
    l.point_idx,
    l.lon,
    l.lat,
    round(-l.north_m, 1) as x_m,
    round(l.east_m, 1) as y_m,
    round(l.distance_m, 1) as distance_m,
    c.turn,
    c.corner_name
from local_m as l
left join seed_corners as c using (point_idx)
order by l.point_idx;
