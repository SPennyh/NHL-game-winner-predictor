# NHL-game-winner-predictor
This project leverages advanced statistics sourced from [Natural Stat Trick](https://www.naturalstattrick.com), utilizing scikit-learn's RandomForestClassifier to forecast the outcomes of NHL games.

An API call is made to google cloud API to save the results and all the other advanced statistics to a [Google Sheet](https://docs.google.com/spreadsheets/d/1RPnWiBpVTMGZOeH4-P1Z44eDeApi5YLXYUU9X3kAj4Y/edit?usp=sharing).

The scripts are ran on a daily schedule hosted by AWS Lambda functions using Docker images. 
- `get_games.py` is scheduled to run at 9:15am PST everyday.
- `get_stats.py` is scheduled to run at 9:20am PST everyday.
- `MLwinner.py` is scheduled to run at 9:25am PST everyday.
- `get_winners.py` is scheduled to run at 11:00pm PST everyday.

If you'd like to run the scripts your selves, you must initiate your own Google Sheet to replace `SHEET_ID` and `SHEET_NAME`.
I also recommend also removing the sheet updating methods as those will require JSON key to run (you could also initiate your own Google Cloud API keys, to store your results), and instead loading the results into a CSV file.

# Dependencies
- pandas
- lxml
- numpy
- scikit-learn
- gspread
