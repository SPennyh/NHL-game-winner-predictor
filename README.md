# NHL-game-winner-predictor
This project leverages advanced statistics sourced from [Natural Stat Trick](https://www.naturalstattrick.com), utilizing scikit-learn's RandomForestClassifier to forecast the outcomes of NHL games.

An API call is made to Google Cloud API to save the results and all the other advanced statistics to a [Google Sheet](https://docs.google.com/spreadsheets/d/1RPnWiBpVTMGZOeH4-P1Z44eDeApi5YLXYUU9X3kAj4Y/edit?usp=sharing).

The scripts are run on a daily schedule hosted by AWS Lambda functions using Docker images. 
- `get_games.py` is scheduled to run at 9:15am PST everyday.
- `get_stats.py` is scheduled to run at 9:20am PST everyday.
- `MLwinner.py` is scheduled to run at 9:25am PST everyday.
- `get_winners.py` is scheduled to run at 11:00pm PST everyday.

If you'd like to run the scripts your selves, you must initiate your own Google Sheet to replace `SHEET_ID` and `SHEET_NAME`.
I also recommend removing the sheet updating methods as those will require JSON key to run (you could also initiate your own Google Cloud API keys, to store your results), and instead loading the results into a CSV file.

# Dependencies
- pandas
- lxml
- numpy
- scikit-learn
- gspread

# Background and Creation Process

## Motivation
This project began back in the winter break in December 2023 after finishing my computational data science course. After recently completing the project NHL conference final predictor project, I was inspired to predict the outcome of individual games. So, the first step was to find data. 
## Data Collection
I was familiar with the site “Natural Stat Trick”, which tracks team advanced statistics. What I like about their site is that you’re able to find data up until a certain date throughout the season. So I had to figure out how to scrape that data off of their site. I first attempted to use the Beautiful Soup library, however it was messy since I was scraping the data from HTML tables. I then gave up for a couple of days and then came back to it with a few Google searches later, I discovered the panda’s library which I was very familiar with had a built-in function called read_html which pulls HTML tables into data frames. Next, I did a bit of string parsing and data cleaning to achieve the desired data I wanted. From there, I originally just copied and pasted the data into a Google sheet from the CSV it produced. So that was just the initial gathering of data up to the current date. 
## Scripts
So, from here I had to figure out a way to update it daily, this was done by using 3 scripts. The first one ran was get_games to get the teams playing for the day, the second script was get_stats which found the stats for the teams playing for that day, and finally, a get_winners script which found the winner of the day. These scripts ran at certain times of the day, where get_games and get_stats had to be run in the morning before any games started. Then get_winners ran at night after all the games had finished for the day. So, then all these scripts were structured very similarly where they scrape an HTML table from certain webpages from Natural Stat Trick and then parsed and cleaned respectively to achieve the data I needed.  
## Machine Learning
The next step was to develop somewhat of a machine learning model to predict the games. So, in this current project, I used the randomForestClassifier, where I optimized the parameters to get the best accuracy. I had tried to use other ML models Sklearn had such as multi-layer perceptrons and support vector classification, but optimizing them the best I could, they were not as good as the random forest model. So, from there I read the Google sheet of data and used the games from before the current day as the training data, and then the data from the current day as the testing data, where it will spit out a prediction for the winner of the day.  
## Data Storage
After a while, it became tedious copying and pasting the data into the sheet resulting me in forgetting some days and eventually getting too busy with school to keep it going. So I did a bit of research on updating Google Sheets through Python and stumbled upon Google Cloud APIs. Where I got an API key to connect to my Google sheet. Then by using the gspread library, I performed batch updates for each of the 4 files where it would import the data into the sheet resulting in 4 requests to the API.
## Computing
The next step was to automate this process, and after some further research, I settled on using AWS Lambda, where then I would convert the 4 scripts into docker images. I didn’t need to containerize all of them as most of the script’s dependencies didn’t exceed the AWS Lambda file size limit, however, I wanted to become familiar with the containerization process, so I converted all of them. The last step was then to schedule each of the scripts using the eventbridge trigger in AWS Lambda, where get_games, get_stats, and machine learning script ran at 9 am consecutively. And at 11 pm later in the day, get_winners ran.   
## Results
Once everything was all automated, I began tracking the success rate of the model, and even though I only had the opportunity to run it for a month it achieved a 57% success rate, which isn’t the best result, but I think it was pretty was cool predicting over half of the games correctly.  
## Opportunities
Some of the future opportunities I can achieve are perhaps using individual stat lines to predict the outcomes, and perhaps visualizing some of my findings to see what is happening.

