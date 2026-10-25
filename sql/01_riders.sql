-- One row per rider. `role` drives the highlighting on the poster (everyone else is grey).
-- `in_chart`: the positions chart shows the six finishers in front only (design standards §5).
create or replace table poster.riders as
select
    rider_number,
    first_name || ' ' || surname as rider_name,
    surname,
    array_to_string(
        list_transform(string_split(lower(surname), ' '), lambda w: upper(w[1]) || w[2:]), ' '
    ) as display_name,
    nation,
    team,
    motorcycle,
    position as final_position,
    status,
    case rider_number
        when getvariable('protagonist') then 'protagonist'
        when getvariable('rival') then 'rival'
        else 'other'
    end as role,
    coalesce(position <= 6, false) as in_chart
from stg_classification;
