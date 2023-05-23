# SQLAlchemy challenge

## Description
Utilized SQLAlchemy, Jupyter Notebook, Flask API, and Pandas to perform data analysis on Hawaiian temperature station data.

## Directory
- SurfsUp folder contains the scripts and data that were used to run the queries.
    - climate.ipynb contains the jupyter notebook used to analyze and explore the climate data
    - app.py contains the code used to design the climate analysis API using Flask
        - several directories were defined to analyze different aspects of the data
            - `/` 
                - Home page with available routes defined
            - `/api/v1.0/precipitation`
                - Date and precipitation for latest year for all stations as JSON
            - `/api/v1.0/stations`
                - List of unique stations as JSON
            - `/api/v1.0/tobs`
                - Latest year of dates and temperatures for most active station
            - `/api/v1.0/[start]`
                - Min, max, and avg temperature from start to latest date as JSON
            - `/api/v1.0/[start]/[end]`
                - Min, max, and avg temperature for custom date range as JSON