# sm_data_analysis
Initially, the aim of this repository was to create a tool to pull follower and engagement data from instagram using the python instaloader module. Data would be saved in a csv format, before being uploaded to a Google Drive, and then imported to a Google Sheet. This data lifecycle can be seen in ig_follower_data_capture.jpg. While the end result is the same, I have gone through a few iterations of the implementation and settled on one that is far more streamlined, and captures more relevant data.

The repo now has 2 main functionalities:
1 - To capture and store the number of instagram followers for a list of accounts stored in a Google Sheet
2 - To use the Youtube API to gather data on the performance of youtube videos for the owners of the instagram accounts being tracked.

This repo was created for the purpose of helping BMX or BMX related companies make data-informed decisions on riders to sponsor in order to promote their products. Instagram follower account alone does not tell a complete picture as to how effective marketing through that account will be. Youtube data is helpful in telling a more complete picture, as video performance over time can be tracked. While the repo was created to aid BMX companies, there is no reason that the functionalities could not be used for other industries where there is a heavy focus on video content to promote products (skateboarding, scooters, snowboarding, mountain biking etc). 
