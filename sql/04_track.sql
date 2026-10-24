-- Circuit outline in drawing order, with corner names on the corner points. Feeds the map.
create or replace table poster.track as
select
    t.point_idx,
    t.lon,
    t.lat,
    round(t.distance_m, 1) as distance_m,
    c.turn,
    c.corner_name
from stg_track_points as t
left join seed_corners as c using (point_idx)
order by t.point_idx;
