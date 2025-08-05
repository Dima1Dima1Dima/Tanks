import pygame
import random
import math
import time
import sys

from platform_module import Platform
from game_data import load_game_data, save_game_data

# Инициализация Pygame
pygame.init()

# Получение информации о дисплее
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h

FPS = 75

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
YELLOW_S = (255, 255, 125)
GRAY = (50, 50, 50)
DARK_GRAY = (100, 100, 100)
CYAN = (0, 200, 200)

colors = [
    (255, 255, 255),  # Белый
    (200, 200, 255),  # Светло-синий
    (255, 200, 200),  # Светло-красный
    (200, 255, 200),  # Светло-зеленый
    (255, 255, 200),  # Светло-желтый
]

# Создание окна
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Танковая битва")

# Установление времени обновления
clock = pygame.time.Clock()

# Размеры шрифта зависят от размера экрана
font_size = int(screen_width * 0.018)  # Пример зависимости от ширины экрана
font_menu_size = int(screen_width * 0.024)
font_home_size = int(screen_width * 0.2)
font_o_size = int(screen_width * 0.47)

# Инициализация шрифтов с учетом расчетных размеров
font = pygame.font.Font(None, font_size)
font_menu = pygame.font.Font(None, font_menu_size)
font_home = pygame.font.Font(None, font_home_size)
font_o = pygame.font.Font(None, font_o_size)

updates = 4
naw_updates = 4

# Загрузка звуков
shot_sound = pygame.mixer.Sound('assets/shoot.mp3')
# Загрузка данных при запуске
game_data = load_game_data()
current_volume = game_data.get('current_volume', 0.5)  # Громкость по умолчанию
is_sound_on = game_data.get('is_sound_on', True)      # Состояние звука по умолчанию

button_sound = pygame.mixer.Sound('assets/button.mp3')
# Загрузка данных при запуске
game_data = load_game_data()
current_buttn_volume = game_data.get('button_sound', 0.5)  # Громкость по умолчанию
is_button_on = game_data.get('is_button_on', True)      # Состояние звука по умолчанию

# Громкость звука1
shot_sound.set_volume(current_volume)

# Громкость звука2
button_sound.set_volume(current_buttn_volume)


background = pygame.image.load('assets/fon/fon.pnj')
background = pygame.transform.scale(background, (screen_width, screen_height))

fon_menu = pygame.image.load('assets/fon/fon_menu.pnj')
fon_menu = pygame.transform.scale(fon_menu, (screen_width, screen_height))

fon_load_menu = pygame.image.load('assets/fon/fon_load_menu.pnj')
fon_load_menu = pygame.transform.scale(fon_load_menu, (screen_width, screen_height))

fon_pause = pygame.image.load('assets/fon/fon_pause.pnj')
fon_pause = pygame.transform.scale(fon_pause, (screen_width, screen_height))

fon_game_menu = pygame.image.load('assets/fon/fon_menu_game.pnj')
fon_game_menu = pygame.transform.scale(fon_game_menu, (screen_width, screen_height))

# Класс Tank
class Tank:
    def __init__(self, x, y, color, controls, initial_angle=0):
        self.x = x
        self.y = y
        self.width = screen_width - screen_width + 100
        self.height = screen_height - screen_height + 50
        self.color = color
        self.angle = initial_angle  # Устанавливаем начальный угол
        self.speed = 4
        self.speed_no = 2
        self.controls = controls
        self.health = 100
        self.bullets = []
        self.last_shot = 0  # Время последнего выстрела
        self.shoot_cooldown = 3  # Кулдаун в секундах
        self.reload_message_time = 0  # Время, до которого показывается сообщение о перезарядке
        self.bullets_shift = []
        self.last_shot_shift = 0
        self.shoot_cooldown_shift = 0.1  # Задержка между выстрелами (секунды)
        self.reload_message_time_shift = 0

        # Загрузка изображений танка и его башни
        self.body_image = pygame.image.load('assets/Tank1.png')  # Замените на путь к изображению корпуса танка
        self.barrel_image = pygame.image.load('assets/Turret1.png')  # Замените на путь к изображению дула танка

        # Масштабирование изображений
        self.body_image = pygame.transform.scale(self.body_image, (self.width, self.height))
        self.barrel_image = pygame.transform.scale(self.barrel_image, (screen_width - screen_width + 90, screen_height - screen_height + 50))  # Длина дула, ширина

    def draw(self, screen):
        # Рисуем корпус танка с учетом угла поворота
        rotated_body = pygame.transform.rotate(self.body_image, self.angle)
        body_rect = rotated_body.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_body, body_rect.topleft)

        # Рисуем дуло танка с учетом угла поворота
        rotated_barrel = pygame.transform.rotate(self.barrel_image, self.angle)
        barrel_length = 30
        barrel_x = self.x + self.width // 2 + math.cos(math.radians(self.angle)) * barrel_length
        barrel_y = self.y + self.height // 2 - math.sin(math.radians(self.angle)) * barrel_length
        barrel_rect = rotated_barrel.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_barrel, barrel_rect.topleft)

        # Отображение сообщения о перезарядке, если оно активно
        if time.time() < self.reload_message_time:
            font = pygame.font.Font(None, 24)  # Шрифт для надписи
            text = font.render("Перезарядка!", True, (255, 0, 0))  # Красный текст
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y - 20))  # Позиция над танком
            screen.blit(text, text_rect)

    def move(self, keys):
        if keys[self.controls["left"]]:
            self.angle += 1.5
        if keys[self.controls["right"]]:
            self.angle -= 1.5
        if keys[self.controls["up"]]:
            self.x += math.cos(math.radians(self.angle)) * self.speed
            self.y -= math.sin(math.radians(self.angle)) * self.speed
        if keys[self.controls["down"]]:
            self.x -= math.cos(math.radians(self.angle)) * self.speed_no
            self.y += math.sin(math.radians(self.angle)) * self.speed_no

        # Стрельба из пулемета для танка1
        if keys[controls_tank1["shoot_machine_gun"]]:
            tank1.shoot_machine_gun()

        # Стрельба из пулемета для танка2
        if keys[controls_tank2["shoot_machine_gun"]]:
            tank2.shoot_machine_gun()

        # Ограничение движения танка в пределах экрана
        self.x = max(0, min(screen_width - self.width, self.x))
        self.y = max(0, min(screen_height - self.height, self.y))

    def shoot(self):
        current_time = time.time()  # Получаем текущее время
        if current_time - self.last_shot >= self.shoot_cooldown:  # Проверяем кулдаун
            bullet = Bullet(self.x + self.width // 2, self.y + self.height // 2, self.angle, self.color)
            self.bullets.append(bullet)
            self.last_shot = current_time  # Обновляем время последнего выстрела
            self.reload_message_time = 0  # Очищаем сообщение о перезарядке

            try:
                if shot_sound:
                    shot_sound.play()
            except NameError:
                pass  # Игнорируем, если звук выстрела не определен
            # Возвращаем True, чтобы указать, что выстрел произошел
            return True
        else:
            # Установка времени, до которого будет отображаться сообщение о перезарядке
            self.reload_message_time = time.time() + 1  # Сообщение будет отображаться 1 секунду
            # Возвращаем False, чтобы указать, что выстрел не произошел
            return False

    def shoot_machine_gun(self):
        current_time = time.time()
        if current_time - self.last_shot >= 0.1:  # Более частый кулдаун для пулемета
            bullet = MachineGun(self.x + self.width // 2, self.y + self.height // 2, self.angle, self.color)
            self.bullets_shift.append(bullet)
            self.last_shot = current_time
            try:
                if shot_sound:
                    shot_sound.play()
            except NameError:
                pass
            return True
        else:
            return False

# Класс Bullet
class Bullet:
    def __init__(self, x, y, angle, color=(0, 0, 0)):  # По умолчанию цвет черный (BLACK)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 30
        self.color = color
        self.radius = screen_width - screen_width + screen_height - screen_height + 5

    def move(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def off_screen(self):
        return self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height

    def hit(self, tank):
        if tank.x < self.x < tank.x + tank.width and tank.y < self.y < tank.y + tank.height:
            return True
        return False

class MachineGun(Bullet):
    def __init__(self, x, y, angle, color=(255, 0, 0)):  # По умолчанию цвет красный (RED)
        super().__init__(x, y, angle, color)  # Наследуем все параметры от Bullet
        self.speed = 45  # Увеличиваем скорость пули для пулемета
        self.radius = screen_width - screen_width + screen_height - screen_height + 3  # Размер пуль пулемета меньше

running = True
text_visible = True # Флаг — отображается ли текст
text_visible_F3 = False  # Флаг — отображается ли текст

tank1_score = 0
tank2_score = 0
shot_1 = 0
shot_2 = 0
struck_1 = 0
struck_2 = 0
struck_gun_1 = 0
struck_gun_2 = 0

def draw_text(screen, text, font, color, pos):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=pos)
    screen.blit(rendered_text, text_rect)
    return text_rect  # Возвращаем область текста для обработки кликов

def draw_text_m(screen, text, font, color, pos):
    rendered_text = font.render(text, True, color)
    text_rect_m = rendered_text.get_rect(center=pos)
    screen.blit(rendered_text, text_rect_m)
    return text_rect_m  # Возвращаем область текста для обработки кликов

# Функция для отображения текста
def draw_text_s(surface, text, font, color, position):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=position)
    surface.blit(text_obj, text_rect)

def display_confirmation(screen, clock, font):
    confirmation_running = True
    while confirmation_running:
        screen.fill(DARK_GRAY)
        draw_text(screen, 'Вы уверены, что хотите сбросить состояние игры?', font, (255, 255, 255),
                  (screen_width // 2, screen_height // 3))
        draw_text(screen, "[Y] - Да, [N] - Нет", font, (255, 255, 255), (screen_width // 2, screen_height // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False
        clock.tick(60)

def shop_b(screen, clock, font):
    confirmation_running = True
    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))

        draw_text(screen, 'МАГАЗИН ТАНКОВ', font, (255, 255, 255),
                  (screen_width // 2, 15))

        esc_button = pygame.Rect((screen_width - 135) // 2, 35, 135, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font_menu.render('НАЗАД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        draw_text(screen, 'магазин не доступен', font, (255, 10, 10), (screen_width // 2, screen_height // 3))
        draw_text(screen, 'появится в 4-6 обновлениях', font, (175, 175, 175), (screen_width // 2, (screen_height // 3) + 30))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        return False
        clock.tick(60)

def management(screen, clock, font):
    confirmation_running = True
    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))

        draw_text(screen, 'НАЗНОЧЕНИЕ КЛАВИШ', font, (255, 255, 255),
                  (screen_width // 2, 15))

        esc_button = pygame.Rect((screen_width - 135) // 2, 35, 135, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font_menu.render('НАЗАД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        # текст право
        font_F3_m = pygame.font.Font(None, 60)
        health_text1 = font_F3_m.render(f'управление танком 1:', True, YELLOW_S)
        screen.blit(health_text1, (10, 20))  # Справа, учли ширину текста

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'движение вперед: w', True, YELLOW_S)
        screen.blit(health_text1, (10, 80))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'движение назад: s', True, YELLOW_S)
        screen.blit(health_text1, (10, 120))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'поворот башни влево: a', True, YELLOW_S)
        screen.blit(health_text1, (10, 160))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'поворот башни вправо: d', True, YELLOW_S)
        screen.blit(health_text1, (10, 200))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'выстрел из орудия: spase (пробел)', True, YELLOW_S)
        screen.blit(health_text1, (10, 240))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'пулемет: lshift', True, YELLOW_S)
        screen.blit(health_text1, (10, 280))

        font_F3 = pygame.font.Font(None, 60)
        health_text2 = font_F3.render(f'управление танком 2:', True, YELLOW_S)
        screen.blit(health_text2, (screen_width - health_text2.get_width() - 10, 20))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'движение вперед: стрелка вверх', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 80))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'движение назад: стрелка вниз', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 120))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'поворот башни влево: стрелка влево', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 160))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'поворот башни вправо: стрелка в право', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 200))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'выстрел из орудия: enter', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 240))

        font_F3 = pygame.font.Font(None, 50)
        health_text1 = font_F3.render(f'пулемет: rshift', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 280))


        # общие

        font_mana_1 = pygame.font.Font(None, 50)
        coords_text_b = font_mana_1.render(f'ОБЩИЕ КНОПКИ', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 350))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render (f'сбросить все состояние: "Backspase"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 400))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render(f'открыть сосояние танков в игре: "F3"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 430))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render(f'начать игру с начала: "y"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 490))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render(f'закрыть игру: "Esc"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 520))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render(f'открыть меню: "t"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 550))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render(f'открыть настройки: "j"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 580))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render(f'главное меню игры: "h"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 610))

        font_mana = pygame.font.Font(None, 40)
        coords_text_b = font_mana.render(f'техническая пауза: "g"', True, YELLOW_S)
        screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), 460))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        return False
        clock.tick(60)

