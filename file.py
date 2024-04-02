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
        self.place_items()
        

    def place_items(self):
        for _ in range(self.total_items):
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            item_type = random.choice(self.item_types)  # Escolhe aleatoriamente entre os tipos de itens disponíveis
            self.grid[x][y] = item_type

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

    def move_towards_item_or_home(self):
        if self.holding_item:
            self.move_to(self.start_x, self.start_y)
        else:
            closest_item_direction = self.find_closest_item_direction()
            if closest_item_direction:
                self.move(closest_item_direction)
            else:
                self.move(random.choice(['up', 'down', 'left', 'right']))

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


class ReactiveAgent(Agent):
    def __init__(self, env, start_x=0, start_y=0, color=WHITE, name="Agent"):
        super().__init__(env, start_x, start_y, color, name)

    def act(self):
        if (self.x, self.y) == (self.start_x, self.start_y) and self.holding_item:
            self.drop()
        elif self.env.is_item_at(self.x, self.y) and not self.holding_item:
            self.pick()
        else:
            self.move_towards_item_or_home()

    def move_towards_item_or_home(self):
        if self.holding_item:
            self.move_to(self.start_x, self.start_y)
        else:
            closest_item_direction = self.find_closest_item_direction()
            if closest_item_direction:
                self.move(closest_item_direction)
            else:
                self.move(random.choice(['up', 'down', 'left', 'right']))

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
    

class StateAgent(Agent):
    def __init__(self, env, start_x=0, start_y=0, color=BLUE, name="Agent"):
        super().__init__(env, start_x, start_y, color, name)
        self.explored = set()  # Conjunto de posições já exploradas
        self.items_locations = []  # Lista de localizações conhecidas de itens

    def update_state(self):
        # Atualiza o estado interno com a localização atual
        self.explored.add((self.x, self.y))
        if self.env.is_item_at(self.x, self.y):
            self.items_locations.append((self.x, self.y))

    def act(self):
        if self.holding_item:
            # Se estiver segurando um item, voltar ao ponto de partida
            self.move_to(self.start_x, self.start_y)
            if (self.x, self.y) == (self.start_x, self.start_y):
                self.drop()
                self.explore()
                self.update_state()
                closest_item_direction = self.find_closest_item_direction()
                if closest_item_direction:
                    self.move(closest_item_direction)
        else:
            if self.env.is_item_at(self.x, self.y):
                self.pick()
            else:
                self.explore()
                self.update_state()
                closest_item_direction = self.find_closest_item_direction()
                if closest_item_direction:
                    self.move(closest_item_direction)

    def move_to(self, target_x, target_y):
        # Semelhante ao ReactiveAgent, mas poderia ser mais sofisticado
        if self.x < target_x:
            self.move('down')
        elif self.x > target_x:
            self.move('up')
        elif self.y < target_y:
            self.move('right')
        elif self.y > target_y:
            self.move('left')

    def explore(self):
        directions = ['up', 'down', 'left', 'right']
        random.shuffle(directions)  # Explora direções aleatoriamente
        unexplored_directions = [direction for direction in directions if self.can_move(direction)]

        if unexplored_directions:
            # Se houver direções não exploradas disponíveis, move-se para a primeira delas.
            self.move(unexplored_directions[0])
        else:
            # Se todas as direções foram exploradas, tenta encontrar uma direção para se mover que não leve fora dos limites
            self.move_to_previously_explored()

    def can_move(self, direction):
        """Verifica se pode mover na direção especificada sem sair dos limites e sem ir para uma célula já explorada."""
        next_x, next_y = self.next_position(direction)
        return (0 <= next_x < self.env.size and 
                0 <= next_y < self.env.size and 
                (next_x, next_y) not in self.explored)

    def move_to_previously_explored(self):
        """Move-se para uma direção aleatória que não o leve fora dos limites do ambiente, mesmo que já explorada."""
        directions = ['up', 'down', 'left', 'right']
        valid_directions = [direction for direction in directions if self.is_within_bounds(direction)]

        if valid_directions:
            self.move(random.choice(valid_directions))

    def is_within_bounds(self, direction):
        """Verifica se a próxima posição está dentro dos limites do ambiente."""
        next_x, next_y = self.next_position(direction)
        return 0 <= next_x < self.env.size and 0 <= next_y < self.env.size      
        
    def next_position(self, direction):
        # Calcula a próxima posição com base na direção
        if direction == 'up':
            return self.x - 1, self.y
        elif direction == 'down':
            return self.x + 1, self.y
        elif direction == 'left':
            return self.x, self.y - 1
        elif direction == 'right':
            return self.x, self.y + 1


