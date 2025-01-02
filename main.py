#Kylie Taylor Student ID: 001329025
#region Imports

from enum import Enum
import sys
import tkinter as tk
from tkinter import ttk
import time
import copy
#endregion

#region GLOBALS

#PROGRAM FLOW:
# 1. create a Package object for each package in the list, add them to either the hub_packages group or the delayed_packages group based off of identifying characteristics
# 2. create a Driver for each driver
# 3. create a Truck for each truck
# 4. load the Superviser_GUI
# 5. when a arrow button is pressed advance the current time by an appropiate amount of time (in 1, 5, 60 minute intervals)
# 6. Each minute run the following checks:
#     Truck logic
#     a. Check if any trucks are at the hub and assign a driver if one is available
#     b. Calculate a route for any trucks at the hub using a nearest neighbor algorithm in Truck.calculate_route
#     c. Load packages onto the truck, removing them from the hub list
#     d. Mark trucks that have a route and are loaded as en_route
#     c. For trucks en_route check if it is time for their next package delivery. 
#         i. find all the packages at the current en_route_node and deliver them


#     Delayed Package Logic:
#     a. Check if any packages that were delayed are ready to be moved into the hub_packages list and move them to the hub packages list
#7. Once all packages have been delivered note the time and end the day


#using 24 hour time, no EOD time given in instructions, assuming 23:59 as end of day

EOD_value = 1439
truck_size_limit = 16
truck_speed = 18
num_drivers = 2
num_trucks = 3
current_time = 8 * 60 #day starts at 8
# selected_package = None
last_package_delivery_time = None

truck_list = []
unassigned_driver_list = []


#these will be hash_tables but because I can't use multiple files to import the class the declarations are None and assignment is done in main()
all_packages = None
hub_packages = None
initial_hub_packages = None
initial_delayed_packages =  None
adj_table = None
delivered_packages = None




address_update_list = [[9, "410 S. State St.", "Salt Lake City", "UT", 84111]] #not a full solution, good enough for this project 



# manually generating the UID since there is only the one set of grouped packages for this assignment, a proper implmentation would rely on the UUID being created when the packages are entered into the system or when the grouping is created
# a better solution would also be using UUIDs not a simple hash like this as its not garunteed unique but there are only 63 known SHA1 collisions https://stackoverflow.com/questions/47601592/safest-way-to-generate-a-unique-hash-in-python
s_instruction = hash("special group")
delayed_UID = hash("delayed")

# Package ID, Address, City, State, Zip, Delivery Deadline, Weight, Group UID, Delayed time (in minutes), Required Truck ID, special_instruction_note
# special instructions implemented via Group UID, delayed reason, delayed time, and required truck id

package_file = [
    [1,   "195 W Oakland Ave",                          "Salt Lake City"  ,         "UT",   84115,   "10:30 AM",      21,    None,           None,              None,                 None,   None                                                            ],
    [2,   "2530 S 500 E",                               "Salt Lake City"  ,         "UT",   84106,   "EOD",           44,    None,           None,              None,                 None,   None                                                            ],
    [3,   "233 Canyon Rd",                              "Salt Lake City"  ,         "UT",   84103,   "EOD",           2,     None,           None,              None,                 2   ,   "Can only be on truck 2"                                        ],
    [4,   "380 W 2880 S",                               "Salt Lake City"  ,         "UT",   84115,   "EOD",           4,     None,           None,              None,                 None,   None                                                            ],
    [5,   "410 S State St",                             "Salt Lake City"  ,         "UT",   84111,   "EOD",           5,     None,           None,              None,                 None,   None                                                            ],
    [6,   "3060 Lester St",                             "West Valley City",         "UT",   84119,   "10:30 AM",      88,    delayed_UID,    "FLIGHT DELAYED",  ((9 * 60) + 5),       None,   "Delayed on flight---will not arrive to depot until 9:05 am"    ],#NOTE delayed packages will not be considered for route selection unless current time > delayed time   
    [7,   "1330 2100 S",                                "Salt Lake City"  ,         "UT",   84106,   "EOD",           8,     None,           None,              None,                 None,   None                                                            ],
    [8,   "300 State St",                               "Salt Lake City"  ,         "UT",   84103,   "EOD",           9,     None,           None,              None,                 None,   None                                                            ],
    [9,   "300 State St",                               "Salt Lake City"  ,         "UT",   84103,   "EOD",           2,     delayed_UID,    "WRONG ADDRESS",   ((10 * 60) + 20),     None,   "Wrong address listed"                                          ],#NOTE: incorrect addresses will be assigned a negative group UID to indicate they can't be loaded (could be improved to allow loading so correction can occur in route)                                 
    [10,  "600 E 900 South",                            "Salt Lake City"  ,         "UT",   84105,   "EOD",           1,     None,           None,              None,                 None,   None                                                            ],
    [11,  "2600 Taylorsville Blvd",                     "Salt Lake City"  ,         "UT",   84118,   "EOD",           1,     None,           None,              None,                 None,   None                                                            ],
    [12,  "3575 W Valley Central Station bus Loop",     "West Valley City",         "UT",   84119,   "EOD",           1,     None,           None,              None,                 None,   None                                                            ],
    [13,  "2010 W 500 S",                               "Salt Lake City",           "UT",   84104,   "10:30 AM",      2,     s_instruction,  None,              None,                 None,   None                                                            ],
    [14,  "4300 S 1300 E",                              "Millcreek",                "UT",   84117,   "10:30 AM",      88,    s_instruction,  None,              None,                 None,   "Must be delivered with 15, 19"                                 ],
    [15,  "4580 S 2300 E",                              "Holladay",                 "UT",   84117,   "9:00 AM",       4,     s_instruction,  None,              None,                 None,   None                                                            ],
    [16,  "4580 S 2300 E",                              "Holladay",                 "UT",   84117,   "10:30 AM",      88,    s_instruction,  None,              None,                 None,   "Must be delivered with 13, 19"                                 ],
    [17,  "3148 S 1100 W",                              "Salt Lake City",           "UT",   84119,   "EOD",           2,     None,           None,              None,                 None,   None                                                            ],
    [18,  "1488 4800 S",                                "Salt Lake City",           "UT",   84123,   "EOD",           6,     None,           None,              None,                 2   ,   "Can only be on truck 2"                                        ],
    [19,  "177 W Price Ave",                            "Salt Lake City",           "UT",   84115,   "EOD",           37,    s_instruction,  None,              None,                 None,   None                                                            ],
    [20,  "3595 Main St",                               "Salt Lake City",           "UT",   84115,   "10:30 AM",      37,    s_instruction,  None,              None,                 None,   "Must be delivered with 13, 15"                                 ],
    [21,  "3595 Main St",                               "Salt Lake City",           "UT",   84115,   "EOD",           3,     None,           None,              None,                 None,   None                                                            ],
    [22,  "6351 South 900 East",                        "Murray",                   "UT",   84121,   "EOD",           2,     None,           None,              None,                 None,   None                                                            ],
    [23,  "5100 South 2700 West",                       "Salt Lake City",           "UT",   84118,   "EOD",           5,     None,           None,              None,                 None,   None                                                            ],
    [24,  "5025 State St",                              "Murray",                   "UT",   84107,   "EOD",           7,     None,           None,              None,                 None,   None                                                            ],
    [25,  "5383 South 900 East #104",                   "Salt Lake City",           "UT",   84117,   "10:30 AM",      7,     delayed_UID,    "FLIGHT DELAYED",  ((9 * 60) + 5),       None,   "Delayed on flight---will not arrive to depot until 9:05 am"    ],
    [26,  "5383 South 900 East #104",                   "Salt Lake City",           "UT",   84117,   "EOD",           25,    None,           None,              None,                 None,   None                                                            ],
    [27,  "1060 Dalton Ave S",                          "Salt Lake City",           "UT",   84104,   "EOD",           5,     None,           None,              None,                 None,   None                                                            ],
    [28,  "2835 Main St",                               "Salt Lake City",           "UT",   84115,   "EOD",           7,     delayed_UID,    "FLIGHT DELAYED",  ((9 * 60) + 5),       None,   "Delayed on flight---will not arrive to depot until 9:05 am"    ],
    [29,  "1330 2100 S",                                "Salt Lake City",           "UT",   84106,   "10:30 AM",      2,     None,           None,              None,                 None,   None                                                            ],
    [30,  "300 State St",                               "Salt Lake City",           "UT",   84103,   "10:30 AM",      1,     None,           None,              None,                 None,   None                                                            ],
    [31,  "3365 S 900 W",                               "Salt Lake City",           "UT",   84119,   "10:30 AM",      1,     None,           None,              None,                 None,   None                                                            ],
    [32,  "3365 S 900 W",                               "Salt Lake City",           "UT",   84119,   "EOD",           1,     delayed_UID,    "FLIGHT DELAYED",  ((9 * 60) + 5),       None,   "Delayed on flight---will not arrive to depot until 9:05 am"    ],
    [33,  "2530 S 500 E",                               "Salt Lake City",           "UT",   84106,   "EOD",           1,     None,           None,              None,                 None,   None                                                            ],
    [34,  "4580 S 2300 E",                              "Holladay",                 "UT",   84117,   "10:30 AM",      2,     None,           None,              None,                 None,   None                                                            ],
    [35,  "1060 Dalton Ave S",                          "Salt Lake City",           "UT",   84104,   "EOD",           88,    None,           None,              None,                 None,   None                                                            ],
    [36,  "2300 Parkway Blvd",                          "West Valley City",         "UT",   84119,   "EOD",           88,    None,           None,              None,                 2   ,   "Can only be on truck 2"                                        ],
    [37,  "410 S State St",                             "Salt Lake City",           "UT",   84111,   "10:30 AM",      2,     None,           None,              None,                 None,   None                                                            ],
    [38,  "410 S State St",                             "Salt Lake City",           "UT",   84111,   "EOD",           9,     None,           None,              None,                 2   ,   "Can only be on truck 2"                                        ],
    [39,  "2010 W 500 S",                               "Salt Lake City",           "UT",   84104,   "EOD",           9,     None,           None,              None,                 None,   None                                                            ],
    [40,  "380 W 2880 S",                               "Salt Lake City",           "UT",   84115,   "10:30 AM",      45,    None,           None,              None,                 None,   None                                                            ] 
]      
      
