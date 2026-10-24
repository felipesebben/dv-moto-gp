-- Position of every rider at the end of each lap (lap 0 = starting grid). Feeds the rank chart.
create or replace table poster.positions as
select
    lc.lap,
    lc.position,
    lc.rider_number,
    r.rider_name,
    r.role
from stg_lap_chart as lc
join poster.riders as r using (rider_number);
