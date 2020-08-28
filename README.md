# Evaluate localization results against ground truth

This repository gives un handy tool to evaluate localization results against ground truth. The localisation results should respect PLOC-ROS message format.

## Prerequities

Create a virtual environment to use python2 within the working directory of your choice

`virtualenv -p /home/username/opt/python-2.7.15/bin/python ve_dev`

`source ve_dev/bin/activate`

`pip install -r requirements.txt`

## Input

This python script take a rosbag containing PLOC messages and evaluate the localisation results against the ground truth using the metrics defined in the **data_paper**

* The ground truth folder should contain :
   * Definition of reference points and enclosing volumes (xml file) as given in the ground truth directory of the **Zenodo Repository** for each scenario
   * Timestamps of testing person passages on reference points and enclosing volumes (txt file) as given in the ground truth directory of the **Zenodo Repository** for each scenario
   * Images (png files) and definition (xml file) of building floors as given in the maps directory of the **Zenodo Repository**
* The bag file should contain the localization results in PLOC format :
```
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
```

## Usage

```#bash
./PLOC_plot_from_xml_rosbag.py -b /path/to/bag.bag -g /path/to/ground_truth_folder -s ref|eval -f png|pdf|svg -i true/false [-d]
```

    * -b or --bagpath, path to bag to evaluate (with ploc message inside hehe)
    * -g or --gtdirectory, path to ground truth files
    * -s or --scenario, to choose the right scenario to evaluate {eval/ref}
    * -f or --format, to choose the ouput graph file format, e.g. 'png', 'pdf', 'svg', ...
    * -i or --init, boolean to choose if evaluation must be done as an initialisation point has been given or not
    * -d or --display, to display graph at runtime (optional)

 ## Output
 This script will output several files :
 * KML files for vizaulisation using Google earth or other Maps application :
   * one global kml containing the global PLOC path and also points and enclosing volumes
   * one kml for each level of the building displaying the floor map and the localization points which are attached to this floor, using the `level` field of the PLOC message
* Image files :
   * Bag_filename_Altitude displaying estimated altitude along time versus ground truth altitude at stationnary points
   * Bag_filename_CEP displaying CEP criterias (CEPH75 and CEPV75) respect to stationnary points
   * Bag_filename_Deplacement displaying estimated displacement status of the testing person along time versus ground truth (when it is known, that is at reference points)
   * Bag_filename_Deplacement displaying estimated indoor/outdoor status along time versus ground truth (when it is known, that is at reference points or enclosing volumes)
   * Bag_filename_orientation displaying estimated orientation along time versus ground truth (when it is known, that is at refernce points when there is an imposed orientation)
   * Bag_filename_orientation_erreur displaying orientation error with respect to ground truth stationnary points with imposed orientation
   * Bag_filename_topologie displaying topological criteria for the different enclosing volumes
   * Bag_filename_WGS displaying the WGS trace in a matplotlib format using distinct colors for each estimated level
* txt file which contains all the metrics defined in the **data_paper**
   * CEP criteria for each stationnary points in the horizontal and vertical plane
   * Global CEPH75 which is the mean of each CEP75 criteria obtained for each stationnary point in horizontal plane
   * Global CEPV75 which is the mean of each CEP75 criteria obtained for each statoionnary point in vertical plane
   * Topological criteria for each enclosing volumes
   * Mean orientation error on stationnary points with imposed orientations
