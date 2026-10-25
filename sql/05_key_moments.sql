-- The story beats. A moment with a turn is also placed on the map; the others live on the
-- race band only. `focus` says whose moment it is (Rossi's, or Capirossi's charge), and
-- `rider_position` is where that rider was on that lap: the race band's connector ends there.
-- Cards alternate above and below the positions chart so close laps don't collide.
create or replace table poster.key_moments as
select
    m.moment_id,
    m.lap,
    m.turn,
    c.corner_name,
    m.turn is not null as on_map,
    t.lon,
    t.lat,
    t.x_m,
    t.y_m,
    m.headline,
    m.story,
    m.focus as rider_role,
    r.rider_number,
    r.display_name as rider_display_name,
    p.position as rider_position,
    tl.protagonist_position,
    tl.leader_name,
    case when row_number() over (order by m.moment_id) % 2 = 1 then 'above' else 'below' end
        as card_side
from seed_key_moments as m
left join seed_corners as c using (turn)
left join poster.track as t using (point_idx)
left join poster.timeline as tl using (lap)
left join poster.riders as r on r.role = m.focus
left join poster.positions as p on p.lap = m.lap and p.rider_number = r.rider_number
order by m.moment_id;
