# Travel Time Optimization

This project was born from the fact that my girlfriend and I live in two
different NYC boroughs, making travel between our apartments a real pain.
Although Uber/Lyft are not too expensive at off-peak times, my method of choice
is public transit since I already have a monthly unlimited pass.

It usually feels that it takes around an hour to get between our apartments,
given that I typically only make the trip on the weekends. I started this
project to figure out when we can get between our apartments the quickest via
public transportation, namely subway and bus.

## Data and Outcomes

The objective is to collect the "best trip" information from the Google Maps API
every 5 minutes for one week from 1) my apartment to my girlfriend's and 2) her
apartment to mine. My initial exploration stores the data a MySQL RDS instance.
I perform EDA to determine the best travel times and see what other insights I can
glean, and present this in a simple dashboard using Dash.

## Extendability

Once complete, I'll make this repository reproducible for the travel time
optimization between any two locations using Google Maps info. 
