"""
Utilities for castbot

"""
import requests
import re
import feedparser
import random

from bs4 import BeautifulSoup


def get_info(podcast=-1):
    """
    Reads the RSS feed and formats it as a Discord message

    podcast: int
        Episode number (defaults to ``-1`` / latest)

    """
    feed = feedparser.parse("https://nisercast.gitlab.io/rss.xml")
    # Always in last-in order
    pods = feed["entries"]
    pods.reverse()

    try:
        pod = pods[podcast]
    except IndexError:
        return None

    pod_num = len(pods)
    pod_title = pod.title
    pod_published = pod.published
    pod_longdesc = BeautifulSoup(pod.summary, "html.parser").get_text()
    pod_shortdesc = re.search('(.+?)Episode Notes:', pod_longdesc).group(1)

    return pod_num, pod_title, pod_published, pod_shortdesc


def get_links():
    """
    Gets links to new episodes from various platforms
    
    """
    # Google
    google_show = r"https://podcasts.google.com/feed/aHR0cHM6Ly9uaXNlcmNhc3QuZ2l0bGFiLmlvL3Jzcy54bWw"
    google_page = requests.get(google_show).text
    google_soup = BeautifulSoup(google_page, "html.parser")
    google_latest = google_show + "/episode/" + re.search("/episode/(.*?)\?", str(google_soup)).group(1)

    # Spotify
    spotify_show = r"https://open.spotify.com/show/6b9PbZU6siLA5tPE1m1Gve"
    spotify_page = requests.get(spotify_show).text
    spotify_soup = BeautifulSoup(spotify_page, "html.parser")
    spotify_latest = re.search('spotify":"(.*?)"', str(spotify_soup)).group(1)

    # Apple
    apple_show = r"https://podcasts.apple.com/in/podcast/nisercast/id1561466001"
    apple_page = requests.get(apple_show).text
    apple_soup = BeautifulSoup(apple_page, "html.parser")
    apple_latest = "https://podcasts.apple.com/in/podcast/id1561466001?i=" + re.search('\/id1561466001\?i=([0-9]+)"', str(apple_soup)).group(1)

    links = [google_latest, spotify_latest, apple_latest]

    return links


def rcol():
    """
    Returns random RGB triplets

    """
    return random.sample(range(255), 3)
