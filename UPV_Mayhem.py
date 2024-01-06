import tkinter as tk, random, pygame.mixer
from tkinter import ttk, messagebox
from PIL import ImageTk, Image

window = tk.Tk()
window.title('UPV Mayhem')
window.geometry('1140x760')

button_style = ttk.Style()
button_style.configure('Custom.TButton', font=('Tahoma', 15))
pygame.mixer.init()

class BaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller 

    def setup_background(self):
        bg = Image.open("images/game-intro-bg.png")
        self.bg_tk = ImageTk.PhotoImage(bg)
        self.bg_canvas = tk.Canvas(self, width=1140, height=760)
        self.bg_canvas.pack()
        self.bg_canvas.create_image(0, 0, image=self.bg_tk, anchor='nw')
    
    def play_background(self):
        play_bg = Image.open("images/classroom.png")
        self.play_bg_tk = ImageTk.PhotoImage(play_bg)
        self.play_bg_canvas = tk.Canvas(self, width=1140, height=760)
        self.play_bg_canvas.pack()
        self.play_bg_canvas.create_image(0, 0, image=self.play_bg_tk, anchor='nw')
    
    def display_image_bg(self, image_path, position, size):
        image = Image.open(image_path)
        image_rs = image.resize(size)
        image_tk = ImageTk.PhotoImage(image_rs)
        self.bg_canvas.create_image(*position, anchor='nw', image=image_tk)
        self.bg_canvas.image = image_tk
    
    def display_image_play(self, image_path, position, size):
        image = Image.open(image_path)
        image_rs = image.resize(size)
        image_tk = ImageTk.PhotoImage(image_rs)
        image_id = self.play_bg_canvas.create_image(*position, anchor='nw', image=image_tk)
        self.play_bg_canvas.image = image_tk

        self.after(3500, lambda: self.play_bg_canvas.delete(image_id))
     
    def navigation_button(self, text, target_page, position):
        button = ttk.Button(self, text=text, command=lambda: show_page(target_page))
        self.bg_canvas.create_window(*position, anchor='nw', window=button)

    def bg_music(self, audio_path, vol, num):
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play(loops=num)
    
    def play_audio(self, audio_path, num):
        sound = pygame.mixer.Sound(audio_path)
        sound.play(loops=num)

