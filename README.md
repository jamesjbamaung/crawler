# UFC Stats Crawler

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Debugging](#debugging)
 
## About <a name = "about"></a>

This is a web scraper to get data from [UFC Stats](http://ufcstats.com/), built using [Scrapy](https://github.com/scrapy/scrapy). Scraped data are organized as follows:

All completed UFC fights:

- `fight_info` <a name = "fight_info"></a> table, contains fight/match-up level meta-data.
- `fighter_stats`<a name = "fighter_stats"></a> table, contains fighter level data of fighters' career summary statistics.
- `fight_stats` <a name="fight_stats"></a> contains fighter-level performance data within each match-up. 
- `fight_rounds` <a name="fight_rounds"></a> contains fighter-level performance data within each match-up by round. 

Upcoming fights:

- `upcoming`<a name = "upcoming"></a> table contains match-up level information of all the upcoming fights in the next UFC event, according to this page http://ufcstats.com/statistics/events/completed. 


## Getting Started <a name = "getting_started"></a>

### Prerequisites

* Python 3
* Scrapy
* Anaconda or Pip (Anaconda is recomended for installation of Scrapy)

It is recomended that you install these packages in a virual environment as opposed to a global install.

# Create Virtual Environment 
With pip:

```
py -m pip install --user virtualenv

#create and name environment
py -m venv envName

#activate environment
.\env\Scripts\activate #activate script
```

With Conda:

```
#create and name environment
conda create --name myenv

#activate environment
conda activate myenv
```

# Install required packages.


```
pip install -r requirements.txt
```
If this errors out, install Anaconda and try 

```
conda install -c conda-forge scrapy 
conda install -file requirements.txt
```

If you have trouble installing Scrapy, see the install section in Scrapy documentation at https://docs.scrapy.org/en/latest/intro/install.html for more details.


## Usage <a name = "usage"></a>

_Note: in the current version, running the spider will crawl the entire site, so it will take some time._

Call `scrapy crawl spider_name` to start the crawler. There are 3 spiders you can run:

```
scrapy crawl ufcFights
```

The `ufcFights` spider will return

- [`fight_info`](#fight_info) table as a `.csv` file saved in `data/fight_info` directory.
- [`fight_stats`](#fight_stats) table as `.jl` file (newline-delimited JSON) saved in `data/fight_stats` directory. One line per fight.
- [`fight_rounds`](#fight_rounds) table as `.jl` file (newline-delimited JSON) saved in `data/fight_rounds` directory. One line per fight.

*If you prefer other output formats, you can modify the respective feed exports pipelines in `pipelines.py`.*


```
scrapy crawl ufcFighters
```

The `ufcFighters` spider will return the [`fighter_stats`](#fighter_stats) table as a `.csv` file saved in `data/fighter_stats` directory.

```
scrapy crawl upcoming
```

The `upcoming` spider will return [`upcoming`](#upcoming) table as a `.csv` file, saved in `data/upcoming` directory.

All output files use timestamp as file names, stored in different folders.


## Debugging <a name = "debugging"></a>

# Text Editor and Extensions
I use Visual Studio Code with Code Runner and Python extensions. 

# Procedure
* With the project open in VS Code, click `Ctrl + Shift + P` to open up the command palette.
* Type in 'Python: Select Interpreter' and select the environment created from above.
* Go to the ``runner.py`` file and click the 'Start' button on the debug panel.

The ``runner.py`` file currently has this code to run the spider for 'ufcFights'.

```
from scrapy.cmdline import execute
execute(['scrapy','crawl', 'ufcFights'])
```
To run other spiders, change 'ufcFights' to the name of the spider

