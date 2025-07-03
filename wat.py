import pygame
import csv
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Initialize mixer for sound
pygame.mixer.init()

# Get fullscreen resolution
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 40)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
BLUE = (100, 150, 255)

# Font settings (scaled for fullscreen)
BASE_FONT_SIZE = 80
TIMER_FONT_SIZE = 48
INSTRUCTION_FONT_SIZE = 28
SMALL_FONT_SIZE = 20

# Scale fonts based on screen resolution
SCALE_FACTOR = min(SCREEN_WIDTH / 1024, SCREEN_HEIGHT / 768)
FONT_SIZE = int(BASE_FONT_SIZE * SCALE_FACTOR)
TIMER_FONT_SIZE = int(TIMER_FONT_SIZE * SCALE_FACTOR)
INSTRUCTION_FONT_SIZE = int(INSTRUCTION_FONT_SIZE * SCALE_FACTOR)
SMALL_FONT_SIZE = int(SMALL_FONT_SIZE * SCALE_FACTOR)

class WATApp:
    def __init__(self):
        # Set fullscreen mode
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("SSB Word Association Test")
        
        # Load bell sound
        self.load_bell_sound()
        
        # Fonts
        self.word_font = pygame.font.Font(None, FONT_SIZE)
        self.timer_font = pygame.font.Font(None, TIMER_FONT_SIZE)
        self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        
        # Game state
        self.current_session_words = []  # Current 60 words for this session
        self.current_word_index = 0
        self.session_word_count = 0
        self.max_words_per_session = 60
        self.is_running = False
        self.is_paused = False
        self.start_time = 0
        self.word_duration = 17  # 20 seconds per word
        self.waiting_for_start = True
        
        # Load words from CSV
        self.load_words()
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
    
    def load_bell_sound(self):
        """Load bell sound file"""
        try:
            self.bell_sound = pygame.mixer.Sound('bell.wav')
            print("Bell sound loaded successfully")
        except pygame.error as e:
            print(f"Could not load bell.wav: {e}")
            print("Creating a simple beep sound as fallback")
            # Create a simple beep sound programmatically as fallback
            self.create_beep_sound()
    
    def create_beep_sound(self):
        """Create a simple beep sound programmatically"""
        try:
            # Create a simple sine wave beep
            sample_rate = 22050
            duration = 0.3  # 300ms
            frequency = 800  # 800 Hz
            
            frames = int(duration * sample_rate)
            arr = []
            for i in range(frames):
                wave = 4096 * (i / frames) * (1 - i / frames)  # Triangle wave with fade
                wave *= 0.3 * (1 + 0.5 * (i % 100) / 100)  # Add some variation
                arr.append([int(wave), int(wave)])
            
            sound_array = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            self.bell_sound = sound_array
            print("Fallback beep sound created")
        except Exception as e:
            print(f"Could not create fallback sound: {e}")
            self.bell_sound = None
    
    def play_bell(self):
        """Play bell sound"""
        if self.bell_sound:
            try:
                self.bell_sound.play()
            except Exception as e:
                print(f"Error playing bell sound: {e}")
    
    def load_words(self):
        """Load words and find next 60 unshown words"""
        self.current_session_words = []
        
        try:
            with open('wat.csv', 'r+', encoding='utf-8') as file:
                lines = file.readlines()
                
                if not lines:
                    return
                
                # Parse CSV manually for simple r+ handling
                for i, line in enumerate(lines[1:], 1):  # Skip header
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        word = parts[0].strip().upper()
                        response = parts[1].strip()
                        shown = parts[2].strip().lower() == 'true'
                        
                        # If not shown and we need more words for session
                        if not shown and len(self.current_session_words) < self.max_words_per_session:
                            self.current_session_words.append({
                                'word': word,
                                'response': response,
                                'line_index': i
                            })
                
                # If no unshown words found, reset all and start over
                if len(self.current_session_words) == 0:
                    self.reset_all_words()
                    # Try again after reset
                    file.seek(0)
                    lines = file.readlines()
                    for i, line in enumerate(lines[1:], 1):
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            word = parts[0].strip().upper()
                            response = parts[1].strip()
                            
                            if len(self.current_session_words) < self.max_words_per_session:
                                self.current_session_words.append({
                                    'word': word,
                                    'response': response,
                                    'line_index': i
                                })
                                
        except FileNotFoundError:
            self.create_default_csv()
            self.load_words()  # Try again after creating default
    
    def create_default_csv(self):
        """Create default CSV file with more comprehensive SSB-style words"""
        default_words = [
            ("LEADERSHIP", "I lead by example and inspire others to achieve their best"),
            ("COURAGE", "Courage helps me face challenges with determination and confidence"),
            ("TEAMWORK", "I believe in working together to achieve common goals"),
            ("DISCIPLINE", "Self-discipline is the foundation of all achievements"),
            ("RESPONSIBILITY", "I take full responsibility for my actions and decisions"),
            ("INTEGRITY", "Honesty and integrity guide all my interactions"),
            ("DEDICATION", "I am dedicated to excellence in everything I undertake"),
            ("CONFIDENCE", "Self-confidence enables me to tackle any challenge"),
            ("SACRIFICE", "I am willing to sacrifice personal comfort for the greater good"),
            ("ADVENTURE", "I embrace adventure as an opportunity for growth and learning"),
            ("DETERMINATION", "My determination helps me overcome all obstacles"),
            ("LOYALTY", "Loyalty to my country and comrades is my highest priority"),
            ("FRIENDSHIP", "True friendship is built on trust and mutual respect"),
            ("SERVICE", "Service to the nation fills me with pride and purpose"),
            ("HONOR", "Honor and dignity are the pillars of my character"),
            ("MOTIVATION", "I stay motivated by focusing on my goals and aspirations"),
            ("CHALLENGE", "Every challenge is an opportunity to prove my capabilities"),
            ("SUCCESS", "Success comes through hard work and perseverance"),
            ("ACHIEVEMENT", "Achievement is the result of dedication and focused effort"),
            ("EXCELLENCE", "I strive for excellence in every task I undertake"),
            ("STRENGTH", "Physical and mental strength help me serve my nation better"),
            ("WISDOM", "Wisdom guides my decisions and actions in all situations"),
            ("JUSTICE", "Justice and fairness are essential for a harmonious society"),
            ("PATRIOTISM", "My love for my country motivates me to serve with pride"),
            ("BRAVERY", "Bravery is not the absence of fear but acting despite it"),
            ("PERSEVERANCE", "Perseverance helps me continue despite temporary setbacks"),
            ("AMBITION", "My ambition drives me to achieve greater heights"),
            ("COMPASSION", "Compassion for others makes me a better human being"),
            ("RESILIENCE", "Resilience helps me bounce back from any adversity"),
            ("INNOVATION", "Innovation and creativity help solve complex problems"),
            ("TRUST", "Trust is the foundation of all meaningful relationships"),
            ("HOPE", "Hope gives me strength during difficult times"),
            ("PATIENCE", "Patience helps me make better decisions and avoid mistakes"),
            ("EMPATHY", "Empathy helps me understand and connect with others"),
            ("VISION", "A clear vision guides my path toward achieving my goals"),
            ("COMMITMENT", "My commitment to my duties is unwavering and absolute"),
            ("COOPERATION", "Cooperation with others leads to mutual success"),
            ("INITIATIVE", "I take initiative to solve problems and improve situations"),
            ("ADAPTABILITY", "Adaptability helps me thrive in changing circumstances"),
            ("RELIABILITY", "Others can count on me to fulfill my commitments"),
            ("OPTIMISM", "Optimism helps me see opportunities in every situation"),
            ("RESPECT", "I treat everyone with dignity and respect"),
            ("KINDNESS", "Kindness and compassion make the world a better place"),
            ("GENEROSITY", "Generosity of spirit enriches both giver and receiver"),
            ("HUMILITY", "Humility keeps me grounded while striving for excellence"),
            ("GRATITUDE", "Gratitude for opportunities motivates me to give my best"),
            ("FOCUS", "Focus and concentration help me achieve my objectives"),
            ("ENERGY", "My energy and enthusiasm inspire others around me"),
            ("BALANCE", "Balance in life helps me maintain effectiveness in all areas"),
            ("GROWTH", "Continuous growth and learning are essential for success"),
            ("FAMILY", "Family provides the support and values that guide my life"),
            ("DUTY", "Duty to my nation and society comes before personal interests"),
            ("PEACE", "I work toward creating peace and harmony in society"),
            ("PROGRESS", "Progress comes through continuous effort and improvement"),
            ("KNOWLEDGE", "Knowledge empowers me to make informed decisions"),
            ("HEALTH", "Good health enables me to serve my nation effectively"),
            ("FUTURE", "I work today to build a better future for my country"),
            ("VICTORY", "Victory is achieved through preparation and determination"),
            ("TRAINING", "Rigorous training prepares me for any challenge"),
            ("MISSION", "I am committed to accomplishing every mission successfully")
        ]
        
        with open('wat.csv', 'w', newline='', encoding='utf-8') as file:
            file.write('word,best_response,shown\n')
            for word, response in default_words:
                file.write(f'{word},{response},false\n')
    
    def mark_word_shown(self, line_index):
        """Mark a specific word as shown in the CSV file"""
        try:
            with open('wat.csv', 'r+', encoding='utf-8') as file:
                lines = file.readlines()
                
                if line_index < len(lines):
                    parts = lines[line_index].strip().split(',')
                    if len(parts) >= 3:
                        # Change false to true
                        parts[2] = 'true'
                        lines[line_index] = ','.join(parts) + '\n'
                        
                        # Write back
                        file.seek(0)
                        file.writelines(lines)
                        file.truncate()
                        
        except Exception as e:
            print(f"Error marking word as shown: {e}")
    
    def reset_all_words(self):
        """Reset all words to false"""
        try:
            with open('wat.csv', 'r+', encoding='utf-8') as file:
                lines = file.readlines()
                
                for i in range(1, len(lines)):  # Skip header
                    parts = lines[i].strip().split(',')
                    if len(parts) >= 3:
                        parts[2] = 'false'
                        lines[i] = ','.join(parts) + '\n'
                
                file.seek(0)
                file.writelines(lines)
                file.truncate()
                
        except Exception as e:
            print(f"Error resetting words: {e}")
    
    def prepare_session(self):
        """Load next session words"""
        self.load_words()
    
    def draw_text_centered(self, text, font, color, y_offset=0):
        """Draw text centered on screen"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset)
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_instructions(self):
        """Draw instruction screen - waiting for Enter to start"""
        # Title - larger and more prominent
        title_offset = int(-300 * SCALE_FACTOR)
        title_surface = self.timer_font.render("SSB Word Association Test", True, GREEN)
        title_rect = title_surface.get_rect()
        title_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + title_offset)
        self.screen.blit(title_surface, title_rect)
        
        # Main instructions with better spacing
        instructions = [
            "","","",            
            "INSTRUCTIONS:",
            "",
            "",
            "",
            "• You will see 60 words, each displayed for 15 seconds.",
            "Write one Sentence on each Word",
            "CONTROLS:",
            "",
            "• SPACEBAR: Pause/Resume during test",
            "",
            "• ESC: Exit application",
            "",
            "Press ENTER to start the session"
        ]
        
        y_start = int(-150 * SCALE_FACTOR)
        line_spacing = int(35 * SCALE_FACTOR)
        
        for i, instruction in enumerate(instructions):
            if instruction == "INSTRUCTIONS:" or instruction == "CONTROLS:":
                color = BLUE
                font = self.instruction_font
            elif instruction == "Press ENTER to start the session":
                color = GREEN
                font = self.timer_font
            elif instruction.startswith("•"):
                color = WHITE
                font = self.instruction_font
            else:
                color = WHITE
                font = self.instruction_font
            
            if instruction.strip():
                text_surface = font.render(instruction, True, color)
                text_rect = text_surface.get_rect()
                text_rect.centerx = SCREEN_WIDTH // 2
                text_rect.y = y_start + (i * line_spacing)
                self.screen.blit(text_surface, text_rect)
        
        # Show progress at bottom with more space
        try:
            with open('wat.csv', 'r', encoding='utf-8') as file:
                lines = file.readlines()
                total_words = len(lines) - 1  # Exclude header
                shown_count = sum(1 for line in lines[1:] if line.strip().split(',')[2].strip().lower() == 'true')
                progress_text = f"Progress: {shown_count}/{total_words} words completed"
                progress_offset = int(350 * SCALE_FACTOR)
                self.draw_text_centered(progress_text, self.small_font, DARK_GRAY, progress_offset)
        except:
            pass
    
    def draw_word_screen(self):
        """Draw the current word and timer"""
        if self.current_word_index < len(self.current_session_words):
            current_word_data = self.current_session_words[self.current_word_index]
            current_word = current_word_data['word']
            
            # Calculate remaining time
            if not self.is_paused:
                elapsed_time = time.time() - self.start_time
                remaining_time = max(0, self.word_duration - elapsed_time)
            else:
                remaining_time = getattr(self, 'paused_remaining_time', self.word_duration)
            
            # Draw word (large and prominent)
            self.draw_text_centered(current_word, self.word_font, WHITE, 0)
            
            # Draw timer
            timer_text = f"{int(remaining_time)}"
            timer_color = RED if remaining_time <= 3 else GREEN
            timer_offset = int(-120 * SCALE_FACTOR)
            self.draw_text_centered(timer_text, self.timer_font, timer_color, timer_offset)
            
            # Draw session progress
            progress_text = f"{self.current_word_index + 1} / {len(self.current_session_words)}"
            progress_offset = int(100 * SCALE_FACTOR)
            self.draw_text_centered(progress_text, self.instruction_font, BLUE, progress_offset)
            
            # Draw pause indicator
            if self.is_paused:
                pause_offset = int(150 * SCALE_FACTOR)
                resume_offset = int(180 * SCALE_FACTOR)
                self.draw_text_centered("PAUSED", self.instruction_font, GREEN, pause_offset)
                self.draw_text_centered("Press SPACEBAR to resume", self.small_font, WHITE, resume_offset)
            
            # Check if time is up
            if not self.is_paused and remaining_time <= 0:
                self.next_word()
    
    def draw_session_complete_screen(self):
        """Draw session completion screen"""
        complete_offset = int(-100 * SCALE_FACTOR)
        completed_offset = int(-50 * SCALE_FACTOR)
        
        self.draw_text_centered("Session Complete!", self.instruction_font, GREEN, complete_offset)
        
        completed_text = f"You completed {len(self.current_session_words)} words"
        self.draw_text_centered(completed_text, self.instruction_font, WHITE, completed_offset)
        
        # Check if more words are available
        try:
            with open('wat.csv', 'r', encoding='utf-8') as file:
                lines = file.readlines()
                unshown_count = sum(1 for line in lines[1:] if line.strip().split(',')[2].strip().lower() == 'false')
                
                if unshown_count > 0:
                    next_text = f"{unshown_count} words remaining"
                    self.draw_text_centered(next_text, self.instruction_font, BLUE, 0)
                    next_session_offset = int(50 * SCALE_FACTOR)
                    self.draw_text_centered("Press ENTER for next session", self.instruction_font, WHITE, next_session_offset)
                else:
                    self.draw_text_centered("All words completed!", self.instruction_font, GREEN, 0)
                    restart_offset = int(50 * SCALE_FACTOR)
                    self.draw_text_centered("Press ENTER to restart from beginning", self.instruction_font, WHITE, restart_offset)
        except:
            next_session_offset = int(50 * SCALE_FACTOR)
            self.draw_text_centered("Press ENTER for next session", self.instruction_font, WHITE, next_session_offset)
        
        quit_offset = int(100 * SCALE_FACTOR)
        self.draw_text_centered("Press ESC to quit", self.small_font, DARK_GRAY, quit_offset)
    
    def start_session(self):
        """Start a new session"""
        if len(self.current_session_words) > 0:
            self.is_running = True
            self.is_paused = False
            self.waiting_for_start = False
            self.current_word_index = 0
            self.start_time = time.time()
            # Play bell sound when starting session
            self.play_bell()
    
    def pause_resume(self):
        """Toggle pause/resume"""
        if not self.is_running or self.waiting_for_start:
            return
            
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.start_time = time.time() - (self.word_duration - self.paused_remaining_time)
            self.play_bell()  # Play bell when resuming
        else:
            # Pause
            self.is_paused = True
            elapsed_time = time.time() - self.start_time
            self.paused_remaining_time = max(0, self.word_duration - elapsed_time)
            self.play_bell()  # Play bell when pausing
    
    def next_word(self):
        """Move to next word"""
        # Mark current word as shown
        if self.current_word_index < len(self.current_session_words):
            word_data = self.current_session_words[self.current_word_index]
            self.mark_word_shown(word_data['line_index'])
        
        self.current_word_index += 1
        
        if self.current_word_index < len(self.current_session_words):
            self.start_time = time.time()
            # Play bell sound when changing to next word
            self.play_bell()
        else:
            # Session complete
            self.is_running = False
            self.waiting_for_start = True
            self.load_words()  # Prepare next session
            # Play bell sound when session completes
            self.play_bell()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_RETURN:
                    if self.waiting_for_start:
                        self.start_session()
                
                elif event.key == pygame.K_SPACE:
                    if self.is_running and not self.waiting_for_start:
                        self.pause_resume()
        
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            
            # Clear screen with dark background
            self.screen.fill(BLACK)
            
            # Draw appropriate screen
            if self.waiting_for_start:
                if not self.is_running:
                    # Either initial start or session complete
                    if self.current_word_index == 0:
                        self.draw_instructions()
                    else:
                        self.draw_session_complete_screen()
            elif self.is_running:
                self.draw_word_screen()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        # Save progress before quitting
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = WATApp()
    app.run()
