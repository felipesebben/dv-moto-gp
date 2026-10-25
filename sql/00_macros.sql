-- Geometry helpers for the Tableau canvases (map, race band, locator).
-- A canvas is drawn on a flat x/y plane (metres, or poster px for the race band) and handed to
-- Tableau as fake geography placed on the equator at 0°, 0°: x becomes longitude and y latitude
-- through the inverse Web Mercator projection, so Tableau's map draws the plane at one uniform
-- scale and every map layer stays locked to the others. Each canvas unit becomes 100 m on the
-- fake globe, so a sheet shows it at a comfortable zoom level instead of street level (Tableau
-- caps how far a map zooms in); Mercator undoes the latitude formula exactly, so shapes stay
-- true at any size. Shapes are WKT strings here; publish casts the `geo_*` columns to Tableau's
-- spatial type.
create or replace macro canvas_lon(x) as degrees(x * 100 / 6378137.0);
create or replace macro canvas_lat(y) as degrees(2 * atan(exp(y * 100 / 6378137.0)) - pi() / 2);
create or replace macro wkt_xy(x, y) as format('{:.9f} {:.9f}', canvas_lon(x), canvas_lat(y));
create or replace macro wkt_point(x, y) as 'POINT(' || wkt_xy(x, y) || ')';
create or replace macro wkt_segment(x0, y0, x1, y1) as
    'LINESTRING(' || wkt_xy(x0, y0) || ', ' || wkt_xy(x1, y1) || ')';
create or replace macro ordinal(n) as
    n || case when n % 100 in (11, 12, 13) then 'th'
              when n % 10 = 1 then 'st' when n % 10 = 2 then 'nd' when n % 10 = 3 then 'rd'
              else 'th' end;
-- The custom Tableau shape a mark uses: the file name, without .png, in design/tableau/shapes/
-- (made by design/tableau/tools/make_shapes.py). Shapes carry their own fill, ring and number,
-- because Tableau colours a shape mark with one colour and draws no border on it.
create or replace macro shape_name(layer, role, label) as
    case layer when 'badge' then 'badge_' || role || '_' || label
               when 'rider_dot' then 'dot_' || role end;