def settings_j(screen, clock, font):
    global current_volume, is_sound_on, game_data
    confirmation_running = True
    slider_x = (screen_width // 2) - 100
    slider_y = 300
    slider_width = 200
    slider_height = 20
    slider_button_radius = 15
    slider_button_x = slider_x + int(current_volume * slider_width)

    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))
        draw_text(screen, 'НАСТРОЙКИ', font, WHITE, (screen_width // 2, 15))

        # Кнопка "Назад"
        esc_button = pygame.Rect((screen_width - 175) // 2, 35, 175, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font_menu.render('ЗАКРЫТЬ', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        management_button = pygame.Rect((screen_width - 410) // 2, screen_height - 50, 410, 40)
        pygame.draw.rect(screen, BLACK, management_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, management_button, border_radius=10)
        pygame.draw.rect(screen, (125, 125, 125), management_button)
        reset_text_m = font_menu.render('НАЗНОЧЕНИЕ КЛАВИШ', True, (255, 255, 255))
        screen.blit(reset_text_m, (management_button.x + 5, management_button.y + 5.5))

        # Отображение громкости
        draw_text(screen, f'ГРОМКОСТЬ: {int(current_volume * 100)}%', font, YELLOW, (screen_width // 2, 150))

        # Кнопки "+" и "-"

        plus_button = pygame.Rect((screen_width // 2) + 100, 200, 50, 50)
        pygame.draw.rect(screen, BLACK, plus_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, plus_button, border_radius=10)
        pygame.draw.rect(screen, (0, 250, 0), plus_button)
        reset_text_m = font.render('+', True, (0, 0, 0))
        screen.blit(reset_text_m, (plus_button.x + 20, plus_button.y + 10))

        minus_button = pygame.Rect((screen_width // 2) - 150, 200, 50, 50)
        pygame.draw.rect(screen, BLACK, minus_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, minus_button, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 0), minus_button)
        reset_text_m = font.render('-', True, (0, 0, 0))
        screen.blit(reset_text_m, (minus_button.x + 20, minus_button.y + 10))

        # Ползунок
        pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height), border_radius=10)
        pygame.draw.circle(screen, BLUE, (slider_button_x, slider_y + slider_height // 2), slider_button_radius)

        # Кнопка включения/выключения звука
        sound_button = pygame.Rect((screen_width - 155) // 2, 400, 155, 35)
        pygame.draw.rect(screen, BLACK, sound_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, sound_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), sound_button)
        reset_text_m = font.render('ЗВУК ВКЛ' if is_sound_on else 'ЗВУК ВЫКЛ', True, (255, 255, 255))
        screen.blit(reset_text_m, (sound_button.x + 5, sound_button.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.time.wait(75)
                    pygame.display.flip()
                    pygame.time.wait(75)  # Задержка для визуального эффекта
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        # Сохраняем звук и громкость при выходе
                        game_data['current_volume'] = current_volume
                        game_data['is_sound_on'] = is_sound_on
                        save_game_data(game_data)
                        return False
                    elif management_button.collidepoint(event.pos):
                        pygame.time.wait(200)
                        pygame.display.flip()
                        pygame.time.wait(200)
                        confirm_reset = management(screen, clock, font)
                    elif plus_button.collidepoint(event.pos):
                        current_volume = min(1.0, current_volume + 0.1)
                        is_sound_on = True  # Включаем звук
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        slider_button_x = slider_x + int(current_volume * slider_width)
                    elif minus_button.collidepoint(event.pos):
                        current_volume = max(0.0, current_volume - 0.1)
                        is_sound_on = current_volume > 0  # Выключаем звук, если громкость 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        slider_button_x = slider_x + int(current_volume * slider_width)
                    elif slider_x <= event.pos[0] <= slider_x + slider_width and \
                            slider_y <= event.pos[1] <= slider_y + slider_height:
                        slider_button_x = event.pos[0]
                        current_volume = (slider_button_x - slider_x) / slider_width
                        is_sound_on = current_volume > 0  # Включаем звук, если громкость больше 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                    elif sound_button.collidepoint(event.pos):
                        is_sound_on = not is_sound_on
                        if not is_sound_on:
                            current_volume = 0.0  # Сбрасываем громкость до минимума
                            slider_button_x = slider_x
                        shot_sound.set_volume(current_volume if is_sound_on else 0)

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if slider_x <= event.pos[0] <= slider_x + slider_width and \
                            slider_y <= event.pos[1] <= slider_y + slider_height:
                        slider_button_x = event.pos[0]
                        current_volume = (slider_button_x - slider_x) / slider_width
                        is_sound_on = current_volume > 0  # Включаем звук, если громкость больше 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)

        clock.tick(60)

def settings_m(screen, clock, font):
    global current_volume, is_sound_on, game_data
    confirmation_running = True
    slider_x = (screen_width // 2) - 100
    slider_y = 300
    slider_width = 200
    slider_height = 20
    slider_button_radius = 15
    slider_button_x = slider_x + int(current_volume * slider_width)

    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))
        draw_text(screen, 'НАСТРОЙКИ', font, WHITE, (screen_width // 2, 15))

        # Кнопка "Назад"
        esc_button = pygame.Rect((screen_width - 135) // 2, 35, 135, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font_menu.render('НАЗАД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        management_button = pygame.Rect((screen_width - 410) // 2, screen_height - 50, 410, 40)
        pygame.draw.rect(screen, BLACK, management_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, management_button, border_radius=10)
        pygame.draw.rect(screen, (125, 125, 125), management_button)
        reset_text_m = font_menu.render('НАЗНОЧЕНИЕ КЛАВИШ', True, (255, 255, 255))
        screen.blit(reset_text_m, (management_button.x + 5, management_button.y + 5.5))

        # Отображение громкости
        draw_text(screen, f'ГРОМКОСТЬ: {int(current_volume * 100)}%', font, YELLOW, (screen_width // 2, 150))

        # Кнопки "+" и "-"

        plus_button = pygame.Rect((screen_width // 2) + 100, 200, 50, 50)
        pygame.draw.rect(screen, BLACK, plus_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, plus_button, border_radius=10)
        pygame.draw.rect(screen, (0, 250, 0), plus_button)
        reset_text_m = font.render('+', True, (0, 0, 0))
        screen.blit(reset_text_m, (plus_button.x + 20, plus_button.y + 10))

        minus_button = pygame.Rect((screen_width // 2) - 150, 200, 50, 50)
        pygame.draw.rect(screen, BLACK, minus_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, minus_button, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 0), minus_button)
        reset_text_m = font.render('-', True, (0, 0, 0))
        screen.blit(reset_text_m, (minus_button.x + 20, minus_button.y + 10))

        # Ползунок
        pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height), border_radius=10)
        pygame.draw.circle(screen, BLUE, (slider_button_x, slider_y + slider_height // 2), slider_button_radius)

        # Кнопка включения/выключения звука
        sound_button = pygame.Rect((screen_width - 155) // 2, 400, 155, 35)
        pygame.draw.rect(screen, BLACK, sound_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, sound_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), sound_button)
        reset_text_m = font.render('ЗВУК ВКЛ' if is_sound_on else 'ЗВУК ВЫКЛ', True, (255, 255, 255))
        screen.blit(reset_text_m, (sound_button.x + 5, sound_button.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        # Сохраняем звук и громкость при выходе
                        game_data['current_volume'] = current_volume
                        game_data['is_sound_on'] = is_sound_on
                        save_game_data(game_data)
                        if button_sound:
                            button_sound.play()
                        return False
                    elif management_button.collidepoint(event.pos):
                        pygame.time.wait(100)
                        pygame.display.flip()
                        pygame.time.wait(100)
                        if button_sound:
                            button_sound.play()
                        confirm_reset = management(screen, clock, font)
                    elif plus_button.collidepoint(event.pos):
                        current_volume = min(1.0, current_volume + 0.1)
                        is_sound_on = True  # Включаем звук
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        slider_button_x = slider_x + int(current_volume * slider_width)
                        if button_sound:
                            button_sound.play()
                    elif minus_button.collidepoint(event.pos):
                        current_volume = max(0.0, current_volume - 0.1)
                        is_sound_on = current_volume > 0  # Выключаем звук, если громкость 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        slider_button_x = slider_x + int(current_volume * slider_width)
                        if button_sound:
                            button_sound.play()
                    elif slider_x <= event.pos[0] <= slider_x + slider_width and \
                            slider_y <= event.pos[1] <= slider_y + slider_height:
                        slider_button_x = event.pos[0]
                        current_volume = (slider_button_x - slider_x) / slider_width
                        is_sound_on = current_volume > 0  # Включаем звук, если громкость больше 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        if button_sound:
                            button_sound.play()
                    elif sound_button.collidepoint(event.pos):
                        is_sound_on = not is_sound_on
                        if not is_sound_on:
                            current_volume = 0.0  # Сбрасываем громкость до минимума
                            slider_button_x = slider_x
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        if button_sound:
                            button_sound.play()

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if slider_x <= event.pos[0] <= slider_x + slider_width and \
                            slider_y <= event.pos[1] <= slider_y + slider_height:
                        slider_button_x = event.pos[0]
                        current_volume = (slider_button_x - slider_x) / slider_width
                        is_sound_on = current_volume > 0  # Включаем звук, если громкость больше 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)

        clock.tick(60)

def stats(screen, clock, font):
    confirmation_running = True
    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))

        draw_text(screen, 'СТАТИСТИКА ТАНКОВ', font, (255, 255, 255),
                  (screen_width // 2, 15))

        esc_button = pygame.Rect((screen_width - 135) // 2, 35, 135, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font_menu.render('НАЗАД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        # танк 1
        font_st_m = pygame.font.Font(None, 40)
        tank1_coords_text = font_st_m.render(f'СТАТИСТИКА ТАНКА 1', True, (255, 255, 255))
        screen.blit(tank1_coords_text, (10, 10))


        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'опыт танка: {load_game_data()['poins_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 60))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'очки танка: {load_game_data()['score_tank1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 90))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'монеты: {load_game_data()['coins_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 120))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'с играл каток: {load_game_data()['total_rounds']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 150))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего побед: {load_game_data()['win_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 180))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего поражений: {load_game_data()['por_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 210))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего выстрелов: {load_game_data()['shot_1_shot']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 240))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего попаданий: {load_game_data()['struck_1_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 270))

        # татнк 2
        font_st_m = pygame.font.Font(None, 40)
        tank2_coords_text = font_st_m.render(f'СТАТИСТИКА ТАНКА 2', True, (255, 255, 255))
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 10))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'опыт танка: {load_game_data()['poins_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 60))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'очки танка: {load_game_data()['score_tank2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 90))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'монеты: {load_game_data()['coins_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 120))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'с играл каток: {load_game_data()['total_rounds']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 150))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего побед: {load_game_data()['win_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 180))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего поражений: {load_game_data()['por_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 210))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего выстрелов: {load_game_data()['shot_2_shot']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 240))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего попаданий: {load_game_data()['struck_2_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 270))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()  # Проигрываем звук
                        return False

        clock.tick(60)

def menu(screen, clock, font):
    confirmation_running = True

    # Цвета кнопок
    button_colors = {
        "esc": (200, 10, 10),
        "stats": (10, 255, 10),
        "shop": (200, 200, 200),
        "settings": (10, 255, 10),
        'countdown_tex': (10, 255, 10),
    }

    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))

        draw_text(screen, 'МЕНЮ ТАНКОВ', font, (255, 255, 255),
                  (screen_width // 2, 15))

        # Кнопка "Выход"
        esc_button = pygame.Rect((screen_width - 145) // 2, 35, 145, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=15)
        pygame.draw.rect(screen, button_colors["esc"], esc_button)
        reset_text_m = font_menu.render('ВЫХОД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        # Кнопка "Статистика"
        stats_button = pygame.Rect((screen_width - 235) // 2, 100, 235, 45)
        pygame.draw.rect(screen, BLACK, stats_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, stats_button, border_radius=15)
        pygame.draw.rect(screen, button_colors["stats"], stats_button)
        reset_text_m = font_menu.render('СТАТИСТИКА', True, (255, 255, 255))
        screen.blit(reset_text_m, (stats_button.x + 5, stats_button.y + 5))

        # Кнопка "Магазин"
        shop_button = pygame.Rect((screen_width - 175) // 2, 165, 175, 45)
        pygame.draw.rect(screen, BLACK, shop_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, shop_button, border_radius=15)
        pygame.draw.rect(screen, button_colors["shop"], shop_button)
        reset_text_m = font_menu.render('МАГАЗИН', True, (255, 255, 255))
        screen.blit(reset_text_m, (shop_button.x + 5, shop_button.y + 5))

        # Кнопка "Настройки"
        settings_button = pygame.Rect((screen_width - 225) // 2, 230, 225, 45)
        pygame.draw.rect(screen, BLACK, settings_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, settings_button, border_radius=15)
        pygame.draw.rect(screen, button_colors["settings"], settings_button)
        reset_text_m = font_menu.render('НАСТРОЙКИ', True, (255, 255, 255))
        screen.blit(reset_text_m, (settings_button.x + 5, settings_button.y + 5))

        button_rect = pygame.Rect((screen_width - 215) // 2, 295, 215, 45)
        pygame.draw.rect(screen, BLACK, button_rect.move(2, 2))
        pygame.draw.rect(screen, GREEN, button_rect, border_radius=15)
        pygame.draw.rect(screen, button_colors["countdown_tex"], button_rect)
        reset_text_m = font_menu.render('ТЕХ. ПАУЗА', True, (255, 255, 255))
        screen.blit(reset_text_m, (button_rect.x + 5, button_rect.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    button_colors["esc"] = (255, 0, 0)  # Изменение цвета кнопки
                    pygame.time.wait(75)
                    pygame.display.flip()
                    pygame.time.wait(75)  # Задержка для визуального эффекта
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        button_colors["esc"] = (255, 0, 0)  # Изменение цвета кнопки
                        pygame.time.wait(75)
                        pygame.display.flip()
                        pygame.time.wait(75)  # Задержка для визуального эффекта
                        return False
                    elif stats_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        button_colors["stats"] = (0, 200, 0)
                        pygame.time.wait(200)
                        pygame.display.flip()
                        pygame.time.wait(200)
                        confirm_reset = stats(screen, clock, font)
                    elif shop_button.collidepoint(event.pos):
                        button_colors["shop"] = (200, 200, 200)
                        draw_text(screen, 'магазин сдесь больше не доступен!', font, RED, (screen_width // 2, screen_height // 2))
                        pygame.display.flip()
                        pygame.time.wait(1500)
                    elif settings_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        button_colors["settings"] = (0, 200, 0)
                        pygame.time.wait(200)
                        pygame.display.flip()
                        pygame.time.wait(200)
                        confirm_reset = settings_m(screen, clock, font)
                        if button_sound:
                            button_sound.play()
                    elif button_rect.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        button_colors["countdown_tex"] = (0, 200, 0)
                        pygame.time.wait(200)
                        pygame.display.flip()
                        pygame.time.wait(200)
                        confirm_reset = countdown_tex(screen, screen_width, screen_height)
                        if button_sound:
                            button_sound.play()

            if event.type == pygame.MOUSEBUTTONUP:
                # Возвращаем цвета кнопок в исходное состояние
                button_colors = {
                    "esc": (200, 10, 10),
                    "stats": (10, 255, 10),
                    "shop": (200, 200, 200),
                    "settings": (10, 255, 10),
                    'countdown_tex': (10, 255, 10),
                }

        clock.tick(60)

# в меню игры
def stats_home(screen, clock, font):
    confirmation_running = True
    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))

        draw_text(screen, 'СТАТИСТИКА ТАНКОВ', font, (255, 255, 255),
                  (screen_width // 2, 15))

        esc_button = pygame.Rect((screen_width - 135) // 2, 35, 135, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font_menu.render('НАЗАД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        # танк 1
        font_st_m = pygame.font.Font(None, 40)
        tank1_coords_text = font_st_m.render(f'СТАТИСТИКА ТАНКА 1', True, (255, 255, 255))
        screen.blit(tank1_coords_text, (10, 10))


        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'опыт танка: {load_game_data()['poins_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 60))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'очки танка: {load_game_data()['score_tank1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 90))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'монеты: {load_game_data()['coins_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 120))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'с играл каток: {load_game_data()['total_rounds']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 150))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего побед: {load_game_data()['win_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 180))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего поражений: {load_game_data()['por_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 210))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего выстрелов: {load_game_data()['shot_1_shot']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 240))

        font_st = pygame.font.Font(None, 36)
        tank1_coords_text = font_st.render(f'всего попаданий: {load_game_data()['struck_1_1']}', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 270))

        # татнк 2
        font_st_m = pygame.font.Font(None, 40)
        tank2_coords_text = font_st_m.render(f'СТАТИСТИКА ТАНКА 2', True, (255, 255, 255))
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 10))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'опыт танка: {load_game_data()['poins_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 60))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'очки танка: {load_game_data()['score_tank2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 90))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'монеты: {load_game_data()['coins_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 120))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'с играл каток: {load_game_data()['total_rounds']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 150))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего побед: {load_game_data()['win_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 180))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего поражений: {load_game_data()['por_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 210))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего выстрелов: {load_game_data()['shot_2_shot']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 240))

        font_st = pygame.font.Font(None, 36)
        tank2_coords_text = font_st.render(f'всего попаданий: {load_game_data()['struck_2_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (screen_width - tank2_coords_text.get_width() - 10, 270))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()  # Проигрываем звук
                        loading_screen_button(screen)
                        return False

        clock.tick(60)

def settings_home(screen, clock, font):
    global current_volume, is_sound_on, game_data
    confirmation_running = True
    slider_x = (screen_width // 2) - 100
    slider_y = 300
    slider_width = 200
    slider_height = 20
    slider_button_radius = 15
    slider_button_x = slider_x + int(current_volume * slider_width)

    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))
        draw_text(screen, 'НАСТРОЙКИ', font, WHITE, (screen_width // 2, 15))

        # Кнопка "Назад"
        esc_button = pygame.Rect((screen_width - 135) // 2, 35, 135, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font_menu.render('НАЗАД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        management_button = pygame.Rect((screen_width - 410) // 2, screen_height - 50, 410, 40)
        pygame.draw.rect(screen, BLACK, management_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, management_button, border_radius=10)
        pygame.draw.rect(screen, (125, 125, 125), management_button)
        reset_text_m = font_menu.render('НАЗНОЧЕНИЕ КЛАВИШ', True, (255, 255, 255))
        screen.blit(reset_text_m, (management_button.x + 5, management_button.y + 5.5))

        # Отображение громкости
        draw_text(screen, f'ГРОМКОСТЬ: {int(current_volume * 100)}%', font, YELLOW, (screen_width // 2, 150))

        # Кнопки "+" и "-"

        plus_button = pygame.Rect((screen_width // 2) + 100, 200, 50, 50)
        pygame.draw.rect(screen, BLACK, plus_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, plus_button, border_radius=10)
        pygame.draw.rect(screen, (0, 250, 0), plus_button)
        reset_text_m = font.render('+', True, (0, 0, 0))
        screen.blit(reset_text_m, (plus_button.x + 20, plus_button.y + 10))

        minus_button = pygame.Rect((screen_width // 2) - 150, 200, 50, 50)
        pygame.draw.rect(screen, BLACK, minus_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, minus_button, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 0), minus_button)
        reset_text_m = font.render('-', True, (0, 0, 0))
        screen.blit(reset_text_m, (minus_button.x + 20, minus_button.y + 10))

        # Ползунок
        pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height), border_radius=10)
        pygame.draw.circle(screen, BLUE, (slider_button_x, slider_y + slider_height // 2), slider_button_radius)

        # Кнопка включения/выключения звука
        sound_button = pygame.Rect((screen_width - 155) // 2, 400, 155, 35)
        pygame.draw.rect(screen, BLACK, sound_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, sound_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), sound_button)
        reset_text_m = font.render('ЗВУК ВКЛ' if is_sound_on else 'ЗВУК ВЫКЛ', True, (255, 255, 255))
        screen.blit(reset_text_m, (sound_button.x + 5, sound_button.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        # Сохраняем звук и громкость при выходе
                        game_data['current_volume'] = current_volume
                        game_data['is_sound_on'] = is_sound_on
                        save_game_data(game_data)
                        if button_sound:
                            button_sound.play()
                        loading_screen_button(screen)
                        return False
                    elif management_button.collidepoint(event.pos):
                        pygame.time.wait(100)
                        pygame.display.flip()
                        pygame.time.wait(100)
                        if button_sound:
                            button_sound.play()
                        confirm_reset = management(screen, clock, font)
                    elif plus_button.collidepoint(event.pos):
                        current_volume = min(1.0, current_volume + 0.1)
                        is_sound_on = True  # Включаем звук
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        slider_button_x = slider_x + int(current_volume * slider_width)
                        if button_sound:
                            button_sound.play()
                    elif minus_button.collidepoint(event.pos):
                        current_volume = max(0.0, current_volume - 0.1)
                        is_sound_on = current_volume > 0  # Выключаем звук, если громкость 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        slider_button_x = slider_x + int(current_volume * slider_width)
                        if button_sound:
                            button_sound.play()
                    elif slider_x <= event.pos[0] <= slider_x + slider_width and \
                            slider_y <= event.pos[1] <= slider_y + slider_height:
                        slider_button_x = event.pos[0]
                        current_volume = (slider_button_x - slider_x) / slider_width
                        is_sound_on = current_volume > 0  # Включаем звук, если громкость больше 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        if button_sound:
                            button_sound.play()
                    elif sound_button.collidepoint(event.pos):
                        is_sound_on = not is_sound_on
                        if not is_sound_on:
                            current_volume = 0.0  # Сбрасываем громкость до минимума
                            slider_button_x = slider_x
                        shot_sound.set_volume(current_volume if is_sound_on else 0)
                        if button_sound:
                            button_sound.play()

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if slider_x <= event.pos[0] <= slider_x + slider_width and \
                            slider_y <= event.pos[1] <= slider_y + slider_height:
                        slider_button_x = event.pos[0]
                        current_volume = (slider_button_x - slider_x) / slider_width
                        is_sound_on = current_volume > 0  # Включаем звук, если громкость больше 0
                        shot_sound.set_volume(current_volume if is_sound_on else 0)

        clock.tick(60)

def shop_home(screen, clock, font):
    confirmation_running = True
    while confirmation_running:
        screen.blit(fon_game_menu, (0, 0))

        draw_text(screen, 'МАГАЗИН ТАНКОВ', font, (255, 255, 255),
                  (screen_width // 2, 15))

        esc_button = pygame.Rect((screen_width - 135) // 2, 35, 135, 45)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font.render('НАЗАД', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 5, esc_button.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                confirmation_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if esc_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        loading_screen_button(screen)
                        return False

        clock.tick(60)  # Ограничение FPS

def home(screen, clock, font, font_home, screen_width, screen_height):
    """Функция главного меню."""
    confirmation_running = True
    while confirmation_running:
        # Отображение фона
        screen.blit(fon_menu, (0, 0))  # Укажите правильный путь к файлу фона

        # Цвета кнопок
        button_colors = {
            "esc": (1, 10, 10),
            "stats": (10, 255, 10),
            "shop": (225, 10, 225),
            "settings": (125, 125, 125),
            'countdown_tex': (176, 204, 92),
        }

        # Создание кнопки "В БОИ"
        v_boi_button = pygame.Rect((screen_width - 1000) // 2, 150, 1000, 350)
        pygame.draw.rect(screen, BLACK, v_boi_button.move(10, 10))  # Тень кнопки
        pygame.draw.rect(screen, GREEN, v_boi_button, border_radius=10)  # Зеленая рамка
        pygame.draw.rect(screen, (255, 165, 0), v_boi_button)  # Желтая кнопка
        reset_text_m = font_home.render('В БОИ', True, (255, 255, 255))  # Текст "В БОИ"
        screen.blit(reset_text_m, (v_boi_button.x + 30, v_boi_button.y + 45))  # Отображаем текст кнопки

        # Координаты кнопок
        button_gap = 50  # Промежуток между кнопками
        button_widths = [235, 175, 225]  # Ширина кнопок (Статистика, Магазин, Настройки)
        total_width = sum(button_widths) + button_gap * (
                    len(button_widths) - 1)  # Общая ширина всех кнопок и промежутков
        start_x = (screen_width - total_width) // 2  # Начальная координата x для первой кнопки

        # Кнопка "Статистика"
        stats_button = pygame.Rect(start_x, v_boi_button.y + v_boi_button.height + 75, 235, 45)
        pygame.draw.rect(screen, BLACK, stats_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, stats_button, border_radius=15)
        pygame.draw.rect(screen, button_colors["stats"], stats_button)
        reset_text_m = font_menu.render('СТАТИСТИКА', True, (255, 255, 255))
        screen.blit(reset_text_m, (stats_button.x + 5, stats_button.y + 5))

        # Кнопка "Магазин"
        shop_button = pygame.Rect(stats_button.x + stats_button.width + button_gap, stats_button.y, 175, 45)
        pygame.draw.rect(screen, BLACK, shop_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, shop_button, border_radius=15)
        pygame.draw.rect(screen, button_colors["shop"], shop_button)
        reset_text_m = font_menu.render('МАГАЗИН', True, (255, 255, 255))
        screen.blit(reset_text_m, (shop_button.x + 5, shop_button.y + 5))

        # Кнопка "Настройки"
        settings_button = pygame.Rect(shop_button.x + shop_button.width + button_gap, shop_button.y, 225, 45)
        pygame.draw.rect(screen, BLACK, settings_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, settings_button, border_radius=15)
        pygame.draw.rect(screen, button_colors["settings"], settings_button)
        reset_text_m = font_menu.render('НАСТРОЙКИ', True, (255, 255, 255))
        screen.blit(reset_text_m, (settings_button.x + 5, settings_button.y + 5))

        # Кнопка "ВЫХОД" остаётся на своём месте
        exit_button_width = 300  # Ширина кнопки
        exit_button_height = 100  # Высота кнопки
        exit_button_x = (screen_width - exit_button_width) // 2  # Центрируем по ширине
        exit_button_y = screen_height - 125  # Располагаем выше от нижнего края

        exit_button = pygame.Rect(exit_button_x, exit_button_y, exit_button_width, exit_button_height)
        pygame.draw.rect(screen, BLACK, exit_button.move(5, 5))  # Тень кнопки
        pygame.draw.rect(screen, GREEN, exit_button, border_radius=10)  # Зеленая рамка
        pygame.draw.rect(screen, (255, 107, 107), exit_button)  # Красная кнопка

        # Устанавливаем текст
        exit_text = font.render('ВЫЙТИ ИЗ ИГРЫ', True, (255, 255, 255))  # Текст кнопки
        text_x = exit_button.x + (exit_button.width - exit_text.get_width()) // 2  # Центрируем текст по ширине кнопки
        text_y = exit_button.y + (exit_button.height - exit_text.get_height()) // 2  # Центрируем текст по высоте кнопки
        screen.blit(exit_text, (text_x, text_y))  # Отображаем текст

        pygame.display.flip()


        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Закрытие окна
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Нажатие мыши
                if event.button == 1:  # Левая кнопка мыши
                    if v_boi_button.collidepoint(event.pos):  # Если нажата кнопка "В БОИ"
                        if button_sound:
                            button_sound.play()
                        countdown(screen, screen_width, screen_height)
                        # Возвращаем необходимые данные для основной игры
                        return tank1, tank2, tank1_score, tank2_score, shot_1, shot_2, struck_1, struck_2, struck_gun_1, struck_gun_2, False
                    if exit_button.collidepoint(event.pos):  # Если нажата кнопка "ВЫХОД"
                        if button_sound:
                            button_sound.play()
                            pygame.quit()
                            sys.exit()
                    elif stats_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        button_colors["stats"] = (0, 200, 0)
                        pygame.time.wait(200)
                        pygame.display.flip()
                        pygame.time.wait(200)
                        confirm_reset = stats_home(screen, clock, font)
                        if button_sound:
                            button_sound.play()
                    elif shop_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        button_colors["shop"] = (200, 0, 200)
                        pygame.time.wait(200)
                        pygame.display.flip()
                        pygame.time.wait(200)
                        confirm_reset = shop_home(screen, clock, font)
                        if button_sound:
                            button_sound.play()
                    elif settings_button.collidepoint(event.pos):
                        if button_sound:
                            button_sound.play()
                        button_colors["settings"] = (100, 100, 100)
                        pygame.time.wait(200)
                        pygame.display.flip()
                        pygame.time.wait(200)
                        confirm_reset = settings_home(screen, clock, font)
                        if button_sound:
                            button_sound.play()

            if event.type == pygame.MOUSEBUTTONUP:
                # Возвращаем цвета кнопок в исходное состояние
                if event.type == pygame.MOUSEBUTTONUP:
                    button_colors = {
                        "esc": (1, 10, 10),
                        "stats": (10, 255, 10),
                        "shop": (225, 10, 225),
                        "settings": (125, 125, 125),
                        'countdown_tex': (176, 204, 92),
                    }

        clock.tick(60)  # Ограничение FPS

def loading_screen(screen):
    progress = 0
    width_bar = 500  # Длина полоски загрузки
    height_bar = 30   # Высота полоски загрузки

    # Центрируем полоску
    bar_x = (screen_width - width_bar) // 2
    bar_y = (screen_height - height_bar) // 2

    while progress < 100:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Перерисовываем фон и текст "Загрузка..."
        screen.blit(fon_load_menu, (0, 0))  # Заново рисуем фон
        text = font.render("Загрузка...", True, WHITE)
        text_rect = text.get_rect(center=(screen_width // 2, bar_y - 40))
        screen.blit(text, text_rect)

        # Случайное увеличение прогресса
        increment = random.randint(5, 25)
        progress += increment
        if progress > 100:
            progress = 100

        # Отрисовываем полоску загрузки
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, width_bar, height_bar))  # Фон полоски
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, (progress / 100) * width_bar, height_bar))  # Прогресс

        # Текст с процентами
        percent_text = font.render(f"{progress}%", True, WHITE)
        percent_rect = percent_text.get_rect(center=(screen_width // 2, bar_y + 55))
        screen.blit(percent_text, percent_rect)

        # Обновление экрана
        pygame.display.update()

        # Задержка для реалистичности
        time.sleep(random.uniform(0.15, 0.30)) # 0.15 0.30

    # Переход к основной функции после завершения загрузки
    home(screen, clock, font, font_home, screen_width, screen_height)

def loading_screen_button(screen):
    progress = 0
    width_bar = 500  # Длина полоски загрузки
    height_bar = 30   # Высота полоски загрузки

    # Центрируем полоску
    bar_x = (screen_width - width_bar) // 2
    bar_y = (screen_height - height_bar) // 2

    while progress < 100:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Перерисовываем фон и текст "Загрузка..."
        screen.blit(fon_load_menu, (0, 0))  # Заново рисуем фон
        text = font.render("Загрузка...", True, WHITE)
        text_rect = text.get_rect(center=(screen_width // 2, bar_y - 40))
        screen.blit(text, text_rect)

        # Случайное увеличение прогресса
        increment = random.randint(75, 100)
        progress += increment
        if progress > 100:
            progress = 100

        # Отрисовываем полоску загрузки
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, width_bar, height_bar))  # Фон полоски
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, (progress / 100) * width_bar, height_bar))  # Прогресс

        # Текст с процентами
        percent_text = font.render(f"{progress}%", True, WHITE)
        percent_rect = percent_text.get_rect(center=(screen_width // 2, bar_y + 55))
        screen.blit(percent_text, percent_rect)

        # Обновление экрана
        pygame.display.update()

        # Задержка для реалистичности
        time.sleep(random.uniform(0.1, 0.11))

def loading_screen_button_home(screen):
    progress = 0
    width_bar = 500  # Длина полоски загрузки
    height_bar = 30   # Высота полоски загрузки

    # Центрируем полоску
    bar_x = (screen_width - width_bar) // 2
    bar_y = (screen_height - height_bar) // 2

    while progress < 100:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Перерисовываем фон и текст "Загрузка..."
        screen.blit(fon_load_menu, (0, 0))  # Заново рисуем фон
        text = font.render("Загрузка...", True, WHITE)
        text_rect = text.get_rect(center=(screen_width // 2, bar_y - 40))
        screen.blit(text, text_rect)

        # Случайное увеличение прогресса
        increment = random.randint(75, 100)
        progress += increment
        if progress > 100:
            progress = 100

        # Отрисовываем полоску загрузки
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, width_bar, height_bar))  # Фон полоски
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, (progress / 100) * width_bar, height_bar))  # Прогресс

        # Текст с процентами
        percent_text = font.render(f"{progress}%", True, WHITE)
        percent_rect = percent_text.get_rect(center=(screen_width // 2, bar_y + 55))
        screen.blit(percent_text, percent_rect)

        # Обновление экрана
        pygame.display.update()

        # Задержка для реалистичности
        time.sleep(random.uniform(0.1, 0.11))
        home(screen, clock, font, font_home, screen_width, screen_height)
        return False

def reset_game(screen_width, screen_height, controls_tank1, controls_tank2):
    """Функция сброса игры."""

    # Создание новых объектов танков с исходным состоянием
    tank1 = Tank(50, 50, (0, 0, 0), controls_tank1, initial_angle=180)
    tank2 = Tank(screen_width - 150, screen_height - 100, (0, 0, 0), controls_tank2, initial_angle=0)

    # Сброс здоровья
    tank1.health = 100
    tank2.health = 100

    # Сброс счетчиков и статистики
    tank1_score = 0
    tank2_score = 0
    shot_1 = 0
    shot_2 = 0
    struck_1 = 0
    struck_2 = 0
    struck_gun_1 = 0
    struck_gun_2 = 0

    # Возвращаем измененные значения
    return tank1, tank2, tank1_score, tank2_score, shot_1, shot_2, struck_1, struck_2, struck_gun_1, struck_gun_2

def countdown(screen, screen_width, screen_height):
    """Функция обратного отсчета перед началом игры с анимацией падения чисел."""
    for count in range(10, 0, -1):  # Отсчет от 3 до 1
        y_position = screen_height // 3  # Начальная позиция текста (за верхней границей экрана)
        while y_position < screen_height // 2:  # Пока текст не достигнет центра экрана
            screen.blit(fon_load_menu, (0, 0))  # Заново рисуем фон
            font_o = pygame.font.Font(None, 400)  # Шрифт и размер текста
            text = font_o.render(str(count), True, (0, 0, 0))  # Текст с текущим числом
            text_rect = text.get_rect(center=(screen_width // 2, y_position))  # Центрируем текст
            screen.blit(text, text_rect)  # Рисуем текст на экране
            font_go = pygame.font.Font(None, 150)
            coords_text_b = font_go.render(f'ДО НАЧАЛА  ПЕРВОГО БОЯ:', True, (0, 255, 0))
            screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), screen_height // 20))
            pygame.display.flip()  # Обновляем экран
            pygame.time.delay(10)  # Задержка, чтобы создать эффект плавного движения
            y_position += 5  # Смещаем текст вниз

        pygame.time.delay(300)  # Небольшая пауза, когда число достигает центра экрана

    # Финальное сообщение "В БОЙ!" с анимацией падения
    y_position = screen_height // 2.5  # Начальная позиция текста
    while y_position < screen_height // 2:  # Пока текст не достигнет центра экрана
        screen.blit(background, (0, 0))  # Очистка экрана (фон белый)
        font_o = pygame.font.Font(None, 300)  # Шрифт и размер текста
        text = font_o.render('В БОЙ!', True, (0, 255, 0))  # Зеленый текст "В БОЙ!"
        text_rect = text.get_rect(center=(screen_width // 2, y_position))  # Центрируем текст
        screen.blit(text, text_rect)  # Рисуем текст на экране
        pygame.display.flip()  # Обновляем экран
        pygame.time.delay(10)  # Задержка, чтобы создать эффект плавного движения
        y_position += 5  # Смещаем текст вниз

    pygame.time.delay(100)  # Пауза

def countdown_y(screen, screen_width, screen_height):
    """Функция обратного отсчета перед началом игры с анимацией падения чисел."""
    for count in range(5, 0, -1):  # Отсчет от 3 до 1
        y_position = screen_height // 3  # Начальная позиция текста (за верхней границей экрана)
        while y_position < screen_height // 2:  # Пока текст не достигнет центра экрана
            screen.blit(fon_load_menu, (0, 0))  # Очистка экрана (фон белый)
            font_o = pygame.font.Font(None, 400)  # Шрифт и размер текста
            text = font_o.render(str(count), True, (0, 0, 0))  # Текст с текущим числом
            text_rect = text.get_rect(center=(screen_width // 2, y_position))  # Центрируем текст
            screen.blit(text, text_rect)  # Рисуем текст на экране
            font_go = pygame.font.Font(None, 250)
            coords_text_b = font_go.render(f'ДО НАЧАЛА БОЯ:', True, (0, 255, 0))
            screen.blit(coords_text_b, ((screen_width // 2) - (coords_text_b.get_width() // 2), screen_height // 20))
            pygame.display.flip()  # Обновляем экран
            pygame.time.delay(10)  # Задержка, чтобы создать эффект плавного движения
            y_position += 5  # Смещаем текст вниз

        pygame.time.delay(300)  # Небольшая пауза, когда число достигает центра экрана

    # Финальное сообщение "В БОЙ!" с анимацией падения
    y_position = screen_height // 2.5  # Начальная позиция текста
    while y_position < screen_height // 2:  # Пока текст не достигнет центра экрана
        screen.blit(background, (0, 0))  # Очистка экрана (фон белый)
        font_o = pygame.font.Font(None, 300)  # Шрифт и размер текста
        text = font_o.render('В БОЙ!', True, (0, 255, 0))  # Зеленый текст "В БОЙ!"
        text_rect = text.get_rect(center=(screen_width // 2, y_position))  # Центрируем текст
        screen.blit(text, text_rect)  # Рисуем текст на экране
        pygame.display.flip()  # Обновляем экран
        pygame.time.delay(10)  # Задержка, чтобы создать эффект плавного движения
        y_position += 5  # Смещаем текст вниз

    pygame.time.delay(100)  # Пауза

# Функция обратного отсчета
def countdown_tex(screen, screen_width, screen_height):
    """Функция обратного отсчета перед началом игры с кнопкой для пропуска."""

    def draw_button():
        font_button = pygame.font.Font(None, 75)  # Шрифт для кнопки
        button_rect = pygame.Rect((screen_width - 245) // 2, screen_height - 75, 245, 50)
        pygame.draw.rect(screen, BLACK, button_rect.move(2, 2))
        pygame.draw.rect(screen, GREEN, button_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), button_rect)
        reset_text_m = font_menu.render('ПРОПУСТИТЬ', True, (255, 255, 255))
        screen.blit(reset_text_m, (button_rect.x + 10, button_rect.y + 10))
        return button_rect

    # Основной цикл обратного отсчета
    for count in range(180, 0, -1):  # Отсчет от 18 до 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Обработка выхода
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):  # Проверяем, нажата ли кнопка
                    return  # Прерываем обратный отсчет

        # Отрисовка фона, текста и кнопки
        screen.blit(fon_pause, (0, 0))  # Очистка экрана (фон белый)
        font_count = pygame.font.Font(None, 400)  # Шрифт для чисел
        text = font_count.render(str(count), True, (200, 25, 200))  # Текст с текущим числом
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))  # Центрируем текст
        screen.blit(text, text_rect)  # Рисуем текст на экране

        # Дополнительный текст "ТЕХНИЧЕСКАЯ ПАУЗА"
        font_pause = pygame.font.Font(None, 125)
        pause_text = font_pause.render('ТЕХНИЧЕСКАЯ ПАУЗА', True, RED)
        screen.blit(pause_text, ((screen_width - pause_text.get_width()) // 2, screen_height // 20))

        # Отрисовка кнопки
        button_rect = draw_button()

        pygame.display.flip()  # Обновляем экран
        pygame.time.delay(1000)  # Задержка для текущего числа

    # Финальное сообщение "В БОЙ!"
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Обработка выхода
            pygame.quit()
            sys.exit()

    # Отрисовка финального текста
    screen.blit(background, (0, 0))
    font_fight = pygame.font.Font(None, 300)  # Шрифт для текста "В БОЙ!"
    text = font_fight.render('В БОЙ!', True, (200, 25, 200))  # Текст "В БОЙ!"
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))  # Центрируем текст
    screen.blit(text, text_rect)  # Рисуем текст на экране

    pygame.display.flip()  # Обновляем экран
    pygame.time.delay(500)  # Завершающая пауза

def check_collision(tank1, tank2):
    # Проверяем столкновение двух прямоугольников (танков)
    rect1 = pygame.Rect(tank1.x, tank1.y, tank1.width, tank1.height)
    rect2 = pygame.Rect(tank2.x, tank2.y, tank2.width, tank2.height)
    return rect1.colliderect(rect2)

def check_collision_with_obstacle(tank, obstacles):
    # Проверяем столкновение танка с любым из препятствий
    tank_rect = pygame.Rect(tank.x, tank.y, tank.width, tank.height)
    for obstacle in obstacles:
        if tank_rect.colliderect(obstacle.get_rect()):
            return True
    return False

# Управление для танков
controls_tank1 = {
    "left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s, "shoot": pygame.K_SPACE, "shoot_machine_gun": pygame.K_LSHIFT
}
controls_tank2 = {
    "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN, "shoot": pygame.K_RETURN, "shoot_machine_gun": pygame.K_RSHIFT
}

# Создание танков с разными углами поворота дула
tank1 = Tank(50, 50, BLACK, controls_tank1, initial_angle=180)
tank2 = Tank(screen_width - 150, screen_height - 100, BLACK, controls_tank2, initial_angle=0)

# Игровой цикл
loading_screen(screen)

while running:
    screen.blit(fon_menu, (0, 0))  # Очистка экрана (фон белый)

    # Сохраняем предыдущие позиции танков
    prev_tank1_x, prev_tank1_y = tank1.x, tank1.y
    prev_tank2_x, prev_tank2_y = tank2.x, tank2.y

    # Создаём препятствия с изображениями
    #obstacles = [
        #Obstacle(238, 362, 150, 150, 'assets/bush3.png'),
        #Obstacle(500, 100, 150, 150, 'assets/bush3.png'),]

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if button_sound:
                    button_sound.play()
                confirmation_running = False
                tank1, tank2, tank1_score, tank2_score, shot_1, shot_2, struck_1, struck_2, struck_gun_1, struck_gun_2 = reset_game(
                    screen_width, screen_height, controls_tank1, controls_tank2)
                loading_screen_button_home(screen)
            elif event.key == pygame.K_t:
                menu(screen, clock, font)
            elif event.key == pygame.K_j:
                settings_j(screen, clock, font)
            elif event.key == pygame.K_y:
                countdown_y(screen, screen_width, screen_height)
                tank1, tank2, tank1_score, tank2_score, shot_1, shot_2, struck_1, struck_2, struck_gun_1, struck_gun_2 = reset_game(
                    screen_width, screen_height, controls_tank1, controls_tank2)
            elif event.key == pygame.K_h:
                tank1, tank2, tank1_score, tank2_score, shot_1, shot_2, struck_1, struck_2, struck_gun_1, struck_gun_2 = reset_game(
                    screen_width, screen_height, controls_tank1, controls_tank2)
                loading_screen_button_home(screen)
            elif event.key == pygame.K_F3:
                text_visible_F3 = not text_visible_F3
                text_visible = not text_visible
            elif event.key == pygame.K_g:
                countdown_tex(screen, screen_width, screen_height)
            elif event.key == pygame.K_BACKSPACE:
                game_data = load_game_data()
                game_data['score_tank1'] = 0
                game_data['score_tank2'] = 0
                game_data['total_rounds'] = 0
                save_game_data(game_data)
            elif event.key == controls_tank1["shoot"]:
                if tank1.shoot():
                    text = font.render('Выстрел!', False, GREEN)
                    text_rect = text.get_rect(center=(tank1.x + tank1.width // 2, tank1.y - 40))
                    screen.blit(text, text_rect)
                    shot_1 += 1
                    game_data = load_game_data()
                    game_data['shot_1_shot'] += 1
                    save_game_data(game_data)
            elif event.key == controls_tank2["shoot"]:
                if tank2.shoot():
                    text = font.render('Выстрел!', False, GREEN)
                    text_rect = text.get_rect(center=(tank2.x + tank2.width // 2, tank2.y - 40))
                    screen.blit(text, text_rect)
                    shot_2 += 1
                    game_data = load_game_data()
                    game_data['shot_2_shot'] += 1
                    save_game_data(game_data)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if reset_button_rect.collidepoint(event.pos):
                    confirm_reset = display_confirmation(screen, clock, font)
                    if confirm_reset:
                        if button_sound:
                            button_sound.play()
                        game_data = load_game_data()
                        game_data['score_tank1'] = 0
                        game_data['score_tank2'] = 0
                        save_game_data(game_data)
                elif menu_button.collidepoint(event.pos):
                    if button_sound:
                        button_sound.play()
                    confirm_reset = menu(screen, clock, font)
                elif esc_button.collidepoint(event.pos):
                    if button_sound:
                        button_sound.play()
                    confirmation_running = False
                    tank1, tank2, tank1_score, tank2_score, shot_1, shot_2, struck_1, struck_2, struck_gun_1, struck_gun_2 = reset_game(
                        screen_width, screen_height, controls_tank1, controls_tank2)
                    loading_screen_button_home(screen)

    # Отображение фона
    screen.blit(background, (0, 0))

    # Получение текущего состояния клавиш
    keys = pygame.key.get_pressed()

    # Движение танков
    tank1.move(keys)  # Передаем состояние клавиш в метод move танка 1
    tank2.move(keys)  # Передаем состояние клавиш в метод move танка 2

    # Отображение текста, если он включен
    if text_visible:

        esc_button = pygame.Rect((screen_width - 100) // 2, screen_height - 57, 100, 21)
        pygame.draw.rect(screen, BLACK, esc_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, esc_button, border_radius=10)
        pygame.draw.rect(screen, (200, 10, 10), esc_button)
        reset_text_m = font.render('ДОМОИ', True, (255, 255, 255))
        screen.blit(reset_text_m, (esc_button.x + 0, esc_button.y - 3))

        menu_button = pygame.Rect((screen_width - 80) // 2, screen_height - 27, 80, 18)
        pygame.draw.rect(screen, BLACK, menu_button.move(2, 2))
        pygame.draw.rect(screen, GREEN, menu_button, border_radius=10)
        pygame.draw.rect(screen, (0, 200, 0), menu_button)
        reset_text = font.render('МЕНЮ', True, (255, 255, 255))
        screen.blit(reset_text, (menu_button.x + 0, menu_button.y - 2))

        reset_button_rect = pygame.Rect(-500, -5000, 275, 35)
        pygame.draw.rect(screen, BLACK, reset_button_rect.move(2, 2))
        pygame.draw.rect(screen, GREEN, reset_button_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 0, 0), reset_button_rect)
        reset_text = font.render('сбросить очки танков', True, (255, 255, 255))
        screen.blit(reset_text, (reset_button_rect.x + 5, reset_button_rect.y + 5))

        FPS = 75

        score_text_post_st = font.render(f'F3 для все статистики', True, GREEN)
        score_text_post_width_st = score_text_post_st.get_width()  # Ширина нижнего текста
        screen.blit(score_text_post_st,
                    ((screen_width - score_text_post_width_st) // 2, 10))  # Центр по горизонтали, снизу

        kust_1 = Platform(screen_width - screen_width + 150, screen_height - screen_height + 150, screen_width - screen_width + 150, screen_height - screen_height + 150,
                          'assets/bush3.png')  # screen_width, screen_height
        kust_2 = Platform(screen_width - screen_width + screen_width - 450, screen_height - screen_height + screen_height - 150, screen_width - screen_width + 150, screen_height - screen_height + 150,
                          'assets/bush3.png')

        kust_3 = Platform(screen_width - screen_width + screen_width - 300,
                          screen_height - screen_height + screen_height - 400, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_4 = Platform(screen_width - screen_width + screen_width - 300,
                          screen_height - screen_height + screen_height - 700, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_5 = Platform(screen_width - screen_width + screen_width - 550,
                          screen_height - screen_height + screen_height - 500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_6 = Platform(screen_width - screen_width + 700,
                          screen_height - screen_height + 75, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_7 = Platform(screen_width - screen_width + 375,
                          screen_height - screen_height + screen_height - 250, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_8 = Platform(screen_width - screen_width + 100,
                          screen_height - screen_height + screen_height - 200, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_9 = Platform(screen_width - screen_width + 500,
                          screen_height - screen_height + 125, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_10 = Platform(screen_width - screen_width + 600,
                          screen_height - screen_height + screen_height - 175, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')


        platforms = pygame.sprite.Group()
        platforms.add(kust_1, kust_2, kust_3, kust_4, kust_5, kust_6, kust_7, kust_8, kust_9, kust_10)

    elif text_visible_F3:

        reset_button_rect = pygame.Rect((screen_width -275) // 2, 60, 275, 35)
        pygame.draw.rect(screen, BLACK, reset_button_rect.move(2, 2))
        pygame.draw.rect(screen, GREEN, reset_button_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 0, 0), reset_button_rect)
        reset_text = font.render('сбросить очки танков', True, (255, 255, 255))
        screen.blit(reset_text, (reset_button_rect.x + 5, reset_button_rect.y + 5))

        FPS = 160

        font_st = pygame.font.Font(None, 24)
        text_f3_1 = font_st.render(f'Побед: {load_game_data()['score_tank1']}', True, BLACK)
        text_rect_1 = text_f3_1.get_rect(center=(tank1.x + tank1.width // 2, tank1.y - 40))
        screen.blit(text_f3_1, text_rect_1)

        font_st = pygame.font.Font(None, 24)
        text_f3_2 = font_st.render(f'Побед: {load_game_data()['score_tank2']}', True, BLACK)
        text_rect_2 = text_f3_2.get_rect(center=(tank2.x + tank2.width // 2, tank2.y - 40))
        screen.blit(text_f3_2, text_rect_2)

        font_st = pygame.font.Font(None, 24)
        text_f3_1 = font_st.render(f'танк 1', True, BLACK)
        text_rect_1 = text_f3_1.get_rect(center=(tank1.x + tank1.width // 2, tank1.y + 60))
        screen.blit(text_f3_1, text_rect_1)

        font_st = pygame.font.Font(None, 24)
        text_f3_2 = font_st.render(f'танк 2', True, BLACK)
        text_rect_2 = text_f3_2.get_rect(center=(tank2.x + tank2.width // 2, tank2.y + 60))
        screen.blit(text_f3_2, text_rect_2)

        score_text_post = font.render(f'всего с играно раундов: {load_game_data()['total_rounds']}', True, BLACK)
        score_text_post_width = score_text_post.get_width()  # Ширина нижнего текста  # Центр по горизонтали, снизу
        screen.blit(score_text_post, ((screen_width - score_text_post_width) // 2, 10))

        kust_1 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_2 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_3 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_4 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_5 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_6 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_7 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_8 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_9 = Platform(-500, -500, screen_width - screen_width + 150,
                          screen_height - screen_height + 150,
                          'assets/bush3.png')
        kust_10 = Platform(-500, -500, screen_width - screen_width + 150,
                           screen_height - screen_height + 150,
                           'assets/bush3.png')

        platforms = pygame.sprite.Group()
        platforms.add(kust_1, kust_2, kust_3, kust_4, kust_5, kust_6, kust_7, kust_8, kust_9, kust_10)

        # текст лево
        font_F3 = pygame.font.Font(None, 26)
        text_rect_1 = font_F3.render(f'всего с играно раундов: {load_game_data()['total_rounds']}', True, YELLOW_S)
        screen.blit(text_rect_1, (10, 40))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_2 = font_F3.render(f'очки танка 1: {load_game_data()['score_tank1']}', True, YELLOW_S)
        screen.blit(text_rect_2, (10, 60))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_3 = font_F3.render(f'очки танка 2: {load_game_data()['score_tank2']}', True, YELLOW_S)
        screen.blit(text_rect_3, (10, 80))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_4 = font_F3.render(f'текущие раунды:', True, YELLOW_S)
        screen.blit(text_rect_4, (10, 120))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_5 = font_F3.render(f'танк 1: {tank1_score}', True, YELLOW_S)
        screen.blit(text_rect_5, (10, 140))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_6 = font_F3.render(f'танк 2: {tank2_score}', True, YELLOW_S)
        screen.blit(text_rect_6, (10, 160))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_6 = font_F3.render(f'выстрелы танка 1: {shot_1}', True, YELLOW_S)
        screen.blit(text_rect_6, (10, 180))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_6 = font_F3.render(f'выстрелы танка 2: {shot_2}', True, YELLOW_S)
        screen.blit(text_rect_6, (10, 200))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_6 = font_F3.render(f'танк 1 пробил {struck_1} раз(а)', True, YELLOW_S)
        screen.blit(text_rect_6, (10, 220))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_6 = font_F3.render(f'танк 2 пробил {struck_2} раз(а)', True, YELLOW_S)
        screen.blit(text_rect_6, (10, 240))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_6 = font_F3.render(f'танк 1 попал из пулемета {struck_gun_1} раз(а)', True, YELLOW_S)
        screen.blit(text_rect_6, (10, 260))

        font_F3 = pygame.font.Font(None, 26)
        text_rect_6 = font_F3.render(f'танк 2 попал из пулемета {struck_gun_2} раз(а)', True, YELLOW_S)
        screen.blit(text_rect_6, (10, 280))

        font_F3 = pygame.font.Font(None, 26)
        tank1_coords_text = font_F3.render(f'координаты танка 1: ({int(tank1.x)}, {int(tank1.y)})', True, YELLOW_S)
        screen.blit(tank1_coords_text, (10, 300))

        font_F3 = pygame.font.Font(None, 26)
        tank2_coords_text = font_F3.render(f'координаты танка 2: ({int(tank2.x)}, {int(tank2.y)})', True, YELLOW_S)
        screen.blit(tank2_coords_text, (10, 320))

        font_F3 = pygame.font.Font(None, 26)
        tank2_coords_text = font_F3.render(f'FPS = {FPS}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (10, 360))

        font_F3 = pygame.font.Font(None, 26)
        tank2_coords_text = font_F3.render(f'монеты танка 1: {load_game_data()['coins_1']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (10, 400))

        font_F3 = pygame.font.Font(None, 26)
        tank2_coords_text = font_F3.render(f'монеты танка 2: {load_game_data()['coins_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (10, 420))

        font_F3 = pygame.font.Font(None, 26)
        tank2_coords_text = font_F3.render(f'опыт танка 1: {load_game_data()['poins_1']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (10, 440))

        font_F3 = pygame.font.Font(None, 26)
        tank2_coords_text = font_F3.render(f'опыт танка 2: {load_game_data()['poins_2']}', True, YELLOW_S)
        screen.blit(tank2_coords_text, (10, 460))

        # текст право
        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'управление танком 1:', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 40))  # Справа, учли ширину текста

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'движение вперед: w', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 60))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'движение назад: s', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 80))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'поворот башни влево: a', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 100))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'поворот башни вправо: d', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 120))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'выстрел из орудия: spase (пробел)', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 140))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'пулемет: lshift', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 160))

        font_F3 = pygame.font.Font(None, 26)
        health_text2 = font_F3.render(f'управление танком 2:', True, YELLOW_S)
        screen.blit(health_text2, (screen_width - health_text2.get_width() - 10, 200))


        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'движение вперед: стрелка вверх', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 220))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'движение назад: стрелка вниз', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 240))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'поворот башни влево: стрелка влево', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 260))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'поворот башни вправо: стрелка в право', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 280))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'выстрел из орудия: enter', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 300))

        font_F3 = pygame.font.Font(None, 26)
        health_text1 = font_F3.render(f'пулемет: rshift', True, YELLOW_S)
        screen.blit(health_text1, (screen_width - health_text1.get_width() - 10, 320))

        font_F3 = pygame.font.Font(None, 26)
        coords_text_b = font_F3.render(f'сбросить все состояние: Backspase', True, YELLOW_S)
        screen.blit(coords_text_b, (screen_width - coords_text_b.get_width() - 10, 360))

        font_F3 = pygame.font.Font(None, 26)
        text_t = font_F3.render(f'text visible: {text_visible}', True, YELLOW_S)
        screen.blit(text_t, (screen_width - text_t.get_width() - 10, 400))

        font_F3 = pygame.font.Font(None, 26)
        text_t_f = font_F3.render(f'text visible F3: {text_visible_F3}', True, YELLOW_S)
        screen.blit(text_t_f, (screen_width - text_t_f.get_width() - 10, 420))

    # Обновление снарядов танков
    for tank in [tank1, tank2]:
        for bullet in tank.bullets[:]:
            bullet.move()
            if bullet.off_screen():
                tank.bullets.remove(bullet)
            elif bullet.hit(tank1) and tank != tank1:
                tank1.health -= random.randint(10, 30)
                tank.bullets.remove(bullet)
                text = font.render('Попал!', True, BLUE)
                screen.blit(text, (tank2.x + tank2.width // 2, tank2.y - 40))
                struck_2 += 1
                game_data = load_game_data()
                game_data['poins_2'] += 2
                game_data['struck_2_2'] += 1
                save_game_data(game_data)
            elif bullet.hit(tank2) and tank != tank2:
                tank2.health -= random.randint(10, 30)
                tank.bullets.remove(bullet)
                text = font.render('Попал!', True, BLUE)
                screen.blit(text, (tank1.x + tank1.width // 2, tank1.y - 40))
                struck_1 += 1
                game_data = load_game_data()
                game_data['poins_1'] += 2
                game_data['struck_1_1'] += 1
                save_game_data(game_data)

        for bullet_shift in tank.bullets_shift[:]:
            bullet_shift.move()
            if bullet_shift.off_screen():
                tank.bullets_shift.remove(bullet_shift)
            elif bullet_shift.hit(tank1) and tank != tank1:
                tank1.health -= 0.5
                tank.bullets_shift.remove(bullet_shift)
                text = font.render('Попал!', True, BLUE)
                screen.blit(text, (tank2.x + tank2.width // 2, tank2.y - 40))
                struck_gun_2 += 1
            elif bullet_shift.hit(tank2) and tank != tank2:
                tank2.health -= 0.5
                tank.bullets_shift.remove(bullet_shift)
                text = font.render('Попал!', True, BLUE)
                screen.blit(text, (tank1.x + tank1.width // 2, tank1.y - 40))
                struck_gun_1 += 1

        if check_collision(tank1, tank2):
            # Если танки столкнулись, наносим урон
            tank1.health -= 1
            tank2.health -= 1

            # Откатываем их на предыдущую позицию
            tank1.x, tank1.y = prev_tank1_x, prev_tank1_y
            tank2.x, tank2.y = prev_tank2_x, prev_tank2_y

        # Проверяем столкновение танков с препятствиями
        #if check_collision_with_obstacle(tank1, obstacles):
            #tank1.x, tank1.y = prev_tank1_x, prev_tank1_y

        #if check_collision_with_obstacle(tank2, obstacles):
            #tank2.x, tank2.y = prev_tank2_x, prev_tank2_y

    # Принудительное отображение здоровья как 0, если здоровье <= 0
    tank1_display_health = max(tank1.health, 0)  # Если здоровье отрицательное, установить в 0
    tank2_display_health = max(tank2.health, 0)  # Если здоровье отрицательное, установить в 0

    # Рендер текста
    health_text1 = font.render(f'ЗДОРОВЬЕ ТАНКА 1: {tank1_display_health}', True, BLACK)
    health_text2 = font.render(f'ЗДОРОВЬЕ ТАНКА 2: {tank2_display_health}', True, BLACK)
    score_text = font.render(f'Танк 1: {tank1_score} | Танк 2: {tank2_score}', True, BLACK)



    # Получение ширины текста для вычисления позиции по центру
    score_text_width = score_text.get_width()  # Ширина верхнего текста

    # Вывод текста на экран
    screen.blit(health_text1, (10, 10))  # Слева
    screen.blit(health_text2, (screen_width - health_text2.get_width() - 10, 10))  # Справа, учли ширину текста

    # Центрирование текста
    screen.blit(score_text, ((screen_width - score_text_width) // 2, 35))  # Центр по горизонтали, сверху

    # Проверка на проигрыш
    if tank1.health <= 0 or tank2.health <= 0:
        # Определяем победителя
        winner = 'второй танк' if tank1.health <= 0 else 'первый танк'

        # Загружаем данные, обновляем и сохраняем
        game_data = load_game_data()
        if winner == 'второй танк':
            game_data['score_tank2'] += 1
            game_data['coins_2'] += 20
            game_data['poins_2'] += 10
            game_data['poins_1'] -= 5
        if game_data['poins_1'] < 0:  # Проверяем, чтобы опыт не ушел в минус
            game_data['poins_1'] = 0
            game_data['win_2'] += 1
            game_data['por_1'] += 1
            tank2_score += 1

        elif winner == 'первый танк':
            game_data['score_tank1'] += 1
            game_data['coins_1'] += 20
            game_data['poins_1'] += 10
            game_data['poins_2'] -= 5
        if game_data['poins_2'] < 0:  # Проверяем, чтобы опыт не ушел в минус
            game_data['poins_2'] = 0
            game_data['win_1'] += 1
            game_data['por_2'] += 1
            tank1_score += 1

        game_data['total_rounds'] += 1  # Общее количество раундов увеличивается
        save_game_data(game_data)

        # Отображаем текст о победителе
        end_text = font.render(f'{winner} победил!', True, GREEN)
        screen.blit(end_text, (screen_width // 2 - 100, screen_height // 2))
        pygame.display.flip()
        reload_message_time = 0
        shoot_cooldown_shift = 0
        tank1_score = tank1_score
        tank2_score = tank2_score
        text_visible = True  # Флаг — отображается ли текст
        text_visible_F3 = False  # Флаг — отображается ли текст

        pygame.time.wait(3000)

        tank1.health = 100
        tank2.health = 100
        tank1 = Tank(50, 50, BLACK, controls_tank1, initial_angle=180)
        tank2 = Tank(screen_width - 150, screen_height - 100, BLACK, controls_tank2, initial_angle=0)

        countdown_y(screen, screen_width, screen_height)

        # Перезапуск игры
        running = True

    # Проверка здоровья танков
    if tank1.health <= 0 or tank2.health <= 0:
        running = False
    # Отрисовка танков и снарядов
    tank1.draw(screen)
    tank2.draw(screen)

    # Отрисовка препятствий
    #for obstacle in obstacles:
        #obstacle.draw(screen)

    for tank in [tank1, tank2]:
        for bullet in tank.bullets:
            bullet.draw(screen)
        for bullet_shift in tank.bullets_shift:
            bullet_shift.draw(screen)
    platforms.draw(screen)  # Отрисовка всех платформ на экране

    # Обновление экрана
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()