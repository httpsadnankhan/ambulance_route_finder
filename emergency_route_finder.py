import heapq
import math
import random
import time
import tkinter as tk
from collections import deque
from tkinter import messagebox, ttk


# The map uses approximate latitude and longitude values.
JUNCTIONS = {
    "Saddar": (24.8556, 67.0214), "Tower": (24.8465, 67.0110),
    "Keamari": (24.8330, 66.9810), "Mauripur": (24.8800, 66.9700),
    "SITE": (24.9050, 66.9900), "Orangi Town": (24.9500, 66.9900),
    "Nazimabad": (24.9120, 67.0300), "North Nazimabad": (24.9350, 67.0400),
    "Lasbela": (24.8800, 67.0260), "Numaish": (24.8725, 67.0335),
    "Liaquatabad": (24.8960, 67.0450), "Federal B Area": (24.9270, 67.0620),
    "Water Pump": (24.9330, 67.0790), "Tariq Road": (24.8720, 67.0560),
    "Shaheed-e-Millat": (24.8830, 67.0620), "Hassan Square": (24.9040, 67.0730),
    "Gulshan Chowrangi": (24.9215, 67.0920), "NIPA": (24.9090, 67.0870),
    "Johar Mor": (24.9140, 67.1210), "Safoora": (24.9430, 67.1300),
    "Airport": (24.9065, 67.1600), "Drigh Road": (24.8880, 67.1250),
    "Malir Halt": (24.8915, 67.2030), "Landhi": (24.8530, 67.2080),
    "Korangi Crossing": (24.8410, 67.1180), "Karsaz": (24.8680, 67.0870),
    "Nursery": (24.8610, 67.0680), "Teen Talwar": (24.8340, 67.0280),
    "Do Talwar": (24.8240, 67.0310), "Sea View": (24.7960, 67.0260),
    "Gizri": (24.8270, 67.0480), "DHA Phase 2": (24.8200, 67.0680),
}

HOSPITALS = {
    "Civil Hospital": (24.8588, 67.0085), "JPMC": (24.8510, 67.0477),
    "AKUH": (24.8921, 67.0742), "Liaquat National": (24.8908, 67.0665),
    "Ziauddin Clifton": (24.8168, 67.0316),
    "South City Hospital": (24.8147, 67.0383),
    "Abbasi Shaheed": (24.9185, 67.0345),
    "Indus Hospital": (24.8286, 67.1143),
}

