import json
import re
import yt_dlp
import yaml
from os import listdir, remove, mkdir
from jinja2 import Environment, FileSystemLoader

yaml_file = 'podcast.yml'
podcast_root_dir = '/tmp/test'
xml_template = 'audio.xml.j2'
podcast_audio_dir = f'{podcast_root_dir}/audio'
xml_file = 'podcast.xml'
jinja2_template_dir = 'templates/'


def read_podcast_info(yaml_filename: str) -> dict:
    """"
    Extracts  podcast info and a list of videos from a YAML file.
    """
    with open(yaml_filename, 'r') as file:
        data = yaml.safe_load(file)
    return data


def existing_audio(directory: str, audio_extension: str = 'mp3') -> list:
    """
    Returns a list of existing MP3 audio files in the specified directory.
    If the directory does not exist, it prints a message
    and creates the directory.
    """
    result = []
    try:
        for f in listdir(directory):
            if f.endswith(audio_extension):
                result.append(f)
    except OSError as e:
        print(f'Audio directory not found: {directory}. It will be created.')
        mkdir(directory)
    return result


def sync_all(video_infos: dict, audios: dict) -> list:
    """
    Synchronizes video and audio files by downloading missing audio files
    and removing obsolete ones.
    Returns a list of video filenames.
    """
    videos = [i['filename'] for i in video_infos]
    add_audio(list(set(videos) - set(audios)), video_infos)
    remove_audio(list(set(audios) - set(videos)))
    return item_list(videos)


def remove_audio(to_remove: list):
    """
    Remove audio files that were not found in metadata file
    """
    if to_remove:
        print(f"Audios to remove: {', '.join(str(i) for i in to_remove)}")
        for i in to_remove:
            full_name = f'{podcast_audio_dir}/{i}'
            remove(full_name)
            remove(f'{full_name.replace(".mp3", "")}.info.json')
            print(f'File removed: {full_name}')
    else:
        print("No podcast to remove. Skipping.")


def add_audio(to_add: list, video_infos: list):
    """
    Download newly added podcast files as audio
    """
    if to_add:
        print(f"Audios to add: {', '.join(str(i) for i in to_add)}")
        for i in video_infos:
            if i['filename'] in to_add:
                full_name = f'{podcast_audio_dir}/{i["filename"]}'
                download(i['link'], full_name)
            else:
                print(f"File exists, skipping: {i['filename']}")
    else:
        print("No new podcast to add. Skipping.")


def download(url: str, filename: str):
    """
    Downloads audio from the given URL,
    converts it to MP3 at 320 kbps,
    and saves it with metadata.
    """
    preferred_quality = '320'
    ydl_opts = {
            'outtmpl': filename.replace('.mp3', ''),
            'extract_audio': True,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': preferred_quality,
            }],
            'dump_single_json': False,
            'writeinfojson': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def item_list(file_list: list) -> list:
    """
    Generates a list of metadata dictionaries for each audio file,
    extracting information from its corresponding JSON file.
    """
    items = []
    for i in file_list:
        full_name = f'{podcast_audio_dir}/{i.replace(".mp3", "")}.info.json'
        with open(full_name) as f:
            data = json.load(f)
            items.append(
                    {
                        "guid": data["id"],
                        "name": data["title"],
                        "filename": i,
                        "description": re.sub(
                            r'http\S+', '',
                            data["description"]).replace('&', '')
                    }
                )
    return items


def generate_xml(template_file: str, xml_file: str,
                 info: dict, items: list):
    """
    Generates an XML file from a Jinja2 template using provided item data.
    """
    file_loader = FileSystemLoader(jinja2_template_dir)
    env = Environment(loader=file_loader)
    template = env.get_template(template_file)
    content = template.render(info=info, items=items)
    with open(xml_file, mode="w", encoding="utf-8") as message:
        message.write(content)


def main():
    """
    Main function
    """
    podcast_info = read_podcast_info(yaml_file)
    video_list = podcast_info['videos']
    audo_files = existing_audio(podcast_audio_dir)
    items = sync_all(video_list, audo_files)
    xml_fullname = f'{podcast_root_dir}/{xml_file}'
    generate_xml(xml_template, xml_fullname, podcast_info, items)


main()
