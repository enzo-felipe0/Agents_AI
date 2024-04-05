import pygame
import time
import random

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)  # Verde escuro
DARK_YELLOW = (204, 204, 0)  # Amarelo mais escuro
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)  # Rosa

class Environment:
    def __init__(self, size=20, total_items=10, item_types = None):
        self.size = size
        self.total_items = total_items
        self.item_types = item_types if item_types is not None else ['I', 'A']  # Dois tipos de itens
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.item_positions_A = []
        self.item_positions_I = []
        self.place_items()
        

    def place_items(self):
        for _ in range(self.total_items):
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            item_type = random.choice(self.item_types)  # Escolhe aleatoriamente entre os tipos de itens disponíveis
            self.grid[x][y] = item_type

            # Adiciona a posição (x, y) à lista correspondente ao tipo de item
            if item_type == 'A':
                self.item_positions_A.append((x, y))
            elif item_type == 'I':
                self.item_positions_I.append((x, y))
            

    def is_item_at(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size and self.grid[x][y] in self.item_types:
            return self.grid[x][y]
        else:
            return False     

    def get_item_points(self, x, y):
        # Define a lógica para obter os pontos de um item em uma célula específica
        # Aqui, estamos retornando pontos fixos para diferentes tipos de itens
        if self.grid[x][y] == 'I':
            return 10
        elif self.grid[x][y] == 'A':
            return 20
        else:
            return 0  # Retorna 0 se não houver item na célula
        
class Agent:
    def __init__(self, env, start_x=0, start_y=0, color=WHITE, name="Agent"):
        self.env = env
        self.x = start_x
        self.y = start_y
        self.holding_item = None  # Inicialmente, o agente não está segurando nenhum item
        self.start_x = start_x
        self.start_y = start_y
        self.score = 0
        self.collected_items = 0
        self.color = color
        self.name = name
        self.direction = 'right'
        self.start_time = time.time()

    def pick(self):
        item_type = self.env.is_item_at(self.x, self.y)
        if item_type:
            if item_type == 'I':
                points = 10
            elif item_type == 'A':
                points = 20
            self.holding_item = (item_type, points)  # Item e pontuação correspondente
            self.env.grid[self.x][self.y] = ' '  # Remover o item do ambiente
            self.score += points  # Adicionar pontos
            self.collected_items += 1

    def drop(self):
        if self.holding_item:
            self.holding_item = None
            

    def move(self, direction):
        if direction == 'up' and self.x > 0:
            self.x -= 1
        elif direction == 'down' and self.x < self.env.size - 1:
            self.x += 1
        elif direction == 'left' and self.y > 0:
            self.y -= 1
        elif direction == 'right' and self.y < self.env.size - 1:
            self.y += 1

    def find_closest_item_direction(self):
        min_distance = float('inf')
        closest_direction = None

        for direction in ['up', 'down', 'left', 'right']:
            next_x, next_y = self.next_position(direction)
            if self.env.is_item_at(next_x, next_y):
                distance = abs(self.start_x - next_x) + abs(self.start_y - next_y)
                if distance < min_distance:
                    min_distance = distance
                    closest_direction = direction

        return closest_direction

    def next_position(self, direction):
        next_x, next_y = self.x, self.y
        if direction == 'up' and self.x > 0:
            next_x -= 1
        elif direction == 'down' and self.x < self.env.size - 1:
            next_x += 1
        elif direction == 'left' and self.y > 0:
            next_y -= 1
        elif direction == 'right' and self.y < self.env.size - 1:
            next_y += 1
        return next_x, next_y

    def move_to(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y

        if dx != 0:
            if dx > 0:
                self.move('down')
            else:
                self.move('up')
        elif dy != 0:
            if dy > 0:
                self.move('right')
            else:
                self.move('left')
    
    def movimentation(self):
        if self.direction == 'right':
            if self.y < self.env.size -1:
                self.move('right')
            else:
                self.move('down')
                self.direction = 'left'
        elif self.direction == 'left':
            if self.y > 0:
                self.move('left')
            else:
                self.move('down')
                self.direction = 'right'

    def no_op(self):
            move_to(self.start_x, self.start_y)


class ReactiveAgent(Agent):
    def __init__(self, env, start_x=0, start_y=0, color=WHITE, name="Agent"):
        super().__init__(env, start_x, start_y, color, name)
        self.direction = 'right'

    def act(self):
        if self.holding_item:
            self.move_to(self.start_x, self.start_y)
            if (self.x, self.y) == (self.start_x, self.start_y):
                self.drop()
                self.movimentation()
                closest_item_direction = self.find_closest_item_direction()
                if closest_item_direction:
                    self.move(closest_item_direction)
        else:
            if self.env.is_item_at(self.x, self.y):
                self.pick()
            else: 
                self.movimentation()
                closest_item_direction = self.find_closest_item_direction()
                if closest_item_direction:
                    self.move(closest_item_direction)

class StateAgent(Agent):
    def __init__(self, env, start_x=0, start_y=0, color=BLUE, name="Agent"):
        super().__init__(env, start_x, start_y, color, name)
        self.last_item_x = 0  # Posição x do último item coletado
        self.last_item_y = 0  # Posição y do último item coletado
        self.direction = 'right'
        self.is_position = True
        self.dir = 'right'

    def act(self):
        if self.holding_item:
            self.move_to(self.start_x, self.start_y)
            if (self.x, self.y) == (self.start_x, self.start_y):
                self.drop()
                self.is_position = False
                self.return_to_last_item()  # Retorna à posição do último item coletado
        else:
            if self.env.is_item_at(self.x, self.y):
                self.last_item_x = self.x  # Armazena a posição do item coletado
                self.last_item_y = self.y
                self.dir = self.direction
                self.pick()
            else:
                if self.is_position == True:
                    self.movimentation()  # Movimenta-se normalmente
                    print("ta andando normal")
                else: 
                    self.return_to_last_item()

    def return_to_last_item(self):
        self.move_to(self.last_item_x, self.last_item_y)
        print("ta voltando pro item")
        if (self.x, self.y) == (self.last_item_x, self.last_item_y):
            self.direction = self.dir
            self.is_position = True


class GoalAgent(Agent):
    def __init__(self, env, start_x=1, start_y=1, color=WHITE, name="Agent"):
        super().__init__(env, start_x, start_y, color, name)
        self.goal = "collect_items"  # Inicialmente, o agente quer coletar itens.
        self.collected_items = 0
        self.explored = set()  # Conjunto de posições já exploradas
        self.item_positions_A = []  # Lista de posições dos itens do tipo A
        self.item_positions_I = []  # Lista de posições dos itens do tipo I
        self.all_items = []
        self.index = 0
        self.collected_items = 0
        

    def act(self):
        self.organize_items(self.item_positions_A, self.item_positions_I)

        # Atualiza o objetivo com base no estado atual
        if self.goal == "collect_items" and self.holding_item:
            self.goal = "return_home"
    
        # Ação baseada no objetivo
        if self.goal == "collect_items":
            self.collect_items()
        elif self.goal == "return_home":
            self.return_home()

    def set_item_positions(self, item_positions_A, item_positions_I):
        self.item_positions_A = item_positions_A
        self.item_positions_I = item_positions_I

    def organize_items(self, item_positions_A, item_positions_I):
        # Combine as duas listas de posições de itens
        self.all_items = item_positions_A + item_positions_I
        # Ordene os itens pela proximidade do ponto (1, 1)
        self.all_items.sort(key=lambda pos: abs(pos[0] - 1) + abs(pos[1] - 1))

        # Crie duas variáveis para armazenar as coordenadas x e y do índice 0 da lista all_items
        if self.index < len(self.all_items):
            self.first_item_x, self.first_item_y = self.all_items[self.index]
        else:
            self.move_to(self.start_x, self.start_y)
         

    def collect_items(self):
        if self.env.is_item_at(self.x, self.y):
            self.pick()
        else:
            self.move_to(self.first_item_x, self.first_item_y)

    def return_home(self):
        if (self.x, self.y) == (self.start_x, self.start_y):
            self.drop()
            self.collected_items = self.collected_items + 1
            if self.index > 10:
                no_op()
            else:
                self.index = self.index + 1
                self.goal = "collect_items"
            
        else:
            self.move_to(self.start_x, self.start_y)

    def no_op(self):
            move_to(0, 0)

class UtilityAgent(Agent):
    def __init__(self, env, start_x=1, start_y=1, color=WHITE, name="Agent"):
        super().__init__(env, start_x, start_y,color, name)
        self.total_points = 0
        self.goal = "collect_items"
        self.explored = set()  # Conjunto de posições já exploradas
        self.item_positions_A = []  # Lista de posições dos itens do tipo A
        self.item_positions_I = []  # Lista de posições dos itens do tipo I
        self.index = 0
        self.first_item_x = None
        self.first_item_y = None
        self.collected_items = 0
        self.start_time = time.time()


    def act(self):
        self.organize_items(self.item_positions_A, self.item_positions_I)

        # Atualiza o objetivo com base no estado atual
        if self.goal == "collect_items" and self.collected_items == 1:
            self.goal = "return_home"
        elif self.goal == "return_home" and self.collected_items == 0:
            self.goal = "collect_items"

        # Ação baseada no objetivo
        if self.goal == "collect_items":
            self.collect_items()
        elif self.goal == "return_home":
            self.return_home()

    def set_item_positions(self, item_positions_A, item_positions_I):
        self.item_positions_A = item_positions_A
        self.item_positions_I = item_positions_I

    def run_list(self, item_positions_A, item_positions_):
        if self.index < len(self.item_positions_A):
            # Crie duas variáveis para armazenar as coordenadas x e y do índice atual da lista A
            self.first_item_x, self.first_item_y = self.item_positions_A[self.index]
        elif self.index < len(self.item_positions_A) + len(self.item_positions_I):
            # Acesse a lista I usando o índice ajustado
            i_index = self.index - len(self.item_positions_A)
            self.first_item_x, self.first_item_y = self.item_positions_I[i_index]
        else:
            self.move_to(0, 0)

    def organize_items(self, item_positions_A, item_positions_I):
        # Ordene os itens pela proximidade do ponto (1, 1)
        self.item_positions_A.sort(key=lambda pos: abs(pos[0] - 1) + abs(pos[1] - 1))
        self.item_positions_I.sort(key=lambda pos: abs(pos[0] - 1) + abs(pos[1] - 1))
        
    def collect_items(self):
        self.run_list(self.item_positions_A, self.item_positions_I)  # Atualiza os itens a serem coletados
        if self.env.is_item_at(self.x, self.y):
            self.pick()
            self.collected_items = self.collected_items
            if (self.x, self.y) == (self.first_item_x, self.first_item_y):
                self.index = self.index + 1
            else:
                self.goal = "collect_items"
        else:
            self.move_to(self.first_item_x, self.first_item_y)

    def return_home(self):
        if (self.x, self.y) == (self.start_x, self.start_y):
            self.drop()
            self.collected_items = self.collected_items - 1
        else:
            self.move_to(self.start_x, self.start_y)


# Função para desenhar o ambiente e os agentes
def draw_environment(screen, env, agents):
    cell_size = 30
    margin = 2
    screen.fill(DARK_YELLOW)  # Preencher a tela com amarelo mais escuro

    # Desenhar grade
    for x in range(env.size):
        for y in range(env.size):
            pygame.draw.rect(screen, WHITE, [(margin + cell_size) * y + margin, (margin + cell_size) * x + margin, cell_size, cell_size], 1)

    # Desenhar itens
    for x in range(env.size):
        for y in range(env.size):
            item_type =  env.is_item_at(x, y)
            if item_type:
                if item_type == 'I':
                    color = PINK
                elif item_type == 'A':
                    color = GREEN
                pygame.draw.rect(screen, color, [(margin + cell_size) * y + margin, (margin + cell_size) * x + margin, cell_size, cell_size])

    # Desenhar agentes
    for agent in agents:
        pygame.draw.rect(screen, agent.color, [(margin + cell_size) * agent.y + margin, (margin + cell_size) * agent.x + margin, cell_size, cell_size])

    # Desenhar placar
    font = pygame.font.Font(None, 24)
    y_offset = 20
    for agent in agents:
        runtime = round(time.time() - agent.start_time, 2)
        text = font.render(f"{agent.name}: {agent.score}", True, BLACK)
        screen.blit(text, (screen.get_width() - 230, y_offset))
        pygame.draw.rect(screen, agent.color, (screen.get_width() - 270, y_offset + 5, 15, 15))  # Mostrar a cor ao lado do placar
        y_offset += 30
        text = font.render(f"Time: {runtime} s", True, BLACK)
        screen.blit(text, (screen.get_width() - 230, y_offset))

    pygame.display.flip()

# Função principal
def main():
    pygame.init()

    size = 20
    env = Environment(size=size, total_items=10)
    item_positions_A = env.item_positions_A
    item_positions_I = env.item_positions_I
    agents = [
        ReactiveAgent(env, color=RED, name="Reactive Agent "),
        #StateAgent(env, color=BLUE, name="State Agent "),
        #GoalAgent(env, color=BLACK, name="Goal Agent"),
        #UtilityAgent(env, color=PURPLE, name="Utility Agent"),
    ]
    #sempre passar o indice do GoalAgent e pro utility
    #agents[0].set_item_positions(item_positions_A, item_positions_I)
    screen_width = size * 32 + 300  # Ajustado para a largura do placar
    screen_height = size * 32
    screen = pygame.display.set_mode([screen_width, screen_height])
    pygame.display.set_caption("Agents")

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for agent in agents:
            agent.act()
        draw_environment(screen, env, agents)
        clock.tick(40)  # Ajuste a velocidade de exibição

    pygame.quit()

if __name__ == "__main__":
    main()