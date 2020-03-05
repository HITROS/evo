import sys
import rosbag
import rospy
import glob
import math

def sort_bags(properties):
    return properties[1]

def merge_bags(output_name, folders, split_interval_length):
    bag_properties = []
    
    allowed_interval_offset = 5 #Offset in seconds which is allowed between two bags
    
    output_start_time = -1
    output_end_time = -1
    #Check all subdirectories of folder to find all rosbags
    for folder in folders:
        files = glob.glob(folder+"*.bag")
        #List all bags
        for file in files:
            #Check Timestamps and list start and end time
            print(file)
            with rosbag.Bag(file, 'r') as bag:
                if(bag.get_start_time() < output_start_time or output_start_time==-1):
                    output_start_time = bag.get_start_time()
                if(bag.get_end_time() > output_end_time or output_end_time==-1):
                    output_end_time = bag.get_end_time()
                #Save name, start, end and duration of current bag
                bag_properties.append((file, bag.get_start_time(), bag.get_end_time()))

    #Error detection
    if(output_start_time==-1 or output_end_time==-1):
        print("No rosbag found")
        return False

    #Initialize Intervals
    number_of_intervals = math.ceil((output_end_time-output_start_time)/float(split_interval_length))
    bag_intervals = []
    for i in range(int(number_of_intervals)):
        bag_intervals.append([])


    #Sort all bags by starttime
    bag_properties.sort(key=sort_bags)

    #Identify overlapping bags
    for idx in range(1,len(bag_properties)):
        start = bag_properties[idx][1]
        end = bag_properties[idx][2]
        interval_start = int(math.floor((start-output_start_time)/float(split_interval_length)))
        interval_end = int(math.floor((end-output_start_time)/float(split_interval_length)))
        if interval_start!=interval_end:
            bag_intervals[interval_start].append(bag_properties[idx])
            bag_intervals[interval_end].append(bag_properties[idx])
        else:
            bag_intervals[interval_start].append(bag_properties[idx])

    #Output resulting numver of intervals
    print(str(len(bag_intervals)) +" intervals have been found in folders:")
    for idx, interval in enumerate(bag_intervals):
        print("Interval "+str(idx)+":")
        for bag in interval:
            print(bag[0])

    #Open rosbags with intersecting time intervals
    for idx,interval in enumerate(bag_intervals):
        #Output some useful parameters on the measurement series
        duration = interval[-1][2]-interval[0][1]
        print("Generating new bag in time interval from " + str(interval[-1][2]) + "s to " + str(interval[0][1])) + "s"
        print("the duration will be: " + str(duration) + " seconds")
        print("Generating: "+output_name+"_"+str(idx)+".bag")
        with rosbag.Bag(output_name+"_"+str(idx)+".bag", 'w') as out_bag:
            #Now process all rosbag in the right order and write the recorded messages into the new bag
            for inputbag in interval:
                print("processing "+inputbag[0]+"...")
                with rosbag.Bag(inputbag[0], 'r') as in_bag:
                    for topic, msg, t in in_bag.read_messages():
                        lower_bound = float(idx*float(split_interval_length))
                        upper_bound = float((idx+1)*float(split_interval_length))

                        if (t.to_sec()-output_start_time)>=lower_bound and (t.to_sec()-output_start_time)<upper_bound:
                            out_bag.write(topic, msg, t)
    

#Prepare input data
output_name = sys.argv[1]
time_interval = float(sys.argv[2])
input_folder = []

for i in range (3,len(sys.argv)):
    input_folder.append(sys.argv[i])
    
print("Try to merge all rosbags in the following folders...")
print(input_folder)

if(merge_bags(output_name, input_folder, time_interval)):
    print("Success: New Rosbag has successfully been generated as: "+ output_name)
else:
    print("FAILED: New Rosbag could not be generated!")
