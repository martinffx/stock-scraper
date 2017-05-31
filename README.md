# Stock Scraper

*PRE-ALPHA* this is in no way complete!

Stock Scraper is a simple application to pull stock price information from google spreadsheet and store it in a database. It can pull data for a whole index using [FT index constituent](1) data stored in the [index sheet](2).

# Examples

## Update the index data

    $ python main.py

This will pull all the indexes in the index sheet and save each index in the index table. For each index it will fetch all the constituent shares and update the share data in the share table.

## Update a single Index and all constituent's price data

    $ python main.py --index FTSE:FSI 2017-05-01 2017-05-31

This will update that Index as above and fetch the

##

# Getting Started

# TODO

- []
- []
- []