#index of the address should line up with the index of the matrix      
#ie HUB is 0, distance_table[0][1] would be the distance from the hub to 1060 Dalton Ave S (84104)

distance_addresses = [
"HUB",
"1060 Dalton Ave S (84104)",
"1330 2100 S (84106)",
"1488 4800 S (84123)",
"177 W Price Ave (84115)",
"195 W Oakland Ave (84115)",
"2010 W 500 S (84104)",
"2300 Parkway Blvd (84119)",
"233 Canyon Rd (84103)",
"2530 S 500 E (84106)",
"2600 Taylorsville Blvd (84118)",
"2835 Main St (84115)",
"300 State St (84103)",
"3060 Lester St (84119)",
"3148 S 1100 W (84119)",
"3365 S 900 W (84119)",
"3575 W Valley Central Station bus Loop (84119)",
"3595 Main St (84115)",
"380 W 2880 S (84115)",
"410 S State St (84111)",
"4300 S 1300 E (84117)",
"4580 S 2300 E (84117)",
"5025 State St (84107)",
"5100 South 2700 West (84118)",
"5383 South 900 East #104 (84117)",
"600 E 900 South (84105)",
"6351 South 900 East (84121)"
]



#I could halve the amount of data stored in the distance table by always looking up the distance value of the greatest node first distance_table[largest][smallest] but I decided not when I was converting the distance table from the excel file

