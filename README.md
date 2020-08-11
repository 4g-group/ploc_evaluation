# Plot PLOC messages against ground truth directly from rosbag

* To that end create a virtual environment to use python3

`python3 -m venv ve_dev`

`source ve_dev/bin/activate`

`pip install -r requirements.txt`

The installation from pip for rospy_message_converter is unsupported.
clone and build of [rospy_message_converter](https://github.com/uos/rospy_message_converter) is needed.

ROS BUG FIX:
replace "Cryptodome" by "Crypto" in /opt/ros/melodic/lib/python3/dist-packages/rosbag/bag.py l.53 and 54

* Launch the script to vizualize either save graphs

`python3 ./PLOC_plot_from_xml_rosbag.py -b /path/to/bag.bag -g /path/to/ground_truth_folder -s ref|eval -f Figureformat [-d]`

    * -b or --bagpath, path to bag to evaluate (with ploc message inside hehe)
    * -g or --gtdirectory, path to ground truth files
    * -s or --scenario, to choose the right scenario to evaluate
    * -f or --format, to choose the ouput graph file format, e.g. 'png', 'pdf', 'svg', ...
    * -d or --display, to display graph at runtime (optional)
