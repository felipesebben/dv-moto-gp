-- The Italy locator: the outline (one ring per polygon: mainland, Sicily, Sardinia) and the
-- point marking Mugello. Plain lon/lat, north-up, so a Tableau map works here.
-- Tableau: polygon mark, Detail = polygon_id, Path = point_idx.
create or replace table poster.italy_outline as
select polygon_id, point_idx, lon, lat
from stg_italy_outline
order by polygon_id, point_idx;

-- Mugello marker: the centre of the circuit outline (its closing point repeats the first).
create or replace table poster.locator_points as
select
    'Mugello' as label,
    e.circuit_name,
    e.circuit_town,
    round(avg(t.lon), 5) as lon,
    round(avg(t.lat), 5) as lat
from stg_track_points as t, stg_event as e
where t.point_idx < (select max(point_idx) from stg_track_points)
group by e.circuit_name, e.circuit_town;