distance_table = [
[0,7.2,3.8,11,2.2,3.5,10.9,8.6,7.6,2.8,6.4,3.2,7.6,5.2,4.4,3.7,7.6,2,3.6,6.5,1.9,3.4,2.4,6.4,2.4,5,3.6],
[7.2,0,7.1,6.4,6,4.8,1.6,2.8,4.8,6.3,7.3,5.3,4.8,3,4.6,4.5,7.4,6,5,4.8,9.5,10.9,8.3,6.9,10,4.4,13],
[3.8,7.1,0,9.2,4.4,2.8,8.6,6.3,5.3,1.6,10.4,3,5.3,6.5,5.6,5.8,5.7,4.1,3.6,4.3,3.3,5,6.1,9.7,6.1,2.8,7.4],
[11,6.4,9.2,0,5.6,6.9,8.6,4,11.1,7.3,1,6.4,11.1,3.9,4.3,4.4,7.2,5.3,6,10.6,5.9,7.4,4.7,0.6,6.4,10.1,10.1],
[2.2,6,4.4,5.6,0,1.9,7.9,5.1,7.5,2.6,6.5,1.5,7.5,3.2,2.4,2.7,1.4,0.5,1.7,6.5,3.2,5.2,2.5,6,4.2,5.4,5.5],
[3.5,4.8,2.8,6.9,1.9,0,6.3,4.3,4.5,1.5,8.7,0.8,4.5,3.9,3,3.8,5.7,1.9,1.1,3.5,4.9,6.9,4.2,9,5.9,3.5,7.2],
[10.9,1.6,8.6,8.6,7.9,6.3,0,4,4.2,8,8.6,6.9,4.2,4.2,8,5.8,7.2,7.7,6.6,3.2,11.2,12.7,10,8.2,11.7,5.1,14.2],
[8.6,2.8,6.3,4,5.1,4.3,4,0,7.7,9.3,4.6,4.8,7.7,1.6,3.3,3.4,3.1,5.1,4.6,6.7,8.1,10.4,7.8,4.2,9.5,6.2,10.7],
[7.6,4.8,5.3,11.1,7.5,4.5,4.2,7.7,0,4.8,11.9,4.7,0.6,7.6,7.8,6.6,7.2,5.9,5.4,1,8.5,10.3,7.8,11.5,9.5,2.8,14.1],
[2.8,6.3,1.6,7.3,2.6,1.5,8,9.3,4.8,0,9.4,1.1,5.1,4.6,3.7,4,6.7,2.3,1.8,4.1,3.8,5.8,4.3,7.8,4.8,3.2,6],
[6.4,7.3,10.4,1,6.5,8.7,8.6,4.6,11.9,9.4,0,7.3,12,4.9,5.2,5.4,8.1,6.2,6.9,11.5,6.9,8.3,4.1,0.4,4.9,11,6.8],
[3.2,5.3,3,6.4,1.5,0.8,6.9,4.8,4.7,1.1,7.3,0,4.7,3.5,2.6,2.9,6.3,1.2,1,3.7,4.1,6.2,3.4,6.9,5.2,3.7,6.4],
[7.6,4.8,5.3,11.1,7.5,4.5,4.2,7.7,0.6,5.1,12,4.7,0,7.3,7.8,6.6,7.2,5.9,5.4,1,8.5,10.3,7.8,11.5,9.5,2.8,14.1],
[5.2,3,6.5,3.9,3.2,3.9,4.2,1.6,7.6,4.6,4.9,3.5,7.3,0,1.3,1.5,4,3.2,3,6.9,6.2,8.2,5.5,4.4,7.2,6.4,10.5],
[4.4,4.6,5.6,4.3,2.4,3,8,3.3,7.8,3.7,5.2,2.6,7.8,1.3,0,0.6,6.4,2.4,2.2,6.8,5.3,7.4,4.6,4.8,6.3,6.5,8.8],
[3.7,4.5,5.8,4.4,2.7,3.8,5.8,3.4,6.6,4,5.4,2.9,6.6,1.5,0.6,0,5.6,1.6,1.7,6.4,4.9,6.9,4.2,5.6,5.9,5.7,8.4],
[7.6,7.4,5.7,7.2,1.4,5.7,7.2,3.1,7.2,6.7,8.1,6.3,7.2,4,6.4,5.6,0,7.1,6.1,7.2,10.6,12,9.4,7.5,11.1,6.2,13.6],
[2,6,4.1,5.3,0.5,1.9,7.7,5.1,5.9,2.3,6.2,1.2,5.9,3.2,2.4,1.6,7.1,0,1.6,4.9,3,5,2.3,5.5,4,5.1,5.2],
[3.6,5,3.6,6,1.7,1.1,6.6,4.6,5.4,1.8,6.9,1,5.4,3,2.2,1.7,6.1,1.6,0,4.4,4.6,6.6,3.9,6.5,5.6,4.3,6.9],
[6.5,4.8,4.3,10.6,6.5,3.5,3.2,6.7,1,4.1,11.5,3.7,1,6.9,6.8,6.4,7.2,4.9,4.4,0,7.5,9.3,6.8,11.4,8.5,1.8,13.1],
[1.9,9.5,3.3,5.9,3.2,4.9,11.2,8.1,8.5,3.8,6.9,4.1,8.5,6.2,5.3,4.9,10.6,3,4.6,7.5,0,2,2.9,6.4,2.8,6,4.1],
[3.4,10.9,5,7.4,5.2,6.9,12.7,10.4,10.3,5.8,8.3,6.2,10.3,8.2,7.4,6.9,12,5,6.6,9.3,2,0,4.4,7.9,3.4,7.9,4.7],
[2.4,8.3,6.1,4.7,2.5,4.2,10,7.8,7.8,4.3,4.1,3.4,7.8,5.5,4.6,4.2,9.4,2.3,3.9,6.8,2.9,4.4,0,4.5,1.7,6.8,3.1],
[6.4,6.9,9.7,0.6,6,9,8.2,4.2,11.5,7.8,0.4,6.9,11.5,4.4,4.8,5.6,7.5,5.5,6.5,11.4,6.4,7.9,4.5,0,5.4,10.6,7.8],
[2.4,10,6.1,6.4,4.2,5.9,11.7,9.5,9.5,4.8,4.9,5.2,9.5,7.2,6.3,5.9,11.1,4,5.6,8.5,2.8,3.4,1.7,5.4,0,7,1.3],
[5,4.4,2.8,10.1,5.4,3.5,5.1,6.2,2.8,3.2,11,3.7,2.8,6.4,6.5,5.7,6.2,5.1,4.3,1.8,6,7.9,6.8,10.6,7,0,8.3],
[3.6,13,7.4,10.1,5.5,7.2,14.2,10.7,14.1,6,6.8,6.4,14.1,10.5,8.8,8.4,13.6,5.2,6.9,13.1,4.1,4.7,3.1,7.8,1.3,8.3,0]
]

class Delivery_Status(Enum):
    AT_HUB = 1
    EN_ROUTE = 2
    DELIVERED = 3
    RETURNING_TO_HUB = 4
    DELAYED = 5    

    def __str__(self):
        return str(self.name)

#endregion

