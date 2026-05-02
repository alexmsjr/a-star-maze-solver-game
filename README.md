
# a-star-maze-solver-game
A small maze game featuring 9 search algorithm implementation. This project was created as an assignment for us Artificial Intelligence university course.

![Maze](https://i.imgur.com/OlDQgAZ.gif)
## 🛠 Search Algorithms Included

-   **Breadth-First Search (Amplitude)**
    
-   **Depth-First Search (Profundidade)**
    
-   **Depth-Limited Search (Profundidade Limitada)**
    
-   **Iterative Deepening (Aprofundamento Iterativo)**
    
-   **Bidirectional Search (Bidirecional)**
    
-   **Uniform Cost Search (Custo Uniforme)**
    
-   **Greedy Search (Gulosa)**
    
-   **A Star Search (A-Estrela)**
    
-   **IDA Search (AIA-Estrela)**

## 📁 Project Structure

#### 🖥️ Interface
- **main.py**: The application's entry point. It contains th Pygames main loop and the user interface.
#### 🧠 Search Engines
- **NPsearch.py**:  (Non-Priority Search), Implements Uninformed Search algorithms. It includes Breadth-First Search, Depth-First Search, Depth-Limited Search, Iterative Deepening Search and Bidirectional Search. In addition to auxiliary methods for the operation of the algorithms
- **Psearch.py**:  (Priority Search), Implements informed Search algorithms. It includes Uniform Cost Search, Greedy Search, A Star Search, Iterative Deepening A Star Search. In addition to auxiliary methods for the operation of the algorithms.
#### 🏗️ Data Structures (Nodes)
- **NPnode.py**: base node class storing the current state (x, y coordinates), the parent node , and the current depth.
- **Pnode.py**: An extension of the base node class. It is designed for cost-based searches.
#### 🛠️ Utility Functions
- **AuxFunctions.py**:  Handles the maze generation logic. It utilizes a variation of Depth-First to "dig"  tunnels in a maze.
## 📋 Technologies Used
- **Language:** Python 3.11.9 🐍
- **Graphic Library:** Pygame 🎮
## 🛠️ Installation & Usage
#### 1. Clone or download the repository.

```bash
git clone https://github.com/alexmsjr/a-star-maze-solver-game.git
```
#### 2. Navigate to the project directory.
```bash
cd a-star-maze-solver-game
```
#### 3. Install Python 3.11.
```bash
winget install -e --id Python.Python.3.11
```
#### 4. Create a virtual environment.
```bash
# Create the env
python -3.11 -m venv myEnv

# Active the env
.\myEnv\Scripts\activate
```
#### 5. Install libraries.
```bash
# Update pip
python -m pip install --upgrade pip
pip install pygame numpy
```
#### 6. Run Main.py.
```bash
python main.py
```

## 🎮 Graphical Interface Guide
The interface is divided into two main sections: the **Maze Display** (top) and the **Command Center** (bottom).

### 1. The Maze
-   **Walls:** Represented by colored cars parked throughout the lot.
    
-   **Origin (Start):** Represented by a **White Car**.
    
-   **Goal (Objective):** Represented by a **Finish Line**.
    
-   **Exploration:** Paths explored by the algorithm are highlighted in **Blue**.
    
-   **Final Path:** Once the goal is reached, the optimal route is highlighted in **Green**.
### 2. The Command Center
Located at the bottom of the screen, the Command Center is organized into several functional panels (from left to right):
#### **A. Customization Panel**

Clicking the **CUSTOMIZAR LABIRINTO** button reveals the customization drawer:

-   **Maze Size (Tamanho do Labirinto):** Select a predefined size for the grid.
    
    -   Note: Changes only take effect after clicking APLICAR MODIFICAÇÕES.
        
-   **Tools (Ferramentas):**
    
    -   **Change Origin (Car Icon):** When active, click anywhere on the maze to relocate the White Car (Start).
        
    -   **Set Goal (Finish Line Icon):** When active, click anywhere on the maze to relocate the objective.
        
    -   **Break Asphalt (Hammer Icon):** This tool changes the terrain. It "breaks" the road, increasing the traversal cost of that node from **1 to 10**.
        
    
    -   Tip: Placing the Origin, Goal, or using the Hammer on a car will "clear" that obstacle.
        
-   **Apply Modifications (Aplicar Modificações):** Confirms changes to the maze size. This will reset the terrain and randomize wall placements.
    
-   **Randomize (Aleatorizar):** Generates a new random maze layout while keeping the current size, origin, and goal.
#### **B. Animation Controls**

-   **Skip Animations (Pular Animações):** A toggle switch. When enabled, the algorithm will calculate the path instantly without showing the step-by-step exploration.
- **Speed Slider:** Controls the delay between animation frames.
    
    -   Default: 50ms.
        
    -   **Up:** Decreases delay (Faster animation).
        
    -   **Down:** Increases delay (Slower animation).
 #### **C. Search Algorithms & Displays**

There are nine algorithm buttons available. Above them, three digital displays track performance:

1.  **Cost (CUSTO):** Shows the total mathematical cost of the path found (considering terrain weights).
    
2.  **Nodes (NÓS):** Shows the total number of nodes explored.
    
    -   Note: For **Profundidade Iterativa** and **IDA**, this count is cumulative, summing all nodes explored across all iterations.*
        
3.  **Limit (LIMITE):** A user-input field. Click and type to set the maximum depth for **Profundidade Limitada** or **Profundidade Iterativa**.
    

#### **D. Utility Buttons**

-   **AJUDA (Help):** Displays a summary of interface functions.
    
-   **SOBRE (About):** Provides information about the software and the development team.
    
-   **SAIR (Quit):** Safely closes the application.

## 👷‍♂️ Contributors
[Alexandre Marciano](https://github.com/alexmsjr)
[Davi Santos](https://github.com/Davi1403)
