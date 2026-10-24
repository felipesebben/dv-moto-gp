-- One row of event + circuit facts for the poster's subtitle and circuit card.
create or replace table poster.event as
select
    *,
    right_corners + left_corners as corners
from stg_event;
