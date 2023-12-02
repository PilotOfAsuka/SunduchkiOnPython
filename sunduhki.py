import pygame
import random
from collections import defaultdict, Counter

# Инициализация Pygame
pygame.init()

# Параметры окна
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Сундучки")

# Цвета
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Размеры и расположение карт
CARD_WIDTH, CARD_HEIGHT = 60, 90
PLAYER_CARD_Y = SCREEN_HEIGHT - CARD_HEIGHT - 10
DECK_POS = (SCREEN_WIDTH - CARD_WIDTH - 10, 10)
STACK_OFFSET = 15  # Смещение для стопки карт

# Класс карты
class Card:
    
    def __init__(self, rank, x, y, count=1):
        self.rank = rank
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.color = GREEN
        self.count = count
        self.font = pygame.font.SysFont(None, 36)  # Создаем объект шрифта


    def draw(self):
        for i in range(self.count):
            rect_offset = pygame.Rect(self.rect.x, self.rect.y - i * STACK_OFFSET, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(screen, self.color, rect_offset)
            pygame.draw.rect(screen, BLACK, rect_offset, 2)  # Черная обводка

            if i == self.count - 1:
                text = self.font.render(self.rank, True, BLACK)
                text_rect = text.get_rect(center=rect_offset.center)
                screen.blit(text, text_rect)

# Класс игры
class SunduchkiGameAI:
    def __init__(self):
        self.deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        self.players_hands = defaultdict(list)
        self.sunduchki = defaultdict(int)
        self.current_player = 0  # 0 - Человек, 1 - AI
        self.last_asked = None
        self.font = pygame.font.SysFont(None, 36)  # Создаем объект шрифта
        self.need_to_draw_card = False  # Флаг, указывающий, нужно ли брать карту из колоды
        self.ai_next_turn_time = 0
        self.ai_turn_interval = 3000  # Интервал в миллисекундах, через который ИИ делает ход


        random.shuffle(self.deck)

        for _ in range(7):
            self.players_hands[0].append(self.deck.pop())
            self.players_hands[1].append(self.deck.pop())

        self.update_cards()

    def update_cards(self):
        card_counts = Counter(self.players_hands[0])
        x_pos = 10
        self.player_cards = []
        for rank, count in card_counts.items():
            self.player_cards.append(Card(rank, x_pos, PLAYER_CARD_Y, count))
            x_pos += CARD_WIDTH + 10
            
    def draw_cards(self):
        
        for card in self.player_cards:
            card.draw()

        # Рисуем колоду
        if self.deck:
            pygame.draw.rect(screen, BLUE, (DECK_POS[0], DECK_POS[1], CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(screen, BLACK, (DECK_POS[0], DECK_POS[1], CARD_WIDTH, CARD_HEIGHT) , 2)  # Черная обводка

        # Выводим, какую карту спросил ИИ
        if self.last_asked:
            
            text = self.font.render(f"Мр. Свин спрашивает карту: {self.last_asked}", True, BLACK)
            screen.blit(text, (10, 10))
        
        # Отображаем количество сундучков для каждого игрока
        player_sunduchki_text = self.font.render(f"Ваши сундучки: {self.sunduchki[0]}", True, BLACK)
        screen.blit(player_sunduchki_text, (SCREEN_WIDTH - 250 , SCREEN_HEIGHT - 100))

        ai_sunduchki_text = self.font.render(f"Сундучки Мр.Свина: {self.sunduchki[1]}", True, BLACK)
        screen.blit(ai_sunduchki_text, (10, 50))
        # Отображаем, чей сейчас ход
        turn_text = "Ваш ход" if self.current_player == 0 else "Ход Мр. Свина"
        turn_text_render = self.font.render(turn_text, True, BLACK)
        screen.blit(turn_text_render, (SCREEN_WIDTH / 2 - 50, 100))
                # Отображаем сообщение о необходимости взять карту, если это требуется
        if self.current_player == 0 and self.need_to_draw_card:
            draw_card_text = "Нажмите на колоду, чтобы взять карту"
            draw_card_text_render = self.font.render(draw_card_text, True, BLACK)
            screen.blit(draw_card_text_render, (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2))



    def handle_click(self, pos):
        # Проверяем, кликнул ли игрок на колоду и нужно ли ему брать карту
        if self.current_player == 0 and self.need_to_draw_card:
            if pygame.Rect(DECK_POS[0], DECK_POS[1], CARD_WIDTH, CARD_HEIGHT).collidepoint(pos):
                self.draw_card()
                self.need_to_draw_card = False  # Сбрасываем флаг после того, как карта взята
                self.current_player = 1  # Передаем ход ИИ
                self.update_cards()  # Обновляем карты после взятия карты из колоды
            return

        # Обработка клика по карте
        for card in self.player_cards:
            if card.rect.collidepoint(pos) and self.current_player == 0:
                self.ask_card(card.rank)
                self.update_cards()
                break
            
    def ask_card(self, asked_rank):
        if asked_rank not in self.players_hands[self.current_player]:
            return False

        other_player = 1 - self.current_player
        if asked_rank in self.players_hands[other_player]:
            self.transfer_cards(asked_rank)
            self.need_to_draw_card = False  # Карта найдена, брать из колоды не нужно
            self.current_player = 1 - self.current_player  # Передаем ход
            return True
        else:
            self.need_to_draw_card = True  # Карта не найдена, брать из колоды нужно
            return False

    def transfer_cards(self, rank):
        other_player = 1 - self.current_player
        while rank in self.players_hands[other_player]:
            self.players_hands[other_player].remove(rank)
            self.players_hands[self.current_player].append(rank)
        self.check_sunduchki(rank) # Проверяем и обновляем сундучки

    def draw_card(self):
        if self.deck:
            drawn_card = self.deck.pop()
            self.players_hands[self.current_player].append(drawn_card)
            self.check_sunduchki(drawn_card)  # Проверяем и обновляем сундучки

    def check_sunduchki(self, rank):
        if self.players_hands[self.current_player].count(rank) == 4:
            self.sunduchki[self.current_player] += 1
            # Удаляем собранные сундучки из руки игрока
            self.players_hands[self.current_player] = [card for card in self.players_hands[self.current_player] if card != rank]
            self.update_cards()


    def ai_turn(self):
        current_time = pygame.time.get_ticks()
        if self.current_player == 1 and self.deck and current_time >= self.ai_next_turn_time:
            ai_card = random.choice(self.players_hands[1])
            self.last_asked = ai_card
            self.ask_card(ai_card)
            if self.need_to_draw_card:
                self.draw_card()
                self.need_to_draw_card = False

            self.update_cards()
            self.current_player = 0  # Передаем ход игроку
            self.ai_next_turn_time = current_time + self.ai_turn_interval
            
    def check_game_over(self):
        if not self.deck:  # Колода закончилась
            return True
        return False

    def draw_game_over_screen(self):
        winner_text = "Вы выиграли!" if self.sunduchki[0] > self.sunduchki[1] else "Вы проиграли!"
        winner_text_render = self.font.render(winner_text, True, BLACK)
        screen.blit(winner_text_render, (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 50))

        restart_button = pygame.Rect(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2, 150, 50)
        pygame.draw.rect(screen, GREEN, restart_button)
        restart_text = self.font.render("Перезапуск", True, BLACK)
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        screen.blit(restart_text, restart_text_rect)
        return restart_button

def main():
    game = SunduchkiGameAI()
    clock = pygame.time.Clock()
    restart_button = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button and restart_button.collidepoint(event.pos):
                    game = SunduchkiGameAI()  # Перезапуск игры
                else:
                    game.handle_click(event.pos)

        game.ai_turn()

        screen.fill(WHITE)
        game.draw_cards()
        if game.check_game_over():
            restart_button = game.draw_game_over_screen()
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
