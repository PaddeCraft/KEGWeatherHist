# KEGWeatherHist

## Installing the requirements

To install the requirements:
`pip install -r requirements(.logger).txt`

## Deploying the docker container

```shell
docker run -d --rm ghcr.io/paddecraft/keg-weather-history-webserver:latest -v <storage path>:/data -v </path/to/.env>:/server/.env -p <port>:8080
```

## Credits

The interface is based on [PaddeCraft/Weathersite](https://github.com/PaddeCraft/Weathersite).