#region Supervisor GUI
#A lot more work could be done on the GUI to improve it, individual panels or frames could be redrawn rather than refreshing the whole thing when advancing the time
class Superviser_GUI(tk.Frame):
    def __init__(self, main=None):
        super().__init__(main)
        main.geometry("1200x800")
        main.title("WGUPS Routing")
        self.main = main
        self.frame = tk.Frame(self.main)
        self.selected_package = None
        self.truck_label_frames = [None for x in range(num_trucks)]
        self.truck_fields =[None for x in range(num_trucks)]
        self.selected_hour = tk.StringVar(self.main)
        self.selected_minute = tk.StringVar(self.main)
        self.selected_meridian = tk.StringVar(self.main)
        self.selected_hour.set('8')
        self.selected_minute.set('00')
        self.selected_meridian.set('AM')

        self.draw_full_frame()
        self.pack()
        pass

    def refresh(self):
        #TODO: Refactor this so it only redraws the necessary items instead of the top level frame
        self.frame.destroy()
        self.frame = tk.Frame(self.main)
        self.draw_full_frame()
        
    def draw_full_frame(self):
        self.layout_panels()
        self.layout_control_panel()
        self.layout_truck_panel()
        self.layout_package_list_panel()
        self.layout_selected_package_panel()
        self.layout_summary_panel()
        self.frame.pack(fill=tk.BOTH, expand=True)

    def refresh_selected_package_panel(self):
        self.selected_frame.destroy()
        self.layout_selected_package_panel()

    def refresh_all_truck_fields(self):
        for t in range(num_trucks):
            self.truck_fields[t].destroy()
            truck_text_frame = tk.Frame(self.truck_label_frames[t])
            self.layout_truck_fields(truck_text_frame,truck_list[t])
            self.truck_fields[t] = truck_text_frame

    # def a_t(self,adv_amount):
    #     advance_time(adv_amount)
    #     self.refresh()
    #     return
    
    def go_to_selected_time(self):
        if self.selected_meridian.get() == 'AM' and  self.selected_hour.get() == '12':
            selected_time = 0
        else:
            selected_time = (int(self.selected_hour.get()) * 60)
        selected_time += int(self.selected_minute.get())
        if self.selected_meridian.get() == 'PM' and self.selected_hour.get() != '12':
            selected_time += 720

        if selected_time < current_time:
            restart_day(0)
            if self.selected_package is not None:
                self.selected_package = all_packages[self.selected_package.id]
            

        advance_time(selected_time - current_time)
        self.refresh()


    def get_selected_time(self):
        return
    def layout_panels(self):
        self.control_panel = tk.Frame(self.frame)
        self.truck_panel = tk.Frame(self.frame)
        self.all_packages_panel = tk.Frame(self.frame)
        selected_and_summary_panel = tk.Frame(self.frame)
        self.summary_panel = tk.Frame(selected_and_summary_panel)
        self.selected_package_panel = tk.Frame(selected_and_summary_panel)

        self.control_panel.pack(side=tk.BOTTOM, fill=tk.X)
        self.all_packages_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.selected_package_panel.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.summary_panel.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
        selected_and_summary_panel.pack(side=tk.LEFT, expand=False, fill=tk.BOTH, padx=5)
        self.truck_panel.pack(side=tk.LEFT,expand=True, fill=tk.BOTH)
        
        return
    
    def layout_selected_package_panel(self):
        selected_frame = tk.LabelFrame(self.selected_package_panel, text="Selected Package")
        self.selected_package : Package

        fields = []
        package_id_string = "Package ID: "
        package_id_string += str(self.selected_package.id) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=package_id_string))

        address_string = "Address: "
        address_string += str(self.selected_package.delivery_address) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=address_string))

        city_string = "City: "
        city_string += str(self.selected_package.delivery_city) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=city_string))

        state_string = "State: " 
        state_string += str(self.selected_package.delivery_state) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=state_string))

        zip_string = "Zip: " 
        zip_string += str(self.selected_package.delivery_zip) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=zip_string))

        weight_string = "Weight: " 
        weight_string += str(self.selected_package.package_weight) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=weight_string))

        deadline_string = "Delivery Deadline: " 
        deadline_string += convert_timestamp(self.selected_package.delivery_deadline) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=deadline_string))

        status_string = "Status: " 
        status_string += str(self.selected_package.status) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=status_string))

        if self.selected_package is not None:
            if self.selected_package.delivered_time is not None:
                delivery_string = "Delivery Time: " 
                delivery_string += convert_timestamp(self.selected_package.delivered_time)
                fields.append(tk.Label(selected_frame, text=delivery_string))
                
            if self.selected_package.delivery_truck_id is not None:
                delivery_truck_string = "Delivery Truck: "
                delivery_truck_string += str(self.selected_package.delivery_truck_id)
                fields.append(tk.Label(selected_frame, text=delivery_truck_string))

        special_instruction_string = "Special Instruction: " 
        special_instruction_string += str(self.selected_package.special_instruction) if self.selected_package is not None else "None"
        fields.append(tk.Label(selected_frame, text=special_instruction_string, wraplength=180, justify=tk.LEFT))

        row_size = 16
        column_size = 1
        counter = 0
        try:
            for x in range(row_size):
                for y in range(column_size):
                    if counter == len(fields):
                        raise Exception("done")
                    fields[counter].grid(column=y,row=x,sticky=tk.W)
                    fields[counter].columnconfigure(y,weight=1)
                    fields[counter].rowconfigure(x,weight=1)
                    counter += 1
        except Exception as inst:
            if inst.args[0] != "done":
                raise inst

        self.selected_frame = selected_frame
        selected_frame.pack(fill=tk.BOTH,expand=tk.Y)
        return

    def get_selected_package(self,event):
        for i in self.package_scroll_list.curselection():
            self.selected_package = all_packages[i+1]
        self.refresh_selected_package_panel()
        return

    def layout_package_list_panel(self):
        tk.Label(self.all_packages_panel, text="All Packages (Click to Select)", ).pack(anchor=tk.W)  
        all_packages_frame = tk.Scrollbar(self.all_packages_panel)
        self.package_scroll_list = tk.Listbox(self.all_packages_panel, width=25, yscrollcommand=all_packages_frame.set)
        for p in all_packages.keys:
            package : Package = all_packages[p]
            package_str = "ID:%02d " % package.id + " Status: " + str(package.status)
            self.package_scroll_list.insert(tk.END, package_str)
        self.package_scroll_list.bind("<<ListboxSelect>>", self.get_selected_package)
        self.package_scroll_list.pack(side=tk.LEFT, fill=tk.BOTH)
        all_packages_frame.config(command=self.package_scroll_list.yview)
        all_packages_frame.pack(side=tk.LEFT, fill=tk.Y)
        return

    def layout_control_panel(self):
        tk.Label(self.control_panel, text=("Current Time: " + convert_timestamp(current_time))).pack(side=tk.TOP)
        dropdowns = tk.Frame(self.control_panel)

        # tk.Button(buttons, text="refresh",width=15, command=self.refresh).pack(side=tk.LEFT)
        # tk.Button(buttons, text=">",width=15, command=lambda:self.a_t(1)).pack(side=tk.LEFT)
        # tk.Button(buttons, text=">>",width=15, command=lambda:self.a_t(5)).pack(side=tk.LEFT)
        # tk.Button(buttons, text=">>>",width=15, command=lambda:self.a_t(60)).pack(side=tk.LEFT)
        # tk.Button(buttons, text="refresh trucks",width=15, command=lambda:self.refresh_all_truck_fields).pack(side=tk.LEFT)

        

       
        hour_dropdown = ttk.Combobox(dropdowns, width = 5, textvariable=self.selected_hour)
        hour_dropdown['values'] = [str(x) for x in range(1,13)]
        hour_dropdown.pack(side=tk.LEFT)
        # hour_dropdown.current(7)
        def hour_selected(event):
            self.selected_hour.set(hour_dropdown.get())
        hour_dropdown.bind("<<ComboboxSelected>>", hour_selected)

        minute_dropdown = ttk.Combobox(dropdowns, width = 5, textvariable=self.selected_minute, values=[ "%02d" % x for x in range(60)])
        # minute_dropdown['values'] = 
        minute_dropdown.pack(side=tk.LEFT)
        # minute_dropdown.current(0)
        def minute_selected(event):
            self.selected_minute.set(minute_dropdown.get())
        minute_dropdown.bind("<<ComboboxSelected>>", minute_selected)


        meridian_dropdown = ttk.Combobox(dropdowns, width = 5, textvariable=self.selected_meridian)
        meridian_dropdown['values'] = ["AM","PM"]
        meridian_dropdown.pack(side=tk.LEFT)
        # meridian_dropdown.current(0)
        def meridian_selected(event):
            self.selected_meridian.set(meridian_dropdown.get())
        meridian_dropdown.bind("<<ComboboxSelected>>", meridian_selected)
        # def get_selected_time(event):
        #     selected_hour = 

        tk.Button(dropdowns, text="Go", command=lambda:self.go_to_selected_time()).pack(side=tk.LEFT)

        dropdowns.pack(side=tk.TOP)
        return

    def layout_truck_fields(self,truck_field_frame,truck):
        truck_fields = []
        truck : Truck
        # .grid(column=0,row=0,sticky="W",padx=5)

        status_string = "Current Status: "
        status_string += str(truck.status)
        truck_fields.append(tk.Label(truck_field_frame, text=status_string))

        destination_string = "Current Destination: "
        destination_string += str(distance_addresses[truck.en_route_node]) if truck.en_route_node is not None else "None"
        truck_fields.append(tk.Label(truck_field_frame, text=( destination_string)))

        delivery_time_string = "Next Delivery Time: " 
        delivery_time_string += str(convert_timestamp(round(truck.next_delivery_time))) if truck.next_delivery_time is not None else "None"
        truck_fields.append(tk.Label(truck_field_frame, text=delivery_time_string))

        traveled_distance_string = "Total Distance Traveled: "  
        traveled_distance_string += str(round(truck.traveled_distance + truck.current_route_distance,1)) if truck.traveled_distance is not None else "0"
        truck_fields.append(tk.Label(truck_field_frame, text=traveled_distance_string))

        current_route_distance_string = "Current Route Distance Traveled: "
        current_route_distance_string += str(truck.current_route_distance)
        truck_fields.append(tk.Label(truck_field_frame, text=current_route_distance_string))

        driver_string = "Driver Employee ID: "
        driver_string += str(truck.driver.employee_id) if truck.driver is not None else "None"
        truck_fields.append(tk.Label(truck_field_frame, text=driver_string))

        package_count_string = "Current Number of Packages: "
        package_count_string += str(truck_size_limit - truck.remaining_space)
        truck_fields.append(tk.Label(truck_field_frame, text=package_count_string))
        

        rows = 4
        columns = 2
        counter = 0
        try:
            for x in range(rows):
                for y in range(columns):
                    if counter >= len(truck_fields):
                        raise Exception("done")
                    truck_fields[counter].grid(column=y,row=x,sticky="W",padx=5)
                    counter += 1
                    
        except Exception as inst:
            if inst.args[0] != "done":
                raise inst
        truck_field_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y)
        return

    def layout_truck_package_info(self,truck_package_info_frame : tk.Frame,truck):
        
        truck_package_info_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y)
               

        truck_loaded_packages_label_frame = tk.LabelFrame(truck_package_info_frame, text="Loaded Packages")
        # truck_loaded_packages_label_frame.configure(background='white')
        truck_loaded_packages_label_frame.pack(side=tk.LEFT, expand=tk.Y, fill=tk.BOTH)
        
        truck_next_packages_to_be_delivered_label_frame = tk.LabelFrame(truck_package_info_frame, text="Next Packages to be Delivered")
        # truck_next_packages_to_be_delivered.configure(background='white')
        truck_next_packages_to_be_delivered_label_frame.pack(side=tk.RIGHT, expand=tk.Y, fill=tk.BOTH)
        
        truck_loaded_packages_frame = tk.Frame(truck_loaded_packages_label_frame,bg='white')


        truck_next_packages_to_be_delivered_frame = tk.Frame(truck_next_packages_to_be_delivered_label_frame,bg='white')

        packages = []
        for package in truck.get_all_packages():
            package_label = tk.Label(truck_loaded_packages_frame, text=str(package.id),bg='white')
            packages.append(package_label)

        row_size = 2
        column_size = 8
        counter = 0
        try:
            for x in range(row_size):
                for y in range(column_size):
                    if counter == len(packages):
                        raise Exception("done")
                    packages[counter].grid(column=y,row=x,sticky=tk.NSEW)
                    packages[counter].columnconfigure(y,weight=1)
                    packages[counter].rowconfigure(x,weight=1)
                    counter += 1
        except Exception as inst:
            if inst.args[0] != "done":
                raise inst
        truck_loaded_packages_frame.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH,padx=2,pady=(0,5))
        

        if truck.en_route_node is not None and truck.en_route_node != 0:
            next_packages = []
            for package in truck.packages[truck.en_route_node][truck.en_route_node]:
                next_package_str = "ID: " + str(package.id) + " ETA: " + convert_timestamp(package.expected_delivery_time) 
                next_package_label = tk.Label(truck_next_packages_to_be_delivered_frame, text=next_package_str,bg='white')
                next_packages.append(next_package_label)

            row_size = 8
            column_size = 1
            counter = 0
            try:
                for x in range(row_size):
                    for y in range(column_size):
                        if counter == len(next_packages):
                            raise Exception("done")
                        next_packages[counter].grid(column=y,row=x,sticky=tk.NSEW)
                        next_packages[counter].columnconfigure(y,weight=1)
                        next_packages[counter].rowconfigure(x,weight=1)
                        counter += 1
            except Exception as inst:
                if inst.args[0] != "done":
                    raise inst
        truck_next_packages_to_be_delivered_frame.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH,padx=2,pady=(0,5))

        
        return

    def layout_truck_panel(self):
        for t in range(num_trucks):
            # truck_info = tk.Frame(self.truck_panel)
            truck : Truck = truck_list[t]
            truck_label_frame = tk.LabelFrame(self.truck_panel, text=("Truck " + str(t + 1)))
            self.truck_label_frames[t] = truck_label_frame
            #this frame is necessary for single side padding due to how seems pack works with label frames
            pad_frame = tk.Frame(truck_label_frame)
            truck_label_frame.pack(fill=tk.BOTH, expand=tk.Y,padx=5,pady=(0,10))
            

            
            truck_field_frame = tk.Frame(pad_frame)
            self.layout_truck_fields(truck_field_frame,truck)
            self.truck_fields[t] = truck_field_frame
            
            truck_package_info_frame = tk.Frame(pad_frame)
            self.layout_truck_package_info(truck_package_info_frame, truck)

            pad_frame.pack(padx=5,pady=(0,10), fill=tk.BOTH, expand=tk.Y)

        return
            
    def layout_summary_panel(self):
        summary_label_frame = tk.LabelFrame(self.summary_panel,text="Day Summary")
        summary_pad_frame = tk.Frame(summary_label_frame)
        summary_fields = []

        total_distance = 0
        for t in range(num_trucks):
            truck : Truck = truck_list[t]
            total_distance += truck.traveled_distance + truck.current_route_distance
        
        total_distance_string = "Total Distance Traveled: "
        total_distance_string += str(round(total_distance,1))
        summary_fields.append(tk.Label(summary_pad_frame, text=total_distance_string))
        if last_package_delivery_time is not None:
            last_package_delivery_time_string = "All Delivery Completion Time: "
            last_package_delivery_time_string += convert_timestamp(last_package_delivery_time)
            summary_fields.append(tk.Label(summary_pad_frame, text=last_package_delivery_time_string))


        rows = 4
        columns = 1
        counter = 0
        try:
            for x in range(rows):
                for y in range(columns):
                    if counter >= len(summary_fields):
                        raise Exception("done")
                    summary_fields[counter].grid(column=y,row=x,sticky="W",padx=5)
                    counter += 1
                    
        except Exception as inst:
            if inst.args[0] != "done":
                raise inst


        summary_pad_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y, padx=5)
        summary_label_frame.pack(fill=tk.BOTH,expand=tk.Y)
        

        return
