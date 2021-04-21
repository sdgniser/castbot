"""
Utilities for castbot

"""
import requests
import re
import feedparser
import random

from bs4 import BeautifulSoup


def get_info(podcast=0):
    """
    Reads the RSS feed and formats it as a Discord message

    podcast: int
        Episode number (defaults to ``0`` / latest)

    """
    feed = feedparser.parse("https://nisercast.gitlab.io/rss.xml")
    # Always in last-in order
    pods = feed["entries"]

    try:
        pod = pods[podcast]
    except IndexError:
        return None

    pod_title = pod.title
    pod_published = pod.published
    pod_longdesc = BeautifulSoup(pod.summary, "html.parser").get_text()
    pod_shortdesc = re.search('(.+?)Episode Notes:', pod_longdesc).group(1)

    return pod_title, pod_published, pod_shortdesc


def get_links():
    """
    Gets links to new episodes from various platforms
    
    """
    # Google
    google_show = "https://podcasts.google.com/feed/aHR0cHM6Ly9uaXNlcmNhc3QuZ2l0bGFiLmlvL3Jzcy54bWw"
    google_page = requests.get(google_show).text
    google_soup = BeautifulSoup(google_page, "html.parser")
    google_latest = google_show + "/episode/" + re.search("/episode/(.*?)\?", str(google_soup)).group(1)

    # Spotify
    spotify_show = "https://open.spotify.com/show/6b9PbZU6siLA5tPE1m1Gve"
    spotify_page = requests.get(spotify_show).text
    spotify_soup = BeautifulSoup(spotify_page, "html.parser")
    spotify_latest = re.search('spotify":"(.*?)"', str(spotify_soup)).group(1)

    # Apple (sucks)
    # https://podcasts.apple.com/in/podcast/1-story-for-everything-prof-varadharajan-muruganandam/id1561466001?i=1000517683108
    # apple_show = "https://podcasts.apple.com/in/podcast/nisercast/id1561466001"
    # apple_page = requests.get(apple_show, headers).text
    # apple_soup = BeautifulSoup(apple_page, "html.parser")
    # apple_latest = "https://podcasts.apple.com/in/podcast/" + re.search("in/podcast/(.*?)", str(apple_soup)).group(1)

    # print(apple_latest)

    links = [google_latest, spotify_latest]

    return links


def rcol():
    """
    Returns random RGB triplets

    """
    return random.sample(range(255), 3)
