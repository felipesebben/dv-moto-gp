-- The race band canvas: the positions chart, the moments' badges and connectors, the axis and
-- the footer key in one table, drawn with the same map-layer technique as the map.
-- Units are poster px from the wireframe (layout D), with the origin where lap 0 meets the axis
-- and y pointing up (so lower positions are further down). The frame is the band from the top
-- cards' edge (TOP_CARDS) to just under the footer key (FOOT_Y + 8), across the poster between
-- the margins: the Tableau sheet for it is 1728 x 560 px, placed at x 96, y = TOP_CARDS.
-- Lines are eased between laps (smoothstep, 10 steps a lap), as in the wireframe.
create or replace table poster.race_features as
with params as (
    select
        1400 / 23 as lap_px,  -- X1 - X0 = 1400 px for 23 laps
        24 as first_row_px,  -- 1st place sits 24 px under the axis
        16 as row_px,
        136 as top_edge_px,  -- the top cards' badges end 136 px above the axis
        148 as top_badge_px,
        184 as bottom_edge_px,  -- the bottom cards' badges start 184 px under the axis
        196 as bottom_badge_px,
        387 as key_px  -- the footer key's centre line, under the axis
),

place as (
    select
        p.*,
        lap * lap_px as x,
        -(first_row_px + (position - 1) * row_px) as y
    from poster.positions as p, params
),

chart_rider as (
    select rider_number, display_name, role, final_position
    from poster.riders
    where in_chart
),

eased as (
    -- t runs 0..230 (tenths of a lap); position eases from one lap to the next
    select
        r.rider_number,
        r.role,
        t,
        a.x + (b.x - a.x) * s as x,
        a.y + (b.y - a.y) * (s * s * (3 - 2 * s)) as y
    from chart_rider as r,
        range(0, 231) as tt (t),
        lateral (select least(t // 10, 22) as lap0, (t - least(t // 10, 22) * 10) / 10 as s)
    join place as a on a.rider_number = r.rider_number and a.lap = lap0
    join place as b on b.rider_number = r.rider_number and b.lap = lap0 + 1
),

moment as (
    select
        m.moment_id,
        m.rider_role,
        m.card_side,
        pl.x,
        pl.y as rider_y,
        case m.card_side when 'above' then p.top_edge_px else -p.bottom_edge_px end as edge_y,
        case m.card_side when 'above' then p.top_badge_px else -p.bottom_badge_px end as badge_y
    from poster.key_moments as m, params as p
    join place as pl on pl.lap = m.lap and pl.rider_number = m.rider_number
),

finish as (
    select r.*, pl.x, pl.y
    from chart_rider as r
    join place as pl on pl.rider_number = r.rider_number and pl.lap = 23
    where r.role != 'other'
),

key_item as (
    select * from (values
        ('badge', 'Rossi moment', 'protagonist', '4', -54, -32),
        ('badge', 'Capirossi moment', 'rival', '2', 122, 144),
        ('line', 'where it happened', 'protagonist', null, 320, 352)
    ) as k (kind, text, role, badge_label, mark_x, text_x)
),

features as (
    select
        'frame' as layer, null as align, f.corner_id as item, null::bigint as moment_id,
        null as role, null as label, f.x, f.y, wkt_point(f.x, f.y) as geometry
    from (values ('top left', -64, 160), ('top right', 1664, 160),
                 ('bottom left', -64, -400), ('bottom right', 1664, -400)) as f (corner_id, x, y)

    union all

    select 'axis', null, 'axis', null, null, null, null, null, wkt_segment(0, 0, 23 * lap_px, 0)
    from params

    union all

    select
        'tick', null, 'lap ' || lap, null, null, null, null, null,
        wkt_segment(lap * lap_px, 4, lap * lap_px, -4)
    from params, range(0, 24) as l (lap)

    union all

    select 'axis_label', 'left', text, null, null, text, -16, y, wkt_point(-16, y)
    from (values ('Grid', 0), ('1st', -24), ('4th', -72), ('8th', -136)) as a (text, y)

    union all

    select 'axis_label', 'center', 'Lap 23', null, null, 'Lap 23', x, -155, wkt_point(x, -155)
    from (select 23 * lap_px as x from params)

    union all

    select
        'line', null, display_name, null, role, display_name, null, null,
        'LINESTRING(' || string_agg(wkt_xy(e.x, e.y), ', ' order by e.t) || ')'
    from eased as e
    join chart_rider using (rider_number, role)
    group by display_name, role

    union all

    -- a background-coloured band under Rossi's line, so it reads as on top where lines cross
    select
        'halo', null, display_name, null, role, null, null, null,
        'LINESTRING(' || string_agg(wkt_xy(e.x, e.y), ', ' order by e.t) || ')'
    from eased as e
    join chart_rider using (rider_number, role)
    where role = 'protagonist'
    group by display_name, role

    union all

    -- straight vertical line from the card's badge to where that rider was on that lap
    select
        'connector', null, 'moment ' || moment_id, moment_id, rider_role, null, null, null,
        wkt_segment(x, edge_y, x, rider_y)
    from moment

    union all

    select
        'rider_dot', null, 'moment ' || moment_id, moment_id, rider_role, null, x, rider_y,
        wkt_point(x, rider_y)
    from moment

    union all

    select
        'badge', null, 'moment ' || moment_id, moment_id, rider_role, moment_id::varchar,
        x, badge_y, wkt_point(x, badge_y)
    from moment

    union all

    select 'rider_dot', null, 'finish ' || display_name, null, role, null, x, y, wkt_point(x, y)
    from finish

    union all

    select
        'end_label', 'right', 'finish ' || display_name, null, role,
        display_name || ' · ' || ordinal(final_position), x + 16, y, wkt_point(x + 16, y)
    from finish

    union all

    select
        'badge', null, 'key: ' || text, null, role, badge_label, mark_x, -key_px,
        wkt_point(mark_x, -key_px)
    from key_item, params
    where kind = 'badge'

    union all

    select
        'key_line', null, 'key: ' || text, null, role, null, null, null,
        wkt_segment(mark_x, -key_px, mark_x + 20, -key_px)
    from key_item, params
    where kind = 'line'

    union all

    select 'key_label', 'right', 'key: ' || text, null, null, text, text_x, -key_px,
        wkt_point(text_x, -key_px)
    from key_item, params
)

select
    layer,
    align,
    item,
    moment_id,
    role,
    label,
    round(x, 1) as x_px,
    round(y, 1) as y_px,
    geometry
from features
order by layer, item;