#endregion
    



#region hash_table
class hash_table:
    #
    def __init__(self,size):
        self.size = size
        self.buckets = []
        self.keys = []
        for i in range(size) : self.buckets.append(Linked_list())
        pass
    
    def __iter__(self):
        return iter(self.keys)
    
    def __getitem__(self, key):
        return self.search(key)
    
    def __setitem__(self,key, data):
        self.insert(key,data)
        return

    #using chaining, no linear probing
    def insert(self,key,value):
        if (self[key] is None):
            bucket = self.buckets[self.hashfunction(key)]
            n = Node(key,value)
            n.data = value
            bucket.append(n)
            self.keys.append(key)
        else:
            self.update(key,value)
        return self
    
    def update(self,key,value):
        if (self[key] is not None):
            bucket = self.buckets[self.hashfunction(key)]
            node = bucket[Node(key)]
            node.data = value
        else:
            self.insert(key,value)
        return self

    #TODO: return a list of all values stored in the table
    def values(self):
        values = []
        return values
    
    def delete(self,key):
        bucket = self.buckets[self.hashfunction(key)]
        bucket.delete(key)
        for x in range(len(self.keys)):
            if self.keys[x] == key:
                self.keys.pop(x)
                break
        return

    def search(self,key):
        bucket = self.buckets[self.hashfunction(key)]
        current_node = bucket[Node(key)]
        if (current_node):
            return current_node.data
        else:
            return None
        
    # def copy(self):
    #     new_hash_table = hash_table(self.size)
    #     for key in self:
    #         new_hash_table[key] = self[key]
    #     return new_hash_table


    def hashfunction(self,key):
        return hash(key) % self.size