class HomePage(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.setup_background()
        self.bg_canvas.create_text(575, 270, text='UPV Mayhem', font=('Mareka', 175), fill='black')
        self.bg_canvas.create_text(580, 272.5, text='UPV Mayhem', font=('Mareka', 175), fill='#f2ea67')
        self.navigation_button('Play', LevelPage, (380, 450))
        self.navigation_button('Help', HelpPage1, (685, 450))

class LevelPage(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.setup_background()
        self.navigation_button('Easy', EasyPage, (525, 270))
        self.navigation_button('Medium', MediumPage, (525, 370))
        self.navigation_button('Hard', HardPage, (525, 470))

class PlayPage(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.play_background()
        self.bg_music("audio/mp3_abloom_takearide_full.mp3", 0.10, -1) #-1 == infinite
        self.fishing_net()
        self.falling_objects = []
        self.init_score = 0
        self.difficulty = {'easy':{'timer': 140, 'speed': 7.5},
                           'medium':{'timer': 110, 'speed': 8}, 
                           'hard':{'timer': 100, 'speed': 8.75}}
        
    def fishing_net(self):
        fn = Image.open('images/fishing-net-cut.png')
        fn_rs = fn.resize((153, 171))
        self.fn_tk = ImageTk.PhotoImage(fn_rs)  # Attach to self to prevent garbage collection
        self.fn_tk_id = self.play_bg_canvas.create_image(random.randint(0, 1140 - 250), 565, anchor='nw', image=self.fn_tk)
        self.master.bind("<Up>", self.up)
        self.master.bind("<Down>", self.down)
        self.master.bind("<Left>", self.left)  
        self.master.bind("<Right>", self.right)  

    def up(self, event):
        self.play_bg_canvas.move(self.fn_tk_id, 0, -65)
    def down(self, event):
        self.play_bg_canvas.move(self.fn_tk_id, 0, 65)
    def left(self, event):
        self.play_bg_canvas.move(self.fn_tk_id, -65, 0)
    def right(self, event):
        self.play_bg_canvas.move(self.fn_tk_id, 65, 0)
    
    def init_timer(self, page_class):
        if page_class == EasyPage:
            self.remaining_time = self.difficulty['easy']['timer']
        elif page_class == MediumPage:
            self.remaining_time = self.difficulty['medium']['timer']
        else:
            self.remaining_time = self.difficulty['hard']['timer']
        
        self.elapsed_time = tk.StringVar()

        timer_label = tk.Label(self, textvariable=self.elapsed_time, font=('Tahoma', 13), fg='#f1eb92', bg='#494240')
        timer_label.config(padx=5, pady=2)
        self.timer = self.play_bg_canvas.create_window(1050, 10, anchor='nw', window=timer_label)
        self.update_timer(page_class)  # update timer call

    def update_timer(self, page_class):
        self.elapsed_time.set(f"Time: {self.remaining_time}s")

        if self.remaining_time > -1:
            self.remaining_time -= 1
            self.after(1000, lambda: self.update_timer(page_class))
            self.time_check(page_class)

        if self.init_score >= 100 and self.remaining_time > -1:
            result = messagebox.askquestion("", "Do you wish to play again?")
            if result == 'yes':
                self.page_destroy()
                show_page(HomePage)
            elif result == 'no':
                self.page_destroy()
                show_page(GameWon)
        
        elif self.remaining_time == -1 and self.init_score < 100:
            self.after(1500)
            result = messagebox.askquestion("", "Do you wish to try again?")
            if result == 'yes':
                self.page_destroy()
                show_page(HomePage)
            elif result == 'no':
                self.page_destroy()
                show_page(GameOver)

    def time_check(self, pageclass):
        if pageclass == EasyPage:
            target_time = self.difficulty['easy']['timer']
        elif pageclass == MediumPage:
            target_time = self.difficulty['medium']['timer']
        elif pageclass == HardPage:
            target_time = self.difficulty['hard']['timer']

        if self.remaining_time == target_time - 1:
            self.TRES_loop()
            self.display_image_play("images/catch_TRES.png", (20, 670), (125, 74))
        elif self.remaining_time == target_time - 6:
            self.oble_loop()
            self.display_image_play("images/dodge-oble.png", (20, 670), (125, 74))
        elif self.remaining_time == target_time - 11:
            self.UNO_loop()
            self.display_image_play("images/catch_UNO.png", (20, 670), (125, 74))
        elif self.remaining_time == target_time - 21:
            self.bb_loop()
            self.display_image_play("images/dodge-bbook.png", (20, 670), (125, 74))
        elif self.remaining_time == target_time - 39:
            self.portal_loop()
            self.display_image_play("images/dodge_portal.png", (20, 670), (125, 74))
        elif self.remaining_time == target_time - 45:
            self.bat_loop()
            self.display_image_play("images/dodge_bats.png", (20, 670), (125, 74))

    def create_falling_object(self, image_path, resize_dimensions, points):
        x = random.randint(0, self.play_bg_canvas.winfo_reqwidth() - resize_dimensions[0] * 2) # random x position in certain range
        y = 0 
        img = Image.open(image_path) # img open
        img_resized = img.resize(resize_dimensions) # resize
        img_tk = ImageTk.PhotoImage(img_resized) # tk.pi
        falling_obj = self.play_bg_canvas.create_image(x, y, anchor='nw', image=img_tk) # display obj on canvas
        self.falling_objects.append({'id': falling_obj, 'image': img_tk, 'points': points}) # storing info only
        
        self.animate_falling_object(falling_obj, x, y)

    def create_flying_object(self, image_path, resize_dimensions, points):
        x = 0
        y = random.randint(0, self.play_bg_canvas.winfo_reqheight() - resize_dimensions[1] * 2) # random y position in certain range
        img = Image.open(image_path) # img open
        img_resized = img.resize(resize_dimensions) # resize
        img_tk = ImageTk.PhotoImage(img_resized) # tk.pi
        flying_obj = self.play_bg_canvas.create_image(x, y, anchor='nw', image=img_tk) # display obj on canvas
        self.falling_objects.append({'id': flying_obj, 'image': img_tk, 'points': points}) # storing info only
        self.animate_flying_object(flying_obj, x, y)

    def check_collision(self, bbox1, bbox2):
        collission = bbox1[0] < bbox2[2] and bbox1[2] > bbox2[0] and bbox1[1] < bbox2[3] and bbox1[3] > bbox2[1]
        if collission:
            self.play_audio("audio/Item Collect SFX.mp3", 0)
        return collission
    
    def point_counter(self):
        self.current_score = tk.StringVar()
        self.current_score.set("Score: 0")
        score_label = tk.Label(self, textvariable=self.current_score, font=('Tahoma', 13), fg='#f1eb92', bg='#494240')
        score_label.config(padx=5, pady=2)
        self.score = self.play_bg_canvas.create_window(15, 10, anchor='nw', window=score_label)
        
    def update_score(self, object_image_id):
        if self.remaining_time > -1: # update score til 0
            falling_obj = next(obj for obj in self.falling_objects if obj['id'] == object_image_id)
            self.init_score += falling_obj.get('points', 0) # zero in this tuple is for default score # when object id not found
            self.current_score.set(f"Score: {self.init_score}")
        else: # Do not update score once the time is up
            return

    def TRES_loop(self):
        self.create_falling_object("images/TRES.png", (61, 95), points=1)  
        self.after(1500, self.TRES_loop)
    
    def oble_loop(self):
        self.create_falling_object("images/oblation.png", (83, 99), points=-1)  
        self.after(2800, self.oble_loop)

    def UNO_loop(self):
        self.create_falling_object("images/UNO.png", (61, 95), points=3)  
        self.after(3300, self.UNO_loop)
    
    def bb_loop(self):
        self.create_falling_object("images/blue-book.png", (72, 106), points=-3)  
        self.after(4500, self.bb_loop)
    
    def portal_loop(self):
        self.create_flying_object("images/upv-portal.png", (77, 96), points=-4)  
        self.after(9000, self.portal_loop)
    
    def bat_loop(self):
        self.create_flying_object("images/bat.png", (77, 93), points=-5)
        self.after(12000, self.bat_loop)

    def page_destroy(self):
        pygame.mixer.music.stop()
        super().destroy()
    
class EasyPage(PlayPage):
    def __init__(self, parent, controller):
        PlayPage.__init__(self, parent, controller)
        self.init_timer(EasyPage)
        self.point_counter()

    def animate_falling_object(self, object_image_id, x, y):
        speed = self.difficulty['easy']['speed']
        if self.remaining_time < 130 and self.remaining_time >= 40:
            speed *= 1.75
        elif self.remaining_time < 40 and self.remaining_time >= 0:
            speed *= 2
        
        if y < self.play_bg_canvas.winfo_reqheight():
            self.play_bg_canvas.move(object_image_id, 0, speed)
            y += speed
            net_bbox = self.play_bg_canvas.bbox(self.fn_tk_id)
            obj_bbox = self.play_bg_canvas.bbox(object_image_id)

            if self.check_collision(net_bbox, obj_bbox):
                self.play_bg_canvas.delete(object_image_id)
                self.update_score(object_image_id)  # pass the object ID to update_score
            else:
                self.after(50, self.animate_falling_object, object_image_id, x, y)  # Schedule the next step

        else:
            self.play_bg_canvas.delete(object_image_id)

    def animate_flying_object(self, object_image_id, x, y):
        speed = 15
        if self.remaining_time < 70 and self.remaining_time >= 0:
            speed *= 1.5

        if x < self.play_bg_canvas.winfo_reqwidth():
            self.play_bg_canvas.move(object_image_id, speed, 0)
            x += speed
            net_bbox = self.play_bg_canvas.bbox(self.fn_tk_id)
            obj_bbox = self.play_bg_canvas.bbox(object_image_id)

            if self.check_collision(net_bbox, obj_bbox):
                self.play_bg_canvas.delete(object_image_id)
                self.update_score(object_image_id)  # Pass the object ID to update_score
            else:
                self.after(50, self.animate_flying_object, object_image_id, x, y) 
                
        else:
            self.play_bg_canvas.delete(object_image_id)

class MediumPage(PlayPage):
    def __init__(self, parent, controller):
        PlayPage.__init__(self, parent, controller)
        self.init_timer(MediumPage)
        self.point_counter()
    
    def animate_falling_object(self, object_image_id, x, y):
        speed = self.difficulty['medium']['speed']
        if self.remaining_time < 100 and self.remaining_time >= 30:
            speed *= 1.75
        elif self.remaining_time < 30 and self.remaining_time >= 0:
            speed *= 2

        if y < self.play_bg_canvas.winfo_reqheight():
            self.play_bg_canvas.move(object_image_id, 0, speed)
            y += speed
            net_bbox = self.play_bg_canvas.bbox(self.fn_tk_id)
            obj_bbox = self.play_bg_canvas.bbox(object_image_id)

            if self.check_collision(net_bbox, obj_bbox):
                self.play_bg_canvas.delete(object_image_id)
                self.update_score(object_image_id)
            else:
                self.after(50, self.animate_falling_object, object_image_id, x, y)

        else:
            self.play_bg_canvas.delete(object_image_id)

    def animate_flying_object(self, object_image_id, x, y):
        speed = 15
        if self.remaining_time < 55 and self.remaining_time >= 0:
            speed *= 1.75

        if x < self.play_bg_canvas.winfo_reqwidth():
            self.play_bg_canvas.move(object_image_id, speed, 0)
            x += speed
            net_bbox = self.play_bg_canvas.bbox(self.fn_tk_id)
            obj_bbox = self.play_bg_canvas.bbox(object_image_id)

            if self.check_collision(net_bbox, obj_bbox):
                self.play_bg_canvas.delete(object_image_id)
                self.update_score(object_image_id)
            else:
                self.after(50, self.animate_flying_object, object_image_id, x, y)

        else:
            self.play_bg_canvas.delete(object_image_id)

class HardPage(PlayPage):
    def __init__(self, parent, controller):
        PlayPage.__init__(self, parent, controller)
        self.init_timer(HardPage)
        self.point_counter()

    def animate_falling_object(self, object_image_id, x, y):
        speed = self.difficulty['hard']['speed']
        if self.remaining_time < 90 and self.remaining_time >= 30:
            speed *= 1.75
        elif self.remaining_time < 35 and self.remaining_time >= 0:
            speed *= 2

        if y < self.play_bg_canvas.winfo_reqheight():
            self.play_bg_canvas.move(object_image_id, 0, speed)
            y += speed
            net_bbox = self.play_bg_canvas.bbox(self.fn_tk_id)
            obj_bbox = self.play_bg_canvas.bbox(object_image_id)

            if self.check_collision(net_bbox, obj_bbox):
                self.play_bg_canvas.delete(object_image_id)
                self.update_score(object_image_id)
            else:
                self.after(50, self.animate_falling_object, object_image_id, x, y)
        else:
            self.play_bg_canvas.delete(object_image_id)

    def animate_flying_object(self, object_image_id, x, y):
        speed = 15  
        if self.remaining_time < 50 and self.remaining_time >= 0:
            speed *= 1.8

        if x < self.play_bg_canvas.winfo_reqwidth():
            self.play_bg_canvas.move(object_image_id, speed, 0)
            x += speed
            net_bbox = self.play_bg_canvas.bbox(self.fn_tk_id)
            obj_bbox = self.play_bg_canvas.bbox(object_image_id)

            if self.check_collision(net_bbox, obj_bbox):
                self.play_bg_canvas.delete(object_image_id)
                self.update_score(object_image_id) 
            else:
                self.after(50, self.animate_flying_object, object_image_id, x, y)  
                
        else:
            self.play_bg_canvas.delete(object_image_id)

class GameOver(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.setup_background()
        self.display_image_bg("images/game_over.png", (105, 160), (941, 552))
        self.bg_music("audio/Oh No.mp3", 0.50, 0)

class GameWon(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.setup_background()
        self.display_image_bg("images/you_win.png", (105, 160), (941, 552))
        self.bg_music("audio/You Won.mp3", 0.50, 0) 

class HelpPage1(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.setup_background()
        self.display_image_bg("images/chancellor.png", (105, 160), (941, 552))
        self.navigation_button('Home', HomePage, (20, 20))
        self.navigation_button('More', HelpPage2, (1020, 20))
        
class HelpPage2(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.setup_background()
        self.display_image_bg("images/arrow-keys.png", (190, 300), (781, 242))
        self.navigation_button('Back', HelpPage1, (20, 20))
        self.navigation_button('More', HelpPage3, (1020, 20))

class HelpPage3(BaseFrame):
    def __init__(self, parent, controller):
        BaseFrame.__init__(self, parent, controller)
        self.setup_background()
        self.display_image_bg("images/point-instru.png", (70, 100), (1000, 620))
        self.navigation_button('Back', HelpPage2, (20, 20))
    
def show_page(page_class):
    page = page_class(window, controller=None)
    page.place(in_=window, x=0, y=0, relwidth=1, relheight=1)

home_page = HomePage(window, controller=None)
home_page.place(in_=window, x=0, y=0, relwidth=1, relheight=1)

window.resizable(False, False)
window.mainloop()