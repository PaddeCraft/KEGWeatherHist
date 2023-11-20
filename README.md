# KEGWeatherHist

## Prerequisites

- reachable meteohub instance
- FTF-server and its credentials
- any device to run this software on (needs to have python installed)

## Installing the requirements

To install the requirements:
`pip install -r requirements.txt`

## Set up environment

Copy the `.env.example` file to `.env` and populate it with your configuration.

## Run

Run the python script at `start.py` to start the uploader.
Run the script `display_meteohub/meteohub-display/update_data.py` from the `display_meteohub/meteohub-display` directory

## Credits

The interface is based on [PaddeCraft/Weathersite](https://github.com/PaddeCraft/Weathersite).