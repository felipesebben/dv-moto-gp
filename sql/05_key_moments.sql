-- The story beats placed on the map: moments without a turn appear on the timeline only.
create or replace table poster.key_moments as
select
    m.moment_id,
    m.lap,
    m.turn,
    c.corner_name,
    t.lon,
    t.lat,
    t.x_m,
    t.y_m,
    m.headline,
    m.story,
    tl.protagonist_position,
    tl.leader_name
from seed_key_moments as m
left join seed_corners as c using (turn)
left join poster.track as t using (point_idx)
left join poster.timeline as tl using (lap)
order by m.moment_id;
