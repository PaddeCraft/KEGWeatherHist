# Ensure root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

printf "Creating directory... "
mkdir overlay/home/alarm/KEGWeatherHist/
printf "Done\n"

# Copy .env file if it exists
if [ -f ../.env ]; then
    printf "Copying .env file... "
    cp ../.env overlay/home/alarm/KEGWeatherHist/
    printf "Done\n"
fi

files=( "start.py" "requirements.txt" "src" "assets" "static" "templates" )
architectures=( "rpi-armv7" "rpi-aarch64" )
architecture_friendly_names=( "RPi2+3" "RPi4" )

printf "Copying files... "
for file in "${files[@]}"
do
    cp -r ../$file overlay/home/alarm/KEGWeatherHist/
done

cp -r ../start overlay/home/alarm/Desktop/
printf "Done\n"

printf "Creating image(s)...\n"
# Create output directory
mkdir -p build
rm -rf build/*

for i in "${!architectures[@]}";
do
    arch=${architectures[$i]}
    friendly_name=${architecture_friendly_names[$i]}
    printf "======> $arch ($friendly_name)... "
    sudo ./create-image 6G $arch setup/$arch setup/avahi setup/kegweather
    mv archlinux-$arch.img build/Image-Hub-$friendly_name-$arch.img
	printf "Compressing image..."
	gzip build/Image-Hub-$friendly_name-$arch.img
    printf "Done\n"
done

printf "Cleaning up... "
rm -rf overlay/home/alarm/KEGWeatherHist/
rm -rf overlay/home/alarm/Desktop/start
printf "Done\n"
