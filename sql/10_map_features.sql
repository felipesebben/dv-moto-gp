-- The map canvas: every layer of the circuit map in one table, so one Tableau sheet can stack
-- them as map layers (Tableau: one layer per `layer`, label alignment from `align`).
-- Units are metres in the TV orientation (poster.track x_m / y_m). Label offsets and callout
-- positions come from the wireframe (seeds/corners.csv, seeds/callouts.csv); on the poster
-- 1 px = 1.1498 m, and the frame is the map box (1136 x 800 px) plus 96 px on every side, so
-- the Tableau sheet for this map is 1328 x 992 px.
create or replace table poster.map_features as
with params as (
    select
        1.1498 as m_per_px,
        1328 as frame_w_px,
        992 as frame_h_px,
        14 as start_line_half_px,
        30 as badge_step_px,
        18 as callout_line_px
),

box as (
    select
        (min(x_m) + max(x_m)) / 2 as cx,
        (min(y_m) + max(y_m)) / 2 as cy
    from poster.track
),

corner as (
    select
        c.turn,
        c.corner_name,
        c.label_dx_m,
        c.label_dy_m,
        c.label_anchor,
        t.x_m,
        t.y_m
    from seed_corners as c
    join poster.track as t using (point_idx)
),

moment as (
    select
        m.moment_id,
        m.turn,
        m.headline,
        m.rider_role,
        c.x_m,
        c.y_m,
        k.badge_dx_m,
        k.badge_dy_m,
        k.text_dx_m,
        k.text_dy_m,
        k.text_anchor,
        row_number() over (partition by m.turn order by m.moment_id) - 1 as j
    from poster.key_moments as m
    join corner as c using (turn)
    join seed_callouts as k using (turn)
),

badge as (
    select
        *,
        x_m + badge_dx_m + j * (select badge_step_px * m_per_px from params) as bx,
        y_m + badge_dy_m as by_
    from moment
),

features as (
    -- invisible corner points that fix the framing (Tableau zooms to fit them)
    select
        'frame' as layer,
        null as align,
        f.corner_id as item,
        null::bigint as moment_id,
        null as role,
        null as label,
        b.cx + f.sx * p.frame_w_px * p.m_per_px / 2 as x,
        b.cy + f.sy * p.frame_h_px * p.m_per_px / 2 as y,
        wkt_point(x, y) as geometry
    from box as b, params as p,
        (values ('top left', -1, 1), ('top right', 1, 1),
                ('bottom left', -1, -1), ('bottom right', 1, -1)) as f (corner_id, sx, sy)

    union all

    select
        'track', null, 'outline', null, null, null, null, null,
        'LINESTRING(' || string_agg(wkt_xy(x_m, y_m), ', ' order by point_idx) || ')'
    from poster.track

    union all

    select
        'stretch', null, label, null, 'protagonist', label, null, null,
        'LINESTRING(' || string_agg(wkt_xy(x_m, y_m), ', ' order by seq) || ')'
    from poster.track_stretches
    group by stretch_id, label

    union all

    -- the finish line: the main straight runs across the poster, so the line is vertical
    select
        'start_line', null, 'Start/Finish', null, null, null, x_m, y_m,
        wkt_segment(x_m, y_m - h, x_m, y_m + h)
    from corner, (select start_line_half_px * m_per_px as h from params)
    where turn = 0

    union all

    select
        'corner_dot', null, corner_name, null, null, null, x_m, y_m, wkt_point(x_m, y_m)
    from corner
    where turn > 0

    union all

    select
        'corner_label',
        case label_anchor when 'start' then 'right' when 'end' then 'left' else 'center' end,
        corner_name, null, null, corner_name,
        x_m + label_dx_m, y_m + label_dy_m, wkt_point(x_m + label_dx_m, y_m + label_dy_m)
    from corner

    union all

    -- a thin line from the corner out to the moment's badge
    select
        'leader', null, 'moment ' || moment_id, moment_id, rider_role, null, null, null,
        wkt_segment(x_m, y_m, bx, by_)
    from badge

    union all

    select
        'badge', null, 'moment ' || moment_id, moment_id, rider_role, moment_id::varchar,
        bx, by_, wkt_point(bx, by_)
    from badge

    union all

    -- the callout text next to the badges: one line per moment, stacked downwards
    select
        'callout',
        case text_anchor when 'start' then 'right' else 'left' end,
        'moment ' || moment_id, moment_id, rider_role, moment_id || ' · ' || headline,
        b.x_m + b.badge_dx_m + b.text_dx_m,
        b.y_m + b.badge_dy_m + b.text_dy_m - b.j * p.callout_line_px * p.m_per_px,
        wkt_point(
            b.x_m + b.badge_dx_m + b.text_dx_m,
            b.y_m + b.badge_dy_m + b.text_dy_m - b.j * p.callout_line_px * p.m_per_px
        )
    from badge as b, params as p
)

select
    layer,
    align,
    item,
    moment_id,
    role,
    label,
    round(x, 1) as x_m,
    round(y, 1) as y_m,
    geometry
from features
order by layer, item;
