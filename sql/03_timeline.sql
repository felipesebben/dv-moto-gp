-- One row per lap: who led, where the protagonist and rival were, and the story beat (if any).
create or replace table poster.timeline as
with race_time as (
    select
        rider_number,
        lap,
        sum(lap_time_s) over (partition by rider_number order by lap) as race_time_s
    from stg_laps
),

at_line as (
    select
        lap,
        max(rider_number) filter (where position = 1) as leader_number,
        max(position) filter (where rider_number = getvariable('protagonist')) as protagonist_position,
        max(position) filter (where rider_number = getvariable('rival')) as rival_position
    from stg_lap_chart
    where lap > 0
    group by lap
)

select
    a.lap,
    leader.rider_name as leader_name,
    a.leader_number = getvariable('protagonist') as protagonist_leads,
    a.protagonist_position,
    a.rival_position,
    round(rt_rival.race_time_s - rt_prot.race_time_s, 3) as rival_minus_protagonist_s,
    m.moment_id is not null as is_key_moment,
    m.headline,
    m.story
from at_line as a
join poster.riders as leader on leader.rider_number = a.leader_number
join race_time as rt_prot
    on rt_prot.lap = a.lap and rt_prot.rider_number = getvariable('protagonist')
join race_time as rt_rival
    on rt_rival.lap = a.lap and rt_rival.rider_number = getvariable('rival')
left join seed_key_moments as m on m.lap = a.lap
order by a.lap;
