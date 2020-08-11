# Message from PLOC DGA String
Header header

# Sentence type
string message_id
# Id of localization system, proper to MALIN challenge
uint8 system_id

# Date UTC, ddmmyy
uint32 utc_date
# Time UTC, hhmmss.sss
float64 utc_time

# Latitude in degrees minutes, ddmm.mmmmmmm
float64 lat
# Direction of latitude, N or S
string lat_dir

# Longitude in degrees minutes, dddmm.mmmmmmm
float64 lon
# Direction of longitude, E or O
string lon_dir

# Altitude WGS84 MSL in meter, mmmm.mm
float32 alt

# Floor level, level 0 is first time in indoor conditions, mm
int8 level

# horizontal velocity m/s, v.vv
float32 speed

# Information on the moving state of the agent ("S": Stationnary or "D": Displacement)
string moving_state
# Infrmation on the environment of the agent ("I": Indoor or "O": Outdoor)
string environment_state

# Heading to True North, degrees, ddd.dd
float32 heading

# Pose mode A=autonomous, G=GNSS, E=Dead Reckoning
string pose_mode

# Standard deviation of latitude in meters, ppp.pp
float32 lat_std_dev
# Standard deviation of longitude in meters, pp.pp
float32 lon_std_dev
# Standard deviation of altitude in meters, pp.pp
float32 alt_std_dev

