from typing import Union, List
from collections import defaultdict
from collections.abc import Iterable
import logging

from html_update_checker.homepage import HomepageUpdateInterface
from html_update_checker import sendgrid

class User(HomepageUpdateInterface):
    def __init__(self, email:str):
        self.email = email
        self.homepages = dict()
        self.pending_update_notifications = defaultdict(list)
    
    def add_homepage_notifications(self, homepage:Union["Homepage", List["Homepage"]]) -> None:
        if isinstance(homepage, Iterable):
            for hp in homepage:
                self.add_homepage_notifications(hp)
        else:
            self.homepages[homepage.url] = homepage
            homepage.register_for_updates(self) 

    def remove_homepage_notifications(self, homepage:Union["Homepage", List["Homepage"]]) -> None:
        if isinstance(homepage, Iterable):
            for hp in homepage:
                self.remove_homepage_notifications(hp)
        else:
            del self.homepages[homepage.url]
    
    def __create_mail_body(self) -> str:
        episode_updates_html = self.__create_episode_updates_html()
        if episode_updates_html:
            return f"<h1>Episode updates</h1><br/>{episode_updates_html}"

    def __create_episode_updates_html(self) -> str:
        episode_updates_html = ""
        for homepage_url, episode_list in self.pending_update_notifications.items():
            if not episode_list: continue
            episode_updates_html += f"<p><h2>{homepage_url}</h2>"
            for episode in episode_list:
                episode_updates_html += f'[{episode.episode_number}] <a href="{episode.url}">{episode.name}</a><br/>'
            episode_updates_html += "</p>"
        
        return episode_updates_html

    def __send_mail(self, html_body:str) -> None:
        sendgrid.send_message(html_body)

    def __remove_update_notifications(self) -> None:
        self.pending_update_notifications = defaultdict(list)

    def send_updates(self) -> None:
        # Create HTML updatemail body
        html_body = self.__create_mail_body()
        if html_body:
            # Send mail
            self.__send_mail(html_body)
            # Remove update notifications after successfull sendout
            self.__remove_update_notifications()

    def add_update_notification(self, homepage:"Homepage", episode:Union["Episode", List["Episode"]]) -> None:
        if isinstance(episode, Iterable):
            for ep in episode:
                self.add_update_notification(ep)
        else:
            self.pending_update_notifications[homepage.url].append(episode)
            logging.info(f"[{self.email}] Added {episode}")

        


    
        

