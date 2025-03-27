# yt-pod

This tiny applications allows to transform YouTube videos to Apple podcasts. It downloads and decodes the video to audio format. After this it generates XML metadata file and stores it next to the audio files.

As soon as all files are downloaded, they may be hosted either locally or in the cloud (e.g. AWS S3)

## Usage

Before you run the app, make sure you updated the `podcast.yml` file, it contains all metdata about the podcast, including the list of videos.

### Run locally as python application

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Run using docker

```sh
docker pull
docker run -v volume:volume
```

## Add to your podcast app by URL

You can add your podcast directly to the Apple podcast app by URL without publishing it to Apple.

## Metadata file

The metadata about the podcast is located in the `podcast.yml` file.