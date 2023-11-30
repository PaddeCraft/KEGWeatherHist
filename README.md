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

## Building the image

For our specific needs, the build script builds for the RaspberryPi 3. To build, go into the `image-builder` directory and run
the `build_kegweather_image` script with root privileges. Good look getting the development environment running, I think you need
to have qemu-system-aarch64, but I don't really know anymore, it's just luck to get it running, I think i used the command `qemu-system-aarch64 -M raspi3b -m 1024 -kernel ./vmlinuz -initrd ./initrd`.

## Credits

The interface is based on [PaddeCraft/Weathersite](https://github.com/PaddeCraft/Weathersite). The image build script is taken from [fwcd/archlinux-arm-images](https://github.com/fwcd/archlinux-arm-images).