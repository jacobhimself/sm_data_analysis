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

Day 2:
Finished steps 2, 3, and 4. Step 5 is finished up to the point where only the automation aspect is left to do.
Became acquainted with Google Apps Script, which is effectively a javascript library with built in functions to interact with Google products (in this case, Sheets). I don't foresee automating the pulling of data from the csv in the Drive folder to be too difficult as I saw that timers can be set to run scripts at certain intervals.
One addition I made that I had not previously planned for was converting the daily handle/follower csv into a JSON object so that it can be processed with greater ease once it is in the Apps Script environment.
