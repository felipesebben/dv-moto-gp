-- The key numbers beside the map: the time between Rossi and Capirossi at three moments,
-- in race order. Labels come from the seed; the values from the timeline.
create or replace table poster.key_numbers as
select
    row_number() over (order by k.moment_id) as rank,
    k.moment_id,
    m.lap,
    m.rider_role,
    abs(tl.rival_minus_protagonist_s) as value_s,
    format('{:.3f} s', abs(tl.rival_minus_protagonist_s)) as value_text,
    k.label
from seed_key_numbers as k
join poster.key_moments as m using (moment_id)
join poster.timeline as tl on tl.lap = m.lap
order by k.moment_id;
