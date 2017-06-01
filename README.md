# Stock Scraper

*PRE-ALPHA* this is in no way complete!

Stock Scraper is a simple application to pull stock price information from google spreadsheet and store it in a database. It can pull data for a whole index using [FT index constituent][1] data stored in the [index sheet][2].

# Examples

## Update the index data

    $ python main.py

This will pull all the indexes in the index sheet and save each index in the index table. For each index it will fetch all the constituent shares and update the share data in the share table.

## Update a single Index and all constituent shares price data for a given period

    $ python main.py --index FTSE:FSI 2017-05-01 2017-05-31
    # or leave the dates out and it'll default to yesterday
    $ python main.py --index FTSE:FSI

This will update that Index as described above and fetch the price data for the specified period for each share in that index.

## Update the price data for a single share for a given period

    $ python main.py --share AAL:LSE 2017-05-01 2017-05-31
    # or leave the dates out and it'll default to yesterday
    $ python main.py --share AAL:LSE

This will update the given share price data for the given period for the given period

# Getting Started

The easiest way to get started is to with this right now is to checkout the code run it using docker:

    $ git clone git@github.com:martinffx/stock-scraper.git
    $ cd stock-scraper
    $ docker-compose run scraper python main.py

# TODO

- [x] Get index data from sheet
- [x] Save index data into database
- [x] Fetch index constituents
- [x] Save share data in database
- [ ] Fetch price data from sheet
- [ ] Save price data
- [ ] Parallelize scraping
- [ ] Setup CI to build and publish a docker image

[1]: https://markets.ft.com/data/indices/tearsheet/constituents?s=FTSE:FSI
[2]: https://docs.google.com/spreadsheets/d/10sHdXR_NyQ-hxrEu7QALDX5qwuLWjCAfENSh2c3Cka4/edit#gid=0
