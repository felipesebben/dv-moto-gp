-- The Italy locator, as real geography (north-up, so a normal Tableau map works here): one
-- polygon per land mass (mainland, Sicily, Sardinia) and the point marking Mugello at the
-- centre of the circuit outline. Rings are written counter-clockwise, the usual convention
-- for geography polygons (a clockwise ring could be read as "everything except Italy").
create or replace table poster.locator_features as
with ring as (
    select
        polygon_id,
        list(lon order by point_idx) as lons,
        list(lat order by point_idx) as lats,
        -- shoelace sum: positive when the ring runs counter-clockwise
        sum(lon * lead_lat - lead_lon * lat) as twice_area
    from (
        select
            *,
            lead(lon) over w as lead_lon,
            lead(lat) over w as lead_lat
        from stg_italy_outline
        window w as (partition by polygon_id order by point_idx)
    )
    group by polygon_id
),

ordered as (
    select
        polygon_id,
        case when twice_area > 0 then lons else list_reverse(lons) end as lons,
        case when twice_area > 0 then lats else list_reverse(lats) end as lats
    from ring
)

select
    'italy' as layer,
    'Italy' as label,
    polygon_id,
    null as shape_file,
    'POLYGON((' || array_to_string(
        list_transform(range(1, len(lons) + 1), lambda i: format('{:.6f} {:.6f}', lons[i], lats[i])), ', '
    ) || '))' as geometry
from ordered

union all

-- Mugello marker: the centre of the circuit outline (its closing point repeats the first).
select
    'mugello' as layer,
    'Mugello' as label,
    null as polygon_id,
    'mugello_marker' as shape_file,
    format('POINT({:.6f} {:.6f})', avg(lon), avg(lat)) as geometry
from stg_track_points
where point_idx < (select max(point_idx) from stg_track_points)
order by layer, polygon_id;