#endregion




#region Linked_list
class Linked_list:
    def __init__(self,node = None):
        self.head = node

    def __getitem__ (self,node):
        return self.search(node)


    def append(self,node):
        if (self.head is None):
            self.head = node
            return
        last_node = self.head
        #navigate to last node in list
        while (last_node.child):
            last_node = last_node.child
        last_node.child = node
        node.parent = last_node
        return
    
    def delete(self,key):
        temp = self.head
        if (temp is not None):
            if temp.key == key:
                self.head = temp.child
                temp = None
                return
        while temp is not None:
            if (temp.key == key):
                break
            temp = temp.child
        if (temp is None):
            return
        temp.parent.child = temp.child
        temp = None


    def search(self,node):
        current_node = self.head
        while (current_node):
            if (current_node.key == node.key):
                return current_node
            current_node = current_node.child
        return None
#endregion




#region Node
class Node:
    def __init__(self,key = None, data = None):
        self.parent = None
        self.child = None
        self.key = key
        self.data = data
        pass

    #this currently just assumes you are storing an array may need to add additional handling
    def __getitem__(self,key):
        try:
            return self.data[key]
        except:
            return None
#endregion




#region Package
class Package:
    
    def __init__(
            self, 
            id, 
            delivery_address = None,  
            delivery_city = None, 
            delivery_state = None, 
            delivery_zip = None, 
            delivery_deadline = "EOD",  
            package_weight = -1, 
            group_UID = None,
            delayed_reason = None,
            delayed_time = None,
            req_truck_id = None,
            special_instruction = None,
            status = Delivery_Status.AT_HUB, 
            delivered_time = None,
            
            ):
        self.id = id
        self.delivery_address = delivery_address
        self.delivery_city = delivery_city
        self.delivery_zip = delivery_zip
        self.delivery_state = delivery_state
        self.package_weight = package_weight
        self.group_UID = group_UID
        self.delayed_reason = delayed_reason  
        self.delayed_time = delayed_time
        self.req_truck_id = req_truck_id
        self.special_instruction = special_instruction
        self.expected_delivery_time=0
        self.delivery_truck_id = None

        self.delivery_deadline = self.convert_delivery_deadline(delivery_deadline)


        #Priority weighting calculation #NOTE: may need to be improved
        self.priority_weight = self.delivery_deadline/EOD_value
        
        self.status = status


        self.delivered_time = delivered_time
        self.get_adjacency()
        pass


    def __eq__(self,other):
        return self.id == other.id
    
    def deliver_package(self,delivery_time):
        self.status = Delivery_Status.DELIVERED
        self.delivered_time = delivery_time
        delivered_packages[self.id] = self

        
        # kind of using the distance table and hub_packages as a stand in for the database here, not sure if I can use SQLite for this project
        # feels like this should actually be changing values in a database and it should be queried for each new truck route calculation
        # this feels wonky

        # for x in distance_table:
        #     x[self.adj_index] = None

        self.status = Delivery_Status.DELIVERED
        return self
    
    def convert_delivery_deadline(self, delivery_deadline):
        if delivery_deadline == "EOD":
            delivery_deadline = EOD_value
        else:
            tmp = str(delivery_deadline).split(" ")
            hm = tmp[0]
            meridiem = tmp[1]
            hm = str(hm).split(":")
            hour = hm[0]
            minute = hm[1]
            
            if (meridiem == "AM"):
                meridiem = 0
                if (hour == 12):
                    hour = 0
            else:
                meridiem = 720

            


            delivery_deadline = (int(hour) * 60) + int(meridiem) + int(minute)
        return delivery_deadline

    def get_adjacency(self):
        adj_address = str(self.delivery_address) + " (" + str(self.delivery_zip) + ")"
        adj = adj_table.search(adj_address)
        # data is stored in the adj_table as [adj_index, [distances to all of the adjacent addresses]]
        self.adj_index = adj[0] 
        adj[1][self.adj_index] = None
        self.adj_distances = adj
        return
    
    #TODO: Improve Edge weight calculation method 

    # using 24 hour time
    # packages that need to be delivered by a set time need to be prioritized so need a lower edge weight
#endregion




#region Package_group
class Package_group:
    #id needs to equal the position in the distance table for the address of the packages.
    def __init__(self, id, priority_weights = None, packages = None, package_count = 0, required_truck_id = None):
        #double assignments here, could be improved
        self.id = id
        self.priority_weights = priority_weights
        self.packages = packages
        self.package_count = package_count
        self.required_truck_id = required_truck_id

        if priority_weights is None:
            self.priority_weights = []
        if packages is None:
            self.packages = hash_table(truck_size_limit)
        pass

    def __iter__(self):
        return iter(self.packages)
    
    def __getitem__(self,key):
        return self.packages[key]

    def add_package(self,package: Package):
        if  package.req_truck_id is not None:
            if (self.required_truck_id is not None) and (self.required_truck_id != package.req_truck_id):
                raise Exception("Unable to add package to Package Group, required truck id mismatch", self.required_truck_id,package.req_truck_id)
            else:
                self.required_truck_id = package.req_truck_id
        delivery_node = self.packages.search(package.adj_index)
        if delivery_node is None:
            self.packages.insert(package.adj_index, [package])
        else:
            delivery_node.append(package)
        self.priority_weights.append(package.priority_weight)
        self.calculate_priority()
        self.package_count += 1
        return
    
    def load_packages(self,truck_id):
        for key in self:
            for package in self[key]:
                package : Package
                package.delivery_truck_id = truck_id
                package.status = Delivery_Status.EN_ROUTE

    
    #deliver packages at a given node
    def deliver_packages(self,node,truck_id):
        delivery_node = self.packages[node]
        for x in range(len(delivery_node)):
            package : Package = delivery_node[x]
            package.deliver_package(current_time)
        self.packages.delete(node)
        self.package_count -= 1
        return
    
    def calculate_priority(self):
        #larger package groups should be prioritized first so they should have the smallest priority value
        self.priority_factor = sum(self.priority_weights)/ (len(self.priority_weights)**len(self.priority_weights))
        return

