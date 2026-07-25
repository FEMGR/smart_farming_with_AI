WITH latest_plant_growth AS (
    SELECT DISTINCT ON (pg.plant_id)
        pg.plant_id,
        pg.height_cm::float AS height_cm,
        pg.stage AS growth_stage
    FROM plant_growth pg
    ORDER BY pg.plant_id, pg.recorded_at DESC, pg.id DESC
),
latest_growth_snapshot AS (
    SELECT DISTINCT ON (gs.plant_id)
        gs.plant_id,
        gs.height_cm::float AS height_cm,
        gs.stage AS growth_stage
    FROM growth_snapshots gs
    ORDER BY gs.plant_id, gs.recorded_date DESC, gs.id DESC
)
SELECT
    p.user_id,
    p.id AS plant_id,
    p.location_id,
    p.species_id,
    p.name AS plant_name,
    COALESCE(NULLIF(p.scientific_name, ''), c.scientific_name, p.name) AS scientific_name,
    p.last_watered::timestamp AS last_watered,
    COALESCE(p.watering_interval_days, c.watering_interval_days) AS watering_interval_days,
    c.recommended_soil,
    c.life_cycle,
    l.environment_type,
    l.latitude::float AS latitude,
    l.longitude::float AS longitude,
    CASE
        WHEN p.planting_date IS NULL THEN NULL
        ELSE (CURRENT_DATE - p.planting_date)::integer
    END AS plant_age_days,
    COALESCE(lgs.height_cm, lpg.height_cm) AS height_cm,
    COALESCE(lgs.growth_stage, lpg.growth_stage) AS growth_stage,
    c.propagation_method,
    c.pest_susceptibility,
    c.sunlight_requirement AS recommended_sunlight,
    p.use_sensor AS is_sensor_enabled
FROM plants p
LEFT JOIN plant_species c
    ON p.species_id = c.id
LEFT JOIN locations l
    ON p.location_id = l.id
LEFT JOIN latest_growth_snapshot lgs
    ON p.id = lgs.plant_id
LEFT JOIN latest_plant_growth lpg
    ON p.id = lpg.plant_id