ROADS = [
    ("Tower", "Saddar"), ("Tower", "Civil Hospital"), ("Saddar", "Civil Hospital"),
    ("Tower", "Keamari"), ("Keamari", "Mauripur"), ("Mauripur", "SITE"),
    ("SITE", "Orangi Town"), ("SITE", "Nazimabad"), ("Orangi Town", "North Nazimabad"),
    ("Orangi Town", "Nazimabad"), ("SITE", "Lasbela"), ("Civil Hospital", "Numaish"),
    ("Saddar", "Numaish"), ("Saddar", "Teen Talwar"), ("Saddar", "JPMC"),
    ("Saddar", "Nursery"), ("JPMC", "Nursery"), ("Teen Talwar", "Do Talwar"),
    ("Teen Talwar", "Gizri"), ("Do Talwar", "Gizri"), ("Do Talwar", "Ziauddin Clifton"),
    ("Do Talwar", "South City Hospital"), ("Ziauddin Clifton", "South City Hospital"),
    ("Do Talwar", "Sea View"), ("South City Hospital", "Sea View"),
    ("Gizri", "DHA Phase 2"), ("Gizri", "Nursery"), ("DHA Phase 2", "Korangi Crossing"),
    ("DHA Phase 2", "Karsaz"), ("Nursery", "Karsaz"), ("Nursery", "Tariq Road"),
    ("Tariq Road", "Numaish"), ("Tariq Road", "Shaheed-e-Millat"),
    ("Shaheed-e-Millat", "Liaquat National"), ("Shaheed-e-Millat", "Liaquatabad"),
    ("Liaquat National", "AKUH"), ("Liaquat National", "Hassan Square"),
    ("AKUH", "Hassan Square"), ("AKUH", "Karsaz"), ("Numaish", "Lasbela"),
    ("Lasbela", "Liaquatabad"), ("Lasbela", "Nazimabad"),
    ("Liaquatabad", "Nazimabad"), ("Liaquatabad", "Federal B Area"),
    ("Nazimabad", "Abbasi Shaheed"), ("Abbasi Shaheed", "North Nazimabad"),
    ("Abbasi Shaheed", "Federal B Area"), ("North Nazimabad", "Federal B Area"),
    ("Federal B Area", "Water Pump"), ("Federal B Area", "Hassan Square"),
    ("Water Pump", "Gulshan Chowrangi"), ("Hassan Square", "Gulshan Chowrangi"),
    ("Hassan Square", "NIPA"), ("Gulshan Chowrangi", "NIPA"),
    ("Gulshan Chowrangi", "Johar Mor"), ("NIPA", "Johar Mor"), ("NIPA", "Karsaz"),
    ("Johar Mor", "Safoora"), ("Johar Mor", "Airport"), ("Safoora", "Airport"),
    ("Karsaz", "Drigh Road"), ("Drigh Road", "Airport"), ("Airport", "Malir Halt"),
    ("Drigh Road", "Malir Halt"), ("Malir Halt", "Landhi"), ("Landhi", "Korangi Crossing"),
    ("Korangi Crossing", "Indus Hospital"), ("Korangi Crossing", "Drigh Road"),
]

POINTS = {**JUNCTIONS, **HOSPITALS}
ALGORITHMS = ("DFS", "BFS", "Greedy", "A*")
COLORS = {"DFS": "#8e44ad", "BFS": "#2980b9", "Greedy": "#e67e22", "A*": "#27ae60"}
SPEED_KMH = 50
ROAD_LENGTH_FACTOR = 1.25
MAP_WIDTH, MAP_HEIGHT, MAP_PADDING = 980, 720, 50


def distance(point_a, point_b):
    """Return the straight-line distance between two GPS points in kilometres."""
    lat1, lon1 = map(math.radians, point_a)
    lat2, lon2 = map(math.radians, point_b)
    lat_difference = lat2 - lat1
    lon_difference = lon2 - lon1
    value = math.sin(lat_difference / 2) ** 2
    value += math.cos(lat1) * math.cos(lat2) * math.sin(lon_difference / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(value))


