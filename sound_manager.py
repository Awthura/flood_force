import pygame as pg
import random
import os
from settings import *

class SoundManager:
    def __init__(self):
        # Initialize Pygame mixer
        pg.mixer.init()
        
        # Set up music dictionaries for different game states
        self.menu_tracks = [
            os.path.join("assets/music", "main_menu_1.ogg"),
            os.path.join("assets/music", "main_menu_2.ogg")
        ]
        
        self.gameplay_tracks = [
            os.path.join("assets/music", "gameplay_1.ogg"),
            os.path.join("assets/music", "gameplay_2.ogg")
        ]
        
        self.victory_tracks = [
            os.path.join("assets/music", "victory.ogg"),
            os.path.join("assets/music", "victory_2.ogg")
        ]
        
        self.game_over_tracks = [
            os.path.join("assets/music", "game_over_1.ogg"),
            os.path.join("assets/music", "game_over_2.ogg")
        ]
        
        self.current_state = None
        
    def update_music(self, game_state):
        """Update music based on game state"""
        # Only change music if the state has changed
        if game_state != self.current_state:
            self.current_state = game_state
            
            # Stop current music
            pg.mixer.music.stop()
            
            # Select and play appropriate music
            if game_state == MENU:
                self._play_random_track(self.menu_tracks)
            elif game_state in [PLANNING, WEATHER]:
                self._play_random_track(self.gameplay_tracks)
            elif game_state == VICTORY:
                self._play_random_track(self.victory_tracks, loop=False)
            elif game_state == GAME_OVER:
                self._play_random_track(self.game_over_tracks, loop=False)
    
    def _play_random_track(self, track_list, loop=True):
        """Play a random track from the given list"""
        if track_list:
            try:
                track = random.choice(track_list)
                pg.mixer.music.load(track)
                pg.mixer.music.play(-1 if loop else 0)  # -1 for loop, 0 for once
            except Exception as e:
                print(f"Error playing music track: {e}")
    
    def stop_music(self):
        """Stop all music playback"""
        pg.mixer.music.stop()
    
    def set_volume(self, volume=0.5):
        """Set music volume (0.0 to 1.0)"""
        pg.mixer.music.set_volume(volume)