class GoalAgent(Agent):
    def __init__(self, env, start_x=1, start_y=1, color=WHITE, name="Agent"):
        super().__init__(env, start_x, start_y, color, name)
        self.goal = "collect_items"  # Inicialmente, o agente quer coletar itens.
        self.collected_items = 0
        self.explored = set()  # Conjunto de posições já exploradas

    def act(self):
        # Atualiza o objetivo com base no estado atual
        if self.goal == "collect_items" and self.collected_items == self.env.total_items:
            self.goal = "return_home"
        
        # Ação baseada no objetivo
        if self.goal == "collect_items":
            self.collect_items()
        elif self.goal == "return_home":
            self.return_home()

    def collect_items(self):
        if self.env.is_item_at(self.x, self.y):
            self.pick()
        else:
            self.explore_or_move_to_item()

    def return_home(self):
        if (self.x, self.y) == (self.start_x, self.start_y):
            self.drop_all_items()
        else:
            self.move_to(self.start_x, self.start_y)

    def explore_or_move_to_item(self):
        # Verifica se há itens visíveis e move-se diretamente para o item A se possível
        for direction in ['up', 'down', 'left', 'right']:
            next_x, next_y = self.next_position(direction)
            if self.env.is_item_at(next_x, next_y) and self.env.grid[next_x][next_y] == 'A':
                self.move(direction)
                return
        # Verifica se há outros itens visíveis e move-se diretamente para eles se possível
        for direction in ['up', 'down', 'left', 'right']:
            next_x, next_y = self.next_position(direction)
            if self.env.is_item_at(next_x, next_y) and self.env.grid[next_x][next_y] != 'I':
                self.move(direction)
                return
        # Se não há itens visíveis de tipo A ou diferentes de tipo I, explora uma célula aleatória não explorada
        directions = ['up', 'down', 'left', 'right']
        random.shuffle(directions)
        for direction in directions:
            next_x, next_y = self.next_position(direction)
            if (next_x, next_y) not in self.explored:
                self.move(direction)
                return

        # Se todas as células vizinhas foram exploradas, move-se aleatoriamente
        self.move(random.choice(['up', 'down', 'left', 'right']))


    def move_to(self, target_x, target_y):
        # Calcula a direção mais curta para alcançar o ponto de destino
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

    def drop_all_items(self):
        # Supondo que o agente possa segurar mais de um item, ele os soltaria todos no ponto de partida
        self.holding_item = False  # Resetar o status de segurar itens

class UtilityAgent(Agent):
    def __init__(self, env, start_x=1, start_y=1, color=WHITE, name="Agent"):
        super().__init__(env, start_x, start_y,color, name)
        self.total_points = 0
        self.utility_threshold = 10  # Limiar de utilidade para decidir se deve coletar ou não um item
        self.explored = set()  # Conjunto de posições já exploradas

    def act(self):
        if self.holding_item:
            self.return_home()
        else:
            self.decide_action()

    def decide_action(self):
        # Calcula a utilidade esperada de coletar um item em cada célula vizinha
        expected_utilities = {}
        for direction in ['up', 'down', 'left', 'right']:
            next_x, next_y = self.next_position(direction)
            if self.env.is_item_at(next_x, next_y):
                expected_utilities[direction] = self.calculate_utility(next_x, next_y)

        if expected_utilities:
            # Se houver células com utilidade positiva, escolhe a que maximiza a utilidade
            best_direction = max(expected_utilities, key=expected_utilities.get)
            if expected_utilities[best_direction] > self.utility_threshold:
                self.move(best_direction)
            else:
                self.explore()
        else:
            # Se não houver itens visíveis, explora uma célula aleatória não explorada
            self.explore()


    def explore(self):
        directions = ['up', 'down', 'left', 'right']
        random.shuffle(directions)  # Explora direções aleatoriamente
        unexplored_directions = [direction for direction in directions if self.can_move(direction)]

        if unexplored_directions:
            # Se houver direções não exploradas disponíveis, move-se para a primeira delas.
            self.move(unexplored_directions[0])
        else:
            # Se todas as direções foram exploradas, tenta encontrar uma direção para se mover que não leve fora dos limites
            self.move_to_previously_explored()

    def can_move(self, direction):
        """Verifica se pode mover na direção especificada sem sair dos limites e sem ir para uma célula já explorada."""
        next_x, next_y = self.next_position(direction)
        return (0 <= next_x < self.env.size and 
                0 <= next_y < self.env.size and 
                (next_x, next_y) not in self.explored)

    def calculate_utility(self, x, y):
        # Calcula a utilidade esperada de coletar um item em uma célula específica
        # Aqui, a utilidade é uma função simples dos pontos obtidos e do tempo gasto
        points = self.env.get_item_points(x, y)
        distance = abs(self.x - x) + abs(self.y - y)
        utility = points - distance  # Utilidade simples: pontos - distância
        return utility

    def return_home(self):
        if (self.x, self.y) == (self.start_x, self.start_y):
            self.drop()
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
        text = font.render(f"{agent.name}: {agent.score}", True, BLACK)
        screen.blit(text, (screen.get_width() - 230, y_offset))
        pygame.draw.rect(screen, agent.color, (screen.get_width() - 270, y_offset + 5, 15, 15))  # Mostrar a cor ao lado do placar
        y_offset += 30

    pygame.display.flip()

# Função principal
def main():
    pygame.init()

    size = 20
    env = Environment(size=size, total_items=10)
    agents = [
        ReactiveAgent(env, color=RED, name="Reactive Agent "),
        StateAgent(env, color=BLUE, name="State Agent "),
        GoalAgent(env, color=BLACK, name="Goal Agent"),
        UtilityAgent(env, color=PURPLE, name="Utility Agent"),
    ]
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
        clock.tick(5)  # Ajuste a velocidade de exibição

    pygame.quit()

if __name__ == "__main__":
    main()
