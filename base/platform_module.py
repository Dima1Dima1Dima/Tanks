import pygame

# Класс платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):  # Конструктор платформы
        super().__init__()  # Инициализация родительского класса Sprite
        self.image = pygame.image.load(image_path)  # Загружаем изображение
        self.image = pygame.transform.scale(self.image, (width, height))  # Масштабируем изображение под заданные размеры
        self.rect = self.image.get_rect(topleft=(x, y))  # Устанавливаем позицию платформы

class Obstacle:
    def __init__(self, x, y, width, height, image_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.image.load(image_path)  # Загружаем изображение
        self.image = pygame.transform.scale(self.image, (width, height))  # Масштабируем изображение под размеры

    def draw(self, screen):
        # Отрисовка изображения препятствия на экране
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        # Возвращает объект pygame.Rect для проверки столкновений
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Пример использования платформы:
# 1. Импортируйте класс платформы в вашем основном игровом коде:
# from platform_module import Platform  # Замените "platform_module" на имя вашего файла

# 2. Создайте объект платформы, указав координаты, размеры и путь к картинке:
# platform = Platform(100, 500, 200, 50, "platform_image.png")

# 3. Добавьте платформу в группу спрайтов:
# platforms = pygame.sprite.Group()
# platforms.add(platform)

# 4. В игровом цикле отрисуйте платформы:
# platforms.draw(screen)