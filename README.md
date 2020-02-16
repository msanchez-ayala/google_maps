# Travel Time Optimization

My girlfriend and I live in two different NYC boroughs, making traveling between
our apartments a real pain. Although an Uber is not too expensive at off-peak times,
my method of choice is public transit since I already have a monthly unlimited pass.
It usually feels that it takes around an hour to get between our apartments, given
that I typically only make the trip on the weekends. I propose this study to determine
when are the quickest and most efficient times to travel between our apartments
using Google Maps.

## Data and Outcomes

Every 5 minutes for one week, I'll call the Google Maps API to gather information
about the "best trip" method to travel from 1) my apartment to hers and 2) her
apartment to mine. The data will be stored on an AWS MySQL RDS instance. Then, I'll
perform EDA to determine the best travel times and see what other insights I can
glean. Some basic statistical modeling could even be interesting depending on
what I find.
