# Emergency Route Finder

A desktop demonstration app that visualizes ambulance routes through a small, predefined road network based on Karachi, Pakistan. Choose an ambulance location, select a hospital or let the app choose one, and compare several graph-search algorithms while blocking and reopening roads on the map.

> **Important:** This is an educational simulation, not a navigation or emergency-dispatch system. Locations and roads are approximate, and routes, distances, and arrival times must not be used for real-world emergency response.

## Features

- Interactive map of modeled Karachi junctions, roads, and hospitals.
- Route search using **DFS**, **BFS**, **Greedy Best-First Search**, or **A\***.
- Automatic destination selection based on the shortest available route to a hospital.
- Route distance, estimated travel time, explored-node count, and search duration.
- Search animation and a visual ambulance movement simulation.
- Road closures that can be toggled on the map or generated randomly.
- Algorithm comparison for the selected destination.
- Automatic route recalculation when a road on the current route is blocked.

## Requirements

- Python 3.6 or later.
- Tkinter, which is included with most standard Python installations.
- No third-party Python packages are required.

On some Linux distributions, Tkinter is packaged separately (for example, as `python3-tk`). On Windows, use a Python installation that includes Tcl/Tk.

## Run the application

Open PowerShell or Command Prompt in the project folder and run:

```powershell
py emergency_route_finder.py
```

If the Python launcher is unavailable, try:

```powershell
python emergency_route_finder.py
```

The application opens a desktop window; it does not start a web server or require internet access.

## Using the application

1. **Choose an ambulance location.** Select a location from the list, or leave **Place ambulance** selected and click near a junction on the map.
2. **Choose a hospital.** Keep **Auto (Nearest)** to use the hospital with the shortest currently available route, or select a specific hospital.
3. **Choose a search algorithm.** Select DFS, BFS, Greedy, or A*. A* is selected by default.
4. **Find a route.** The app displays route information and, when **Show search animation** is enabled, animates the nodes explored before highlighting the route.
5. **Move the ambulance.** Click **Start ambulance** to animate movement along the current route. The animation is illustrative and does not represent a real driving speed.
6. **Change road availability.** Select **Block / open a road** and click a road segment to toggle it. Use **Random blocks** to close up to four currently open roads, or **Clear blocks** to reopen all roads.
7. **Compare algorithms.** Click **Compare algorithms** to display routes to the current destination and compare their distance, estimated time, and number of explored nodes.
8. **Reset.** Click **Reset** to clear the selected location, route, comparison, and road closures.

If a road on the active route is blocked while the ambulance is moving, the app stops the current movement and searches for a replacement route from the ambulance's current junction.

## Search algorithms and measurements

The map is represented as an undirected, weighted graph: junctions and hospitals are vertices, and roads are edges. Road weights are estimated distances in kilometres.

- **DFS (Depth-First Search):** explores one branch at a time. It finds a reachable route, but does not guarantee the route has the fewest roads or the least distance.
- **BFS (Breadth-First Search):** explores by number of roads from the start. It finds a route with the fewest edges, which is not necessarily the shortest route by distance.
- **Greedy Best-First Search:** prioritizes locations that appear geographically closer to the destination. It does not guarantee a shortest-distance route.
- **A\* Search:** combines distance already traveled with a straight-line distance estimate to the destination. With the app's non-negative road weights and geographic heuristic, it is intended to find a shortest-distance route in this modeled graph.

The straight-line heuristic uses the Haversine formula on the approximate latitude/longitude coordinates. Each road's modeled length is 1.25 times the straight-line distance between its endpoints. The displayed ETA is calculated using a fixed assumed speed of 50 km/h; traffic, road conditions, turns, and actual travel speeds are not modeled.

The comparison table reports route distance, estimated time, and explored-node count. The “Shortest route” result is chosen by distance, using explored-node count as a tie-breaker. Search duration shown in route details is the measured algorithm runtime on the current computer and is not a measure of real-world response time.

## Project structure

```text
.
├── emergency_route_finder.py   # Map data, graph search, Tkinter UI, and simulation
├── README.md                   # Setup, usage, and implementation notes
└── .gitignore                  # Python-generated and local development files
```

## Map data and customization

The modeled places, approximate coordinates, hospitals, and road connections are defined near the top of `emergency_route_finder.py` in `JUNCTIONS`, `HOSPITALS`, and `ROADS`. These are static sample data, not a live map feed. To change the modeled network, update these collections while ensuring each road endpoint is a key in `POINTS` (the combined junction and hospital mapping).

Other simulation assumptions, including the road-distance multiplier, fixed speed, and map dimensions, are defined by constants in the same file.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'tkinter'`:** Install the Tkinter package provided for your Python distribution, then run the script again.
- **The window does not appear:** Run the command from a desktop session with a graphical display; Tkinter requires a GUI environment.
- **No route is found:** Reopen some blocked roads, choose a different start location or hospital, or click **Reset** to clear all road closures.

