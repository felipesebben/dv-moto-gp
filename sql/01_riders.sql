-- One row per rider. `role` drives the highlighting on the poster (everyone else is grey).
create or replace table poster.riders as
select
    rider_number,
    first_name || ' ' || surname as rider_name,
    surname,
    nation,
    team,
    motorcycle,
    position as final_position,
    status,
    case rider_number
        when getvariable('protagonist') then 'protagonist'
        when getvariable('rival') then 'rival'
        else 'other'
    end as role
from stg_classification;
