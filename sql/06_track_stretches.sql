-- The stretches of track painted yellow (where Rossi's moments happened), one path per stretch.
-- A stretch may wrap past the start line (to_idx < from_idx). The outline's last point repeats
-- point 0, so it's skipped. `seq` is the drawing order (Tableau: Path).
create or replace table poster.track_stretches as
with closing as (
    select max(point_idx) as last_idx from poster.track
),

points as (
    select
        s.stretch_id,
        s.label,
        s.moment_ids,
        unnest(
            case
                when s.to_idx >= s.from_idx then range(s.from_idx, s.to_idx + 1)
                else list_concat(range(s.from_idx, c.last_idx), range(0, s.to_idx + 1))
            end
        ) as point_idx,
        s.from_idx,
        c.last_idx
    from seed_stretches as s, closing as c
)

select
    p.stretch_id,
    p.label,
    p.moment_ids,
    case
        when p.point_idx >= p.from_idx then p.point_idx - p.from_idx
        else p.point_idx + p.last_idx - p.from_idx
    end as seq,
    p.point_idx,
    t.x_m,
    t.y_m
from points as p
join poster.track as t using (point_idx)
order by p.stretch_id, seq;