#endregion




#region Truck
class Truck:

    #driver id is negative if no driver assigned
    def __init__(self,truck_id, package_limit = truck_size_limit, truck_speed = truck_speed, driver = None, status = Delivery_Status.AT_HUB):
        self.truck_id = truck_id
        self.package_limit = package_limit
        self.packages = hash_table(package_limit)
        self.truck_speed = truck_speed
        self.driver = driver
        self.status = status
        self.remaining_space = package_limit
        self.en_route_node = None
        self.route = []
        self.next_delivery_time = None
        self.traveled_distance = 0
        self.current_route_distance = 0
        pass

    def get_all_packages(self,sort="N"): 

        packages = []
        if len(self.route) == 0:
            return packages
        try:
            for delivery_node in self.route:
                if delivery_node == 0:
                    continue
                for package in self.packages[delivery_node][delivery_node]:
                    packages.append(package)
            if sort == "Y":
                packages.sort(key=lambda x: x.id)

            return packages
        except TypeError:
            return

    #Load a package onto the truck
    def load_truck(self,hub_packages : hash_table):
        
        for package_group_key in self.route:
            if package_group_key == 0:
                continue
            package_group : Package_group = hub_packages.search(package_group_key)
            package_group.load_packages(self.truck_id)
            self.packages.insert(package_group_key,package_group)
            hub_packages.delete(package_group_key)



        # raise Exception("Unable to add package to truck")

    

    def return_to_hub(self):
        self.route = []
        self.packages = hash_table(self.package_limit)
        self.status = Delivery_Status.AT_HUB
        # self.current_route_distance += distance_table[self.previous_node][0]
        self.current_route_distance += distance_table[self.previous_node][self.en_route_node]
        self.en_route_node = None
        self.next_delivery_time = EOD_value
        self.traveled_distance += self.current_route_distance
        self.current_route_distance = 0
        return


    def deliver_to_next_node(self):
        if self.en_route_node == 0:
            self.return_to_hub()
            return
        package_group : Package_group = self.packages[self.en_route_node]
        self.remaining_space += len(package_group[self.en_route_node])
        package_group.deliver_packages(self.en_route_node, self.truck_id)
        self.calculate_next_node()
        return

    def calculate_next_node(self):
        self.current_route_distance += distance_table[self.previous_node][self.en_route_node]
        self.current_route_distance = round(self.current_route_distance,1)
        self.previous_node = self.route.pop(0)
        self.en_route_node = self.route[0]
        self.calculate_delivery_time()
        self.set_package_estimated_delivery_time()
        return
    
    def set_package_estimated_delivery_time(self):
        if self.en_route_node == 0:
            return
        for package in self.packages[self.en_route_node][self.en_route_node]:
                package : Package
                package.expected_delivery_time = self.next_delivery_time


    def calculate_delivery_time(self):
        next_delivery_time = distance_table[self.previous_node][self.en_route_node] + self.current_route_distance
        next_delivery_time = next_delivery_time * 60
        next_delivery_time = next_delivery_time/self.truck_speed
        next_delivery_time += self.depart_time
        self.next_delivery_time = next_delivery_time
        return

    def depart(self,depart_time):
        
        
        
        
        self.route.pop(0)
        if len(self.route) == 0:
            return
        try:
            self.en_route_node = self.route[0]
        except:
            raise
        self.status = Delivery_Status.EN_ROUTE
        self.depart_time = depart_time
        self.previous_node = 0 #start at the hub 
        self.current_route_distance = 0
        self.calculate_delivery_time()
        self.set_package_estimated_delivery_time()

        self.previous_node = 0 #start at hub for delivery calculations
        return


    def calculate_route(self, packages: hash_table):
        # the route is a list of package group IDs, route calculation automatically tracks the number of pacakages in a group and the total space on the truck, 
        # it should try to fill every truck up to max with the best option weighted towards delivering more packages at once and packages that have a deadline
        # priority calculations could be better
        distances = distance_table[0].copy() #hub index
        priorities = [] #list of all the package group indexes
        self.route.append(0) #start at hub
        #helper methods
        def find_nearest_neighbor(l):
            min = 0
            while (min < len(l) - 1) and (l[min] is None):
                min += 1
            if l[min] is None:
                return None
            for x in range(len(l)):
                if l[x] is not None:                
                    if l[x] < l[min]:
                        min = x
            
            return min

        def calculate_next_node(self, id, priorities, packages):
            distances = distance_table[id].copy()

                #ignore packages already added to the route
            for y in self.route:
                distances[y] = None

            #Nodes that are able to be visited must have a priority value, if not then they need to be None
            next_package_id = find_nearest_neighbor([None if ((distances[x] is None) or (distances[x] == 0) or (priorities[x] is None)) else (distances[x] * priorities[x]) for x in range(len(distances))])
            if next_package_id is None:
                self.route.clear
                raise Exception("Unable to find any packages to add to route")
            next_package_group : Package_group = packages.search(next_package_id)
            required_space = next_package_group.package_count
            if  (required_space <= self.remaining_space) and ((next_package_group.required_truck_id is None) or (next_package_group.required_truck_id == self.truck_id)):
                self.remaining_space -= required_space
                
                #should only append the node to the route if it isn't already there
                for delivery_node_id in next_package_group.packages.keys:
                    for current_route_node_id in self.route:
                        if delivery_node_id == current_route_node_id:
                            break
                    else:
                        self.route.append(delivery_node_id)
                return next_package_group.packages.keys[-1]
            else:
                distances[next_package_id] = None

        
        def get_priorities(distances):
            priorities = []
            for x in range(len(distances)):
                package_group : Package_group = packages.search(x)
                if package_group is not None:
                    priorities.append(package_group.priority_factor)
                else:
                    priorities.append(None)
            return priorities
        
        def calculate_total_distance(route):
            total_distance = 0
            for r in range(len(route) - 1):
                total_distance += distance_table[route[r]][route[r+1]]
            return total_distance

        def optimize_route(self):
            best_route = self.route
            best_distance = calculate_total_distance(self.route)
            new_distance = 0
            is_better_route = True
            while is_better_route:
                is_better_route = False
                for i in range(1,len(self.route) - 2):
                    for j in range(i+1, len(self.route) - 1):
                        new_route = self.route[:]
                        #using index slicing find two nodes and swap them 1,2,3,6 -> 1,3,2,6
                        new_route[i:j+1] = reversed(new_route[i:j+1])
                        new_distance = calculate_total_distance(new_route)
                        if new_distance < best_distance:
                            best_route = new_route
                            best_distance = new_distance
                            is_better_route = True
            self.route = best_route
            return

        priorities = get_priorities(distances)
        current_package_group_id = 0
        safe_to_continue = True
        while (safe_to_continue):
            # print(1)
            if (self.remaining_space > 0):
                safe_to_continue = True
            try:
                current_package_group_id = calculate_next_node(self, current_package_group_id,priorities, packages)
                if current_package_group_id is None:
                    safe_to_continue = False
            except Exception as inst:
                if inst.args[0] == 'Unable to find any packages to add to route':
                    safe_to_continue = False
                    if len(self.route) == 1:
                        self.route.clear
                        return self
                else:
                    raise inst
                
        self.route.append(0)
        if len(self.route) == 2:
            self.route.clear
            return self
        optimize_route(self)
        return self

    def assign_driver(self,driver):
        self.driver = driver
        pass

    # def remove_driver(self):
    #     self.driver_id = None
    #     pass