class Map:
    """Store roads and find routes between map points."""

    def __init__(self):
        self.roads = {name: {} for name in POINTS}
        self.road_list = list(ROADS)
        self.closed_roads = set()

        for first, second in ROADS:
            length = distance(POINTS[first], POINTS[second]) * ROAD_LENGTH_FACTOR
            self.roads[first][second] = length
            self.roads[second][first] = length

    def open_neighbors(self, place):
        result = {}
        for neighbor, length in self.roads[place].items():
            if frozenset((place, neighbor)) not in self.closed_roads:
                result[neighbor] = length
        return result

    def guess_distance(self, place, destination):
        return distance(POINTS[place], POINTS[destination])

    def path_length(self, path):
        return sum(self.roads[first][second] for first, second in zip(path, path[1:]))

    def make_path(self, previous, start, destination):
        path = [destination]
        while path[-1] != start:
            path.append(previous[path[-1]])
        return list(reversed(path))

    def depth_first(self, start, destination):
        stack = [(start, [start])]
        visited = set()
        checked = []
        while stack:
            place, path = stack.pop()
            if place in visited:
                continue
            visited.add(place)
            checked.append(place)
            if place == destination:
                return path, checked
            for neighbor in sorted(self.open_neighbors(place), reverse=True):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
        return None, checked

    def breadth_first(self, start, destination):
        places = deque([start])
        previous = {}
        visited = {start}
        checked = []
        while places:
            place = places.popleft()
            checked.append(place)
            if place == destination:
                return self.make_path(previous, start, destination), checked
            for neighbor in sorted(self.open_neighbors(place)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    previous[neighbor] = place
                    places.append(neighbor)
        return None, checked

    def best_first(self, start, destination, use_real_distance):
        queue = [(self.guess_distance(start, destination), 0, start)]
        previous = {}
        visited = set()
        total_distance = {start: 0}
        checked = []
        number = 0

        while queue:
            _, _, place = heapq.heappop(queue)
            if place in visited:
                continue
            visited.add(place)
            checked.append(place)
            if place == destination:
                return self.make_path(previous, start, destination), checked

            for neighbor, road_length in self.open_neighbors(place).items():
                new_distance = total_distance[place] + road_length
                if new_distance < total_distance.get(neighbor, float("inf")):
                    total_distance[neighbor] = new_distance
                    previous[neighbor] = place
                    number += 1
                    if use_real_distance:
                        priority = new_distance + self.guess_distance(neighbor, destination)
                    else:
                        priority = self.guess_distance(neighbor, destination)
                    heapq.heappush(queue, (priority, number, neighbor))
        return None, checked

    def find(self, algorithm, start, destination):
        start_time = time.perf_counter()
        if algorithm == "DFS":
            path, checked = self.depth_first(start, destination)
        elif algorithm == "BFS":
            path, checked = self.breadth_first(start, destination)
        else:
            path, checked = self.best_first(start, destination, algorithm == "A*")
        milliseconds = (time.perf_counter() - start_time) * 1000
        return path, checked, milliseconds

    def nearest_hospital(self, start):
        nearest = None
        shortest = float("inf")
        for hospital in HOSPITALS:
            path, _, _ = self.find("A*", start, hospital)
            if path:
                length = self.path_length(path)
                if length < shortest:
                    nearest, shortest = hospital, length
        return nearest


class RouteApp(tk.Tk):
    """The small Tkinter window used by the route finder."""

    def __init__(self):
        super().__init__()
        self.title("Emergency Route Finder - Karachi")
        self.geometry("1380x790")
        self.configure(bg="#eef2f5")

        self.map = Map()
        self.positions = self.make_positions()
        self.ambulance = None
        self.destination = None
        self.route = []
        self.ambulance_position = None
        self.is_moving = False
        self.route_step = 0
        self.route_progress = 0
        self.move_job = None
        self.animation_job = None
        self.explored = []
        self.route_lines = []

        self.location_text = tk.StringVar()
        self.hospital_text = tk.StringVar(value="Auto (Nearest)")
        self.algorithm_text = tk.StringVar(value="A*")
        self.click_mode = tk.StringVar(value="ambulance")
        self.animate_search = tk.BooleanVar(value=True)
        self.move_speed = tk.DoubleVar(value=4)
        self.details_text = tk.StringVar(value="No route yet.")
        self.status_text = tk.StringVar(value="Choose an ambulance location.")

        self.make_widgets()
        self.draw_map()

    def make_positions(self):
        latitudes = [point[0] for point in POINTS.values()]
        longitudes = [point[1] for point in POINTS.values()]
        middle_latitude = math.radians((min(latitudes) + max(latitudes)) / 2)
        width = (max(longitudes) - min(longitudes)) * math.cos(middle_latitude)
        height = max(latitudes) - min(latitudes)
        scale = min(
            (MAP_WIDTH - 2 * MAP_PADDING) / width,
            (MAP_HEIGHT - 2 * MAP_PADDING) / height,
        )
        positions = {}
        for name, (latitude, longitude) in POINTS.items():
            x = MAP_PADDING + (longitude - min(longitudes)) * math.cos(middle_latitude) * scale
            y = MAP_PADDING + (max(latitudes) - latitude) * scale
            positions[name] = (x, y)
        return positions

    def make_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#eef2f5")
        style.configure("TLabel", background="#eef2f5")
        style.configure("TLabelframe", background="#eef2f5")
        style.configure("TLabelframe.Label", background="#eef2f5", font=("Segoe UI", 10, "bold"))

        left = ttk.Frame(self, padding=8)
        left.pack(side="left", fill="y")
        tk.Label(left, text="Ambulance Route Finder", bg="#c0392b", fg="white",
                 font=("Segoe UI", 13, "bold"), pady=8).pack(fill="x", pady=(0, 8))

        location_box = ttk.LabelFrame(left, text="1. Ambulance location", padding=6)
        location_box.pack(fill="x", pady=3)
        location_list = ttk.Combobox(
            location_box, textvariable=self.location_text,
            values=sorted(POINTS), state="readonly", width=30,
        )
        location_list.pack(fill="x")
        location_list.bind("<<ComboboxSelected>>", self.location_selected)

        hospital_box = ttk.LabelFrame(left, text="2. Hospital", padding=6)
        hospital_box.pack(fill="x", pady=3)
        ttk.Combobox(
            hospital_box, textvariable=self.hospital_text,
            values=["Auto (Nearest)"] + list(HOSPITALS), state="readonly", width=30,
        ).pack(fill="x")

        algorithm_box = ttk.LabelFrame(left, text="3. Search algorithm", padding=6)
        algorithm_box.pack(fill="x", pady=3)
        for algorithm in ALGORITHMS:
            ttk.Radiobutton(
                algorithm_box, text=algorithm, value=algorithm,
                variable=self.algorithm_text,
            ).pack(anchor="w")
        ttk.Checkbutton(
            algorithm_box, text="Show search animation",
            variable=self.animate_search,
        ).pack(anchor="w")

        click_box = ttk.LabelFrame(left, text="Map click mode", padding=6)
        click_box.pack(fill="x", pady=3)
        ttk.Radiobutton(
            click_box, text="Place ambulance", value="ambulance",
            variable=self.click_mode,
        ).pack(anchor="w")
        ttk.Radiobutton(
            click_box, text="Block / open a road", value="road",
            variable=self.click_mode,
        ).pack(anchor="w")
        buttons = ttk.Frame(click_box)
        buttons.pack(fill="x", pady=4)
        ttk.Button(buttons, text="Random blocks", command=self.random_blocks).pack(side="left", fill="x", expand=True)
        ttk.Button(buttons, text="Clear blocks", command=self.clear_blocks).pack(side="left", fill="x", expand=True)

        action_box = ttk.LabelFrame(left, text="Actions", padding=6)
        action_box.pack(fill="x", pady=3)
        ttk.Button(action_box, text="Find route", command=self.find_route).pack(fill="x", pady=1)
        ttk.Button(action_box, text="Start ambulance", command=self.start_ambulance).pack(fill="x", pady=1)
        ttk.Button(action_box, text="Compare algorithms", command=self.compare_algorithms).pack(fill="x", pady=1)
        ttk.Button(action_box, text="Reset", command=self.reset).pack(fill="x", pady=1)
        ttk.Label(action_box, text="Animation speed").pack(anchor="w", pady=(5, 0))
        tk.Scale(action_box, from_=1, to=14, orient="horizontal",
                 variable=self.move_speed, showvalue=False, length=180,
                 bg="#eef2f5", highlightthickness=0).pack()

        details_box = ttk.LabelFrame(left, text="Route details", padding=6)
        details_box.pack(fill="x", pady=3)
        ttk.Label(details_box, textvariable=self.details_text,
                  justify="left", wraplength=300).pack(anchor="w")

        compare_box = ttk.LabelFrame(left, text="Comparison", padding=6)
        compare_box.pack(fill="x", pady=3)
        columns = ("algorithm", "km", "minutes", "nodes")
        self.table = ttk.Treeview(compare_box, columns=columns, show="headings", height=4)
        for column, title, width in zip(columns, ("Algorithm", "km", "ETA", "Nodes"), (105, 50, 55, 55)):
            self.table.heading(column, text=title)
            self.table.column(column, width=width, anchor="center")
        self.table.pack(fill="x")
        self.best_text = ttk.Label(compare_box, text="")
        self.best_text.pack(anchor="w", pady=(4, 0))

        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        self.canvas = tk.Canvas(
            right, width=MAP_WIDTH, height=MAP_HEIGHT, bg="#f6f3ec",
            highlightthickness=1, highlightbackground="#bbb",
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.map_clicked)
        tk.Label(right, textvariable=self.status_text, anchor="w",
                 bg="#2c3e50", fg="white", padx=8, pady=5).pack(fill="x")

    def draw_map(self):
        self.canvas.delete("all")
        for first, second in self.map.road_list:
            x1, y1 = self.positions[first]
            x2, y2 = self.positions[second]
            closed = frozenset((first, second)) in self.map.closed_roads
            self.canvas.create_line(
                x1, y1, x2, y2, fill="#e74c3c" if closed else "#b3bcc5",
                width=4 if closed else 3, dash=(7, 4) if closed else None,
            )

        for path, color, width in self.route_lines:
            points = [value for name in path for value in self.positions[name]]
            if len(points) >= 4:
                self.canvas.create_line(*points, fill=color, width=width, capstyle="round")

        for name in self.explored:
            x, y = self.positions[name]
            self.canvas.create_oval(x - 9, y - 9, x + 9, y + 9, fill="#fbe08a", outline="#e5a50a")

        for name, (x, y) in self.positions.items():
            if name in HOSPITALS:
                self.canvas.create_rectangle(x - 9, y - 9, x + 9, y + 9, fill="#e74c3c", outline="white")
                self.canvas.create_text(x, y, text="H", fill="white", font=("Segoe UI", 9, "bold"))
                self.canvas.create_text(x, y - 18, text=name, fill="#922b21", font=("Segoe UI", 8, "bold"))
            else:
                self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="white", outline="#34495e")
                self.canvas.create_text(x, y + 13, text=name, fill="#34495e", font=("Segoe UI", 7))

        if self.destination:
            x, y = self.positions[self.destination]
            self.canvas.create_oval(x - 16, y - 16, x + 16, y + 16, outline="#27ae60", width=3)
        if self.ambulance_position:
            x, y = self.ambulance_position
            self.canvas.create_rectangle(x - 12, y - 20, x + 12, y - 5, fill="white", outline="#c0392b", width=2)
            self.canvas.create_text(x, y - 13, text="+", fill="#c0392b", font=("Segoe UI", 11, "bold"))
            self.canvas.create_oval(x - 4, y - 26, x + 4, y - 20, fill="#e74c3c", outline="")

    @staticmethod
    def line_distance(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        part = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        part = max(0, min(1, part))
        return math.hypot(px - x1 - part * dx, py - y1 - part * dy)

    def map_clicked(self, event):
        if self.click_mode.get() == "ambulance":
            closest = min(
                self.positions,
                key=lambda name: math.hypot(event.x - self.positions[name][0], event.y - self.positions[name][1]),
            )
            x, y = self.positions[closest]
            if math.hypot(event.x - x, event.y - y) < 28:
                self.choose_location(name=closest)
            return

        road = min(
            self.map.road_list,
            key=lambda item: self.line_distance(
                event.x, event.y, *self.positions[item[0]], *self.positions[item[1]],
            ),
        )
        if self.line_distance(event.x, event.y, *self.positions[road[0]], *self.positions[road[1]]) < 10:
            key = frozenset(road)
            if key in self.map.closed_roads:
                self.map.closed_roads.remove(key)
                self.status_text.set("Road opened again.")
            else:
                self.map.closed_roads.add(key)
                self.status_text.set("Road blocked.")
            self.check_route_after_road_change()

    def location_selected(self, event):
        self.choose_location(event.widget.get())

    def choose_location(self, name=None):
        if self.is_moving:
            messagebox.showinfo("Ambulance is moving", "Wait until it arrives or press Reset.")
            return
        name = name or self.location_text.get()
        self.ambulance = name
        self.location_text.set(name)
        self.destination = None
        self.route = []
        self.route_lines = []
        self.explored = []
        self.ambulance_position = self.positions[name]
        self.details_text.set("No route yet.")
        self.status_text.set("Location selected. Click Find route.")
        self.draw_map()

    def check_route_after_road_change(self):
        if self.route and any(
            frozenset((first, second)) in self.map.closed_roads
            for first, second in zip(self.route, self.route[1:])
        ):
            if self.is_moving:
                self.reroute()
            else:
                self.find_route(show_message=False)
        else:
            self.draw_map()

    def choose_destination(self, start):
        if self.hospital_text.get().startswith("Auto"):
            return self.map.nearest_hospital(start)
        return self.hospital_text.get()

    def make_route(self, start):
        destination = self.choose_destination(start)
        if not destination:
            return None
        path, checked, milliseconds = self.map.find(self.algorithm_text.get(), start, destination)
        if not path:
            return None
        length = self.map.path_length(path)
        return {
            "path": path, "checked": checked, "destination": destination,
            "length": length, "minutes": length / SPEED_KMH * 60,
            "milliseconds": milliseconds, "algorithm": self.algorithm_text.get(),
        }

    def show_details(self, route):
        self.details_text.set(
            f"Algorithm: {route['algorithm']}\n"
            f"Hospital: {route['destination']}\n"
            f"Distance: {route['length']:.2f} km\n"
            f"ETA: {route['minutes']:.1f} minutes\n"
            f"Nodes checked: {len(route['checked'])}\n"
            f"Time: {route['milliseconds']:.3f} ms"
        )

    def find_route(self, show_message=True, after=None):
        if not self.ambulance or self.is_moving:
            if show_message:
                messagebox.showwarning("Choose location", "Select an ambulance location first.")
            return
        self.stop_search_animation()
        route = self.make_route(self.ambulance)
        if not route:
            self.route = []
            self.route_lines = []
            self.draw_map()
            if show_message:
                messagebox.showwarning("No route", "No open route to a hospital was found.")
            return

        self.route = route["path"]
        self.destination = route["destination"]
        self.show_details(route)
        self.status_text.set(f"Route found to {route['destination']}.")

        if self.animate_search.get() and show_message:
            self.animate_checked_nodes(route["checked"], route, after)
        else:
            self.route_lines = [(self.route, COLORS[route["algorithm"]], 7)]
            self.draw_map()
            if after:
                after()

    def animate_checked_nodes(self, checked, route, after):
        self.explored = []
        position = [0]

        def show_next():
            if position[0] >= len(checked):
                self.explored = []
                self.route_lines = [(route["path"], COLORS[route["algorithm"]], 7)]
                self.animation_job = None
                self.draw_map()
                if after:
                    after()
                return
            self.explored = checked[:position[0] + 2]
            position[0] += 2
            self.draw_map()
            self.animation_job = self.after(70, show_next)

        show_next()

    def stop_search_animation(self):
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None

    def random_blocks(self):
        free_roads = [road for road in self.map.road_list if frozenset(road) not in self.map.closed_roads]
        for road in random.sample(free_roads, min(4, len(free_roads))):
            self.map.closed_roads.add(frozenset(road))
        self.status_text.set("Some roads were blocked randomly.")
        self.check_route_after_road_change()

    def clear_blocks(self):
        self.map.closed_roads.clear()
        self.status_text.set("All roads are open.")
        self.draw_map()

    def compare_algorithms(self):
        if not self.ambulance or self.is_moving:
            messagebox.showwarning("Choose location", "Select an ambulance location first.")
            return
        destination = self.choose_destination(self.ambulance)
        if not destination:
            messagebox.showwarning("No route", "No hospital can be reached.")
            return

        results = []
        for algorithm in ALGORITHMS:
            path, checked, milliseconds = self.map.find(algorithm, self.ambulance, destination)
            if path:
                length = self.map.path_length(path)
                results.append((algorithm, path, length, checked, milliseconds))
        if not results:
            messagebox.showwarning("No route", "No open route was found.")
            return

        self.table.delete(*self.table.get_children())
        best = min(results, key=lambda result: (result[2], len(result[3])))
        for algorithm, path, length, checked, milliseconds in results:
            self.table.insert(
                "", "end",
                values=(algorithm, f"{length:.2f}", f"{length / SPEED_KMH * 60:.1f}", len(checked)),
            )
        self.best_text.config(text=f"Shortest route: {best[0]} ({best[2]:.2f} km)")
        self.route, self.destination = best[1], destination
        self.route_lines = [
            (path, COLORS[algorithm], max(3, 12 - index * 2))
            for index, (algorithm, path, _, _, _) in enumerate(sorted(results, key=lambda item: -item[2]))
        ]
        self.details_text.set(
            f"Hospital: {destination}\nShortest algorithm: {best[0]}\n"
            f"Distance: {best[2]:.2f} km\nETA: {best[2] / SPEED_KMH * 60:.1f} minutes"
        )
        self.status_text.set("Algorithm comparison finished.")
        self.draw_map()

    def start_ambulance(self):
        if not self.ambulance:
            messagebox.showwarning("Choose location", "Select an ambulance location first.")
            return
        if self.is_moving:
            return
        if not self.route or self.route[0] != self.ambulance:
            self.find_route(after=self.begin_moving)
        else:
            self.begin_moving()

    def begin_moving(self):
        if not self.route:
            return
        self.is_moving = True
        self.route_step = 0
        self.route_progress = 0
        self.move_ambulance()

    def move_ambulance(self):
        if not self.is_moving:
            return
        remaining = self.move_speed.get()
        while remaining > 0 and self.route_step < len(self.route) - 1:
            first = self.route[self.route_step]
            second = self.route[self.route_step + 1]
            x1, y1 = self.positions[first]
            x2, y2 = self.positions[second]
            segment = math.hypot(x2 - x1, y2 - y1)
            left = segment * (1 - self.route_progress)
            if remaining >= left:
                remaining -= left
                self.route_step += 1
                self.route_progress = 0
            else:
                self.route_progress += remaining / segment
                remaining = 0

        if self.route_step >= len(self.route) - 1:
            self.ambulance = self.route[-1]
            self.location_text.set(self.ambulance)
            self.ambulance_position = self.positions[self.ambulance]
            self.is_moving = False
            self.route_lines = []
            self.draw_map()
            self.status_text.set(f"Ambulance arrived at {self.ambulance}.")
            messagebox.showinfo("Arrived", f"Ambulance reached {self.ambulance}.")
            return

        first = self.route[self.route_step]
        second = self.route[self.route_step + 1]
        x1, y1 = self.positions[first]
        x2, y2 = self.positions[second]
        self.ambulance_position = (
            x1 + (x2 - x1) * self.route_progress,
            y1 + (y2 - y1) * self.route_progress,
        )
        self.draw_map()
        self.move_job = self.after(30, self.move_ambulance)

    def reroute(self):
        self.is_moving = False
        if self.move_job:
            self.after_cancel(self.move_job)
            self.move_job = None
        current_place = self.route[self.route_step]
        self.ambulance = current_place
        self.ambulance_position = self.positions[current_place]
        self.find_route(show_message=False, after=self.begin_moving)

    def reset(self):
        self.stop_search_animation()
        if self.move_job:
            self.after_cancel(self.move_job)
            self.move_job = None
        self.map.closed_roads.clear()
        self.ambulance = None
        self.destination = None
        self.route = []
        self.route_lines = []
        self.explored = []
        self.ambulance_position = None
        self.is_moving = False
        self.location_text.set("")
        self.table.delete(*self.table.get_children())
        self.best_text.config(text="")
        self.details_text.set("No route yet.")
        self.status_text.set("Choose an ambulance location.")
        self.draw_map()


if __name__ == "__main__":
    RouteApp().mainloop()
