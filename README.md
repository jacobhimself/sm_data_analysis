# sm_data_analysis
The aim of this repository is to create a tool to pull follower and engagement data from instagram using python, and save it in a csv format.

A log of progress will be kept here in the README file

The daily lifecyle of data movement in this project is as follows:

![IG_Follower_Diagram](ig_follower_data_capture.jpg)

Day 1:
Created draft outline of the project and daily lifecycle. Originally wanted to use R for data scraping but python appeared to be an easier solution with regards to available modules
Spent time becoming reacquainted with python after not using it since graduating university (4 years ago!). Relearned how to read/write to/from csv files.
Set up pip installer
Searched for module to help with instagram scraping
As part of initial drafting, my script pulled and pushed the WHOLE spreadsheet of handles and follower counts, which will become unneccesarily slow once the spreadsheet is populated. Came up with solution to just pull a list of account handles each day (in case there are insertions/deletions) and upload only the follower count for that day.