#endregion




#region Driver
class Driver:
    def __init__(self,employee_id):
        self.employee_id = employee_id
        pass
#endregion

def move_delayed_package_to_hub(package : Package, delayed_packages : Package_group):
        package.status = Delivery_Status.AT_HUB
        package.delayed_reason = None
        package.delayed_time = None
        package_group = hub_packages[package.adj_index]
        if package_group is None:
            package_group = Package_group(package.adj_index)
        package_group.add_package(package)
        hub_packages[package.adj_index] = package_group
        delayed_packages.delete(package.id)

def convert_timestamp(time):
    time = round(time)
    minutes = time%60
    hours = int((time-minutes)/60)
    if time == 0:
        hours = 12
    meridiem = "AM"
    if time >= 720:
        meridiem = "PM"
    if hours > 12:
        hours -= 12

    return "%02d" % hours + ":%02d " % minutes + meridiem

def advance_time(adv_amount = 1):
    i = 0
    global current_time
    
    if current_time >= EOD_value:
        return

    #helper methods
    def truck_en_route_logic(truck : Truck):
        if truck.next_delivery_time <= current_time:
            truck.deliver_to_next_node()
        return

    def truck_at_hub_logic(truck : Truck):
        if truck.driver is None:
            if len(unassigned_driver_list) > 0:
                truck.assign_driver(unassigned_driver_list.pop(0))
            else:
                return
            
        truck.calculate_route(hub_packages)
        truck.load_truck(hub_packages)
        truck.depart(current_time)

    
    def package_wrong_address(package: Package):
        for updated_address in address_update_list:
            #could be better
            if updated_address[0] == package.id:
                package.delivery_address = updated_address[1]
                package.delivery_city = updated_address[2]
                package.delivery_state = updated_address[3]
                package.delivery_zip = updated_address[4]
        move_delayed_package_to_hub(package,delayed_packages)

    def end_of_day_check():
        latest = 0
        for p in all_packages:
            package: Package = all_packages[p]
            if package.status != Delivery_Status.DELIVERED:
                return None
            if package.delivered_time > latest:
                latest = package.delivered_time
        return latest
    
    while i < adv_amount:
        
        
        #Truck Logic
        #only calucalate after the day has begun
        if current_time >= 8*60:
            truck : Truck
            for truck in truck_list:
                if truck.status == Delivery_Status.EN_ROUTE:
                    truck_en_route_logic(truck)
                elif truck.status == Delivery_Status.AT_HUB:
                    truck_at_hub_logic(truck)
            

            #Delayed Packages Logic
            for package_id in delayed_packages:
                package = delayed_packages[package_id]
                if current_time >= package.delayed_time:
                    if package.delayed_reason == "WRONG ADDRESS":
                        package_wrong_address(package)
                    elif package.delayed_reason == "FLIGHT DELAYED":
                        move_delayed_package_to_hub(package,delayed_packages)
            global last_package_delivery_time
            last_package_delivery_time = end_of_day_check()
        i += 1
        current_time += 1

def restart_day(selected_time):
    #This is probably not thread safe
    global current_time
    global last_package_delivery_time
    global truck_list
    global unassigned_driver_list
    global selected_package

    selected_package = None
    truck_list= []
    unassigned_driver_list = []
    current_time = selected_time
    
    last_package_delivery_time = None
    

    parse_package_file()
    create_truck_list()
    create_driver_list()

    return
    
def parse_package_file():
    global adj_table
    global hub_packages
    global initial_hub_packages
    global delayed_packages
    global initial_delayed_packages
    global delivered_packages
    global all_packages

    adj_table = hash_table(len(distance_addresses))
    hub_packages = hash_table(len(package_file) * 2) #worst case space complexity is 2N if all packages are solo
    delayed_packages =  hash_table(len(package_file))
    delivered_packages = hash_table(len(package_file))
    all_packages = hash_table(len(package_file))

    for i in range(len(distance_addresses)):
        # data is stored in the adj_table as {adj_index, [distances to all of the adjacent addresses]}
        adj_table.insert(distance_addresses[i],[i,distance_table[i]])

    for p in package_file:

        #New Package format
        # id, delivery_address = None,  delivery_city = None, delivery_state = None, delivery_zip = None,  delivery_deadline = "EOD", package_weight = -1, group_UID = None, delayed_time = None, req_truck_id = None, status = Delivery_Status.AT_HUB,   delivered_time = None

        # Package table data format
        #  0 Package ID, 1 Address, 2 City, 3 State, 4 Zip, 5 Delivery Deadline, 6 Weight, 7 Group UID,  8 Delayed Reason 9 Delayed time (in minutes), 10 Required Truck ID

        # would be easier if all this data was stored in an SQL table instead of a multi dimmensional array
        #TODO: rework this to instead just pass a list and have the constructor sort this out instead
        package = Package(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7], p[8], p[9],p[10],p[11])
        all_packages[package.id] = package

        if package.group_UID is None:
            package.group_UID = hash(str(package.adj_index))

        if package.group_UID == delayed_UID:
            package.status = Delivery_Status.DELAYED
            delayed_packages[package.id] = package
            continue

        package_group = hub_packages[package.group_UID]
            
        if (package_group is None):

            if hub_packages[package.adj_index] is not None:
                package_group : Package_group = hub_packages[package.adj_index]
                package_group.add_package(package)
            else:
                package_group = Package_group(package.group_UID)
                package_group.add_package(package)
                hub_packages[package.adj_index] = package_group
            hub_packages[package.group_UID] =  package_group


        else:
            try:
                package_group.add_package(package)
            #should only occur when trying to add packages with conflicting truck id requirements
            except Exception as inst:
                if inst.args[0] == "Unable to add package to Package Group, required truck id mismatch":
                    package_group = Package_group(package.group_UID)
                    package_group.add_package(package)
                else:
                    raise inst
            hub_packages[package.adj_index] = package_group

def create_truck_list():
    #not starting at 0 for the ids since that usually confuses non programmers
    for t in range(1,num_trucks + 1):
        #Truck init format:
        #id, package_limit, average_speed, driver_id
        truck = Truck(t, truck_size_limit, 18, None)
        truck_list.append(truck)
        
def create_driver_list():
    for d in range(1,num_drivers + 1):
        driver = Driver(d)
        unassigned_driver_list.append(driver)

#region Main
def main():
    parse_package_file()
    create_truck_list()
    create_driver_list()
  

    root = tk.Tk()
    GUI = Superviser_GUI(main=root)
    root.mainloop()
    return 0
#endregion




if __name__ == '__main__':
    sys.exit(main())
