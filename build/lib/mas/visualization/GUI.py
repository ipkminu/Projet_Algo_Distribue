import tkinter as tk
import tkinter.font as tkFont
from tkinter import DISABLED, Toplevel
from mas.visualization.GraphViz import GraphViz
from mas.visualization.SimulationViz import SimulationViz
import re
import json
import os

class GUI(tk.Frame):

    autosize = "auto"

    def __init__(self, root, simulation, canvas_size=autosize):
        tk.Frame.__init__(self, root)

        self._graphViz = GraphViz()
        self._graphViz.init_from_graph(simulation.topology(), copy=False)
        self._simulationViz = SimulationViz(simulation, self._graphViz)

        # self._all_debug_options = [
        #     "Normal",
        #     "Vertex_visualization",
        #     "Full_visualization",
        #     "Simple_debug",
        #     "Exploration_debug",
        #     "Cartography_debug"
        # ]
        self._debug_options = self._load_debug_options()
        default_debug_option = "Normal"
        self._zoomed = False

        # Canvas
        self._canvas = tk.Canvas(self)

        # Buttons
        self._pause = True
        self._run_button = tk.Button(self, text="Run")
        self._pause_button = tk.Button(self, text="Pause")
        self._step_button = tk.Button(self, text="Step")
        self._redraw_button = tk.Button(self, text="Re-draw")
        self._exit_button = tk.Button(self, text="Exit")

        # Sliders
        self._max_running_speed = 1000
        self._running_speed = tk.IntVar()
        self._running_speed.set(200)
        self._speed_slider = tk.Scale(
            self, from_=1, to=self._max_running_speed-1)

        # Control Variables
        self._layout_option = tk.StringVar()
        self._debug_option = tk.StringVar()
        self._hide_agents = tk.BooleanVar()

        # Menu Buttons
        self._layout_optionMenu = tk.OptionMenu(
            self,
            self._layout_option,
            *self._graphViz.get_all_layout_methods()
        )
        self._debug_optionMenu = tk.OptionMenu(
            self,
            self._debug_option,
            *self._debug_options
        )

        # Check Buttons
        self._hide_agents_button = tk.Checkbutton(
            self,
            variable = self._hide_agents,
            onvalue=True,
            offvalue=False
        )

        self._config_canvas(canvas_size)
        self._config_buttons(default_debug_option)
        self._arrange()
        self.grid()

        self.draw_graph()
        self.draw_agents()
        self.draw_step_number()

        self.popup = None

        # self._select_debug_option(default_debug_option)
        self._activate_debug_option(default_debug_option)

    # Initialisations

    def _load_debug_options(self):
        path = os.getcwd()
        mas_path = os.path.join(path, "mas")
        visualization_path = os.path.join(mas_path, "visualization")
        file = os.path.join(visualization_path, "debug_modes.json")
        with open(file, "r") as f:
            return json.load(f)

    def _config_canvas(self, canvas_size):
        if canvas_size == GUI.autosize:
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
            size = min(width, height)
            self._graphViz.set_max_x_coordinate(size * 4/5)
            self._graphViz.set_max_y_coordinate(size * 4/5)
        
        else:
            self._graphViz.set_max_x_coordinate(canvas_size)
            self._graphViz.set_max_y_coordinate(canvas_size)

        x, y = self._graphViz.get_max_x_y_coordinate()
        r = self._graphViz.get_vertices_radius()
        p = self._graphViz.get_padding()
        width = x + 2*(r + p)
        height = y + 2*(r + p)
        self._canvas.config(bg="light gray", height=height, width=width)

        self._canvas.bind("<ButtonPress-1>", self._scan_coordinates)
        self._canvas.bind("<B1-Motion>", self._move)
        self._canvas.bind("<MouseWheel>", self._zoom)

    def _config_buttons(self, default_debug_option):
        self._run_button.config(width=10, command=self.start_run_algorithm)
        self._pause_button.config(
            width=10,
            command=self.pause_algorithm,
            state=tk.DISABLED)
        self._step_button.config(width=10, command=self.step_algorithm)
        self._redraw_button.config(width=10, command=self.redraw)
        self._exit_button.config(width=10, command=self.quit)

        self._layout_optionMenu.config(width=10)
        self._layout_option.set(self._graphViz.get_layout_method())

        self._speed_slider.config(
            orient=tk.HORIZONTAL,
            variable=self._running_speed,
            label="running speed",
            showvalue=0
        )

        self._debug_option.trace("w", self.switch_debug_option)
        self._debug_optionMenu.config(width=10)
        self._debug_option.set(default_debug_option)

        self._hide_agents.set(False)
        self._hide_agents_button.config(
            text="hide agents", 
            width=10, 
            command=self._hide_or_display_agents
        )

    def _init_mark_activators(self):
        option = self._debug_option.get()
        self._mark_vertices = self._debug_options[option]["mark_vertices"]
        self._mark_edges = self._debug_options[option]["mark_edges"]

    def _arrange(self):
        self._canvas.grid(row=0, column=0, rowspan=100)
        self._run_button.grid(row=1, column=1)
        self._pause_button.grid(row=2, column=1)
        self._step_button.grid(row=3, column=1)
        self._redraw_button.grid(row=4, column=1)
        self._layout_optionMenu.grid(row=5, column=1)
        self._speed_slider.grid(row=6, column=1)

        self._debug_optionMenu.grid(row=40, column=1)
        self._hide_agents_button.grid(row=41, column=1)

        self._exit_button.grid(row=99, column=1)

    # Canvas Actions

    def _scan_coordinates(self, event):
        self._canvas.scan_mark(event.x, event.y)

    def _move(self, event):
        self._canvas.scan_dragto(event.x, event.y, gain=1)

    def _zoom(self, event):
        if (event.delta > 0):
            self._canvas.scale("all", event.x, event.y, 1.1, 1.1)
        elif (event.delta < 0):
            self._canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._zoomed = True

    # Button Actions

    def redraw(self):
        self.clear_graph()
        self.draw_graph()
        self._debug_redrawing()
        self.draw_agents()

    def step_algorithm(self):
        if self._zoomed:
            self.redraw()
            self._zoomed = False
        self._simulationViz.step_algo()
        self._debug_drawings()
        self.clear_agents()
        self.draw_agents()
        self.clear_step_number()
        self.draw_step_number()

    def start_run_algorithm(self):
        if self._pause:
            self._pause = False
            self._pause_button.config(state=tk.NORMAL)
            self._run_button.config(state=tk.DISABLED)
            self.run_algorithm()

    def run_algorithm(self):
        if not self._pause:
            self.step_algorithm()
            self.after(1000 - self._running_speed.get(), self.run_algorithm)

    def pause_algorithm(self):
        if not self._pause:
            self._pause = True
            self._pause_button.config(state=tk.DISABLED)
            self._run_button.config(state=tk.NORMAL)

    # Control Variable Callbacks

    # def switch_debug_option(self, *args):
    #     option = self._debug_option.get()
    #     self._canvas.delete("_debug_option_text")
    #     self._select_debug_option(option)

    def switch_debug_option(self, *args):
        option = self._debug_option.get()
        self._canvas.delete("_debug_option_text")
        self._activate_debug_option(option)    

    # def _select_debug_option(self, option):
    #     if option == "Normal":
    #         self._activate_normal_mode()
    #     elif option == "Vertex_visualization":
    #         self._activate_vertex_visualization_mode()
    #     elif option == "Full_visualization":
    #         self._activate_full_visualization_mode()
    #     elif option == "Simple_debug":
    #         self._activate_simple_debug_mode()
    #     elif option == "Exploration_debug":
    #         self._activate_exploration_debug_mode()
    #     elif option == "Cartography_debug":
    #         self._activate_cartography_debug_mode()

    # Popups

    def _popup_message(self, title, message):
        if self.popup is not None:
            self.popup.destroy()

        self.popup = Toplevel(self.master)
        self.popup.geometry("250x250")
        self.popup.title(title)

        text = tk.Text(self.popup)
        text.insert(tk.END, message)
        text.config(state=DISABLED)
        text.pack()

        exit_button = tk.Button(self.popup, text="Close", width=10,
                                command=self.popup.destroy)
        exit_button.pack(side=tk.BOTTOM)

    # Drawings

    def draw_agents(self):
        if not self._hide_agents.get():
            self._simulationViz.draw_all_agents(self._canvas)

    def draw_graph(self):
        self._graphViz.set_layout_method(self._layout_option.get())
        self._graphViz.draw(self._canvas)

    def draw_step_number(self):
        self._simulationViz.draw_step_number(self._canvas)

    def clear_agents(self):
        self._canvas.delete("agents")

    def clear_graph(self):
        self._canvas.delete("vertices")
        self._canvas.delete("edges")
        self._canvas.delete("agents")
        self._canvas.delete("vertex_marks")

    def clear_step_number(self):
        self._canvas.delete("step_text")

    def clear_debug_drawings(self):
        self._canvas.delete("vertex_marks")
        self._canvas.delete("edge_marks")

    # def _debug_drawings(self):
    #     option = self._debug_option.get()
    #     if option not in ["Normal", "Simple_debug"]:
    #         self._simulationViz.remove_occupied_position_marks(self._canvas)
    #         self._simulationViz.mark_every_agent_position(self._canvas)
    #     if option in ["Full_visualization", "Cartography_debug"]:
    #         self._simulationViz.remove_just_traversed_edge_marks(self._canvas)
    #         self._simulationViz.mark_every_edge(self._canvas)

    def _debug_drawings(self):
        option = self._debug_option.get()
        if self._debug_options[option]["mark_vertices"]:
            self._simulationViz.remove_occupied_position_marks(self._canvas)
            self._simulationViz.mark_every_agent_position(self._canvas)
        if self._debug_options[option]["mark_edges"]:
            self._simulationViz.remove_just_traversed_edge_marks(self._canvas)
            self._simulationViz.mark_every_edge(self._canvas)

    # def _debug_redrawing(self):
    #     self.clear_debug_drawings()
    #     option = self._debug_option.get()

    #     if option in ["Normal", "Simple_debug"]:
    #         return

    #     self._simulationViz.mark_every_visited_position(self._canvas)
    #     if option in ["Cartography_debug", "Full_visualization"]:
    #         self._simulationViz.mark_every_visited_edge(self._canvas)

    def _debug_redrawing(self):
        self.clear_debug_drawings()
        option = self._debug_option.get()

        if self._debug_options[option]["mark_vertices"]:
            self._simulationViz.mark_every_visited_position(self._canvas)
        if self._debug_options[option]["mark_edges"]:
            self._simulationViz.mark_every_visited_edge(self._canvas)

    def _display_debug_option(self, option, color):
        self._canvas.delete("_debug_option_text")
        self._canvas.create_text(
            self._canvas.winfo_width() - 10,
            10,
            anchor="ne",
            font=tkFont.Font(size=15, weight='bold', slant="italic"),
            fill=color,
            text=option,
            tags=["text", "_debug_option_text"]
        )

    # Miscellanous

    def _activate_debug_option(self, option):
        self.redraw()
        verbose = self._debug_options[option]["verbose"]
        name = self._debug_options[option]["name"]

        if self._debug_options[option]["display_name"]:
            color = self._debug_options[option]["displaying_color"]
            self._display_debug_option(name, color)
        self._simulationViz.set_verbose(verbose)

        if self._debug_options[option]["activate_clicking"]:
            self._activate_element_clicking()
        else:
            self._deactivate_element_clicking()

    # def _activate_normal_mode(self):
    #     self.redraw()
    #     self._simulationViz.set_verbose(False)
    #     self._deactivate_element_clicking()

    # def _activate_vertex_visualization_mode(self):
    #     self.redraw()
    #     self._simulationViz.set_verbose(False)
    #     self._display_debug_option("Vertex_visualization", "blue")
    #     self._deactivate_element_clicking()

    # def _activate_full_visualization_mode(self):
    #     self.redraw()
    #     self._simulationViz.set_verbose(False)
    #     self._display_debug_option("Full_visualization", "blue")
    #     self._deactivate_element_clicking()

    # def _activate_simple_debug_mode(self):
    #     self.redraw()
    #     self._simulationViz.set_verbose(True)
    #     self._display_debug_option("Simple_debug", "red")
    #     self._activate_element_clicking()

    # def _activate_exploration_debug_mode(self):
    #     self.redraw()
    #     self._simulationViz.set_verbose(True)
    #     self._display_debug_option("Exploration_debug", "red")
    #     self._activate_element_clicking()

    # def _activate_cartography_debug_mode(self):
    #     self.redraw()
    #     self._simulationViz.set_verbose(True)
    #     self._display_debug_option("Cartography_debug", "red")
    #     self._activate_element_clicking()

    def _activate_element_clicking(self):
        self._canvas.tag_bind("agents", '<Button-1>', self._click_element)
        self._canvas.tag_bind("vertices", '<Button-1>', self._click_element)
        self._canvas.tag_bind("agents", "<Enter>", self._hover_element)
        self._canvas.tag_bind("vertices", "<Enter>", self._hover_element)
        self._canvas.tag_bind("agents", "<Leave>", self._unhover_element)
        self._canvas.tag_bind("vertices", "<Leave>", self._unhover_element)

    def _click_element(self, event):
        obj_id = self._canvas.find_closest(event.x, event.y)
        all_tags = self._canvas.itemcget(obj_id, "tags")

        if "agents" in all_tags:
            tag = self._extract_unique_tag_from_obj_id(obj_id, "agent")
            agent = self._simulationViz.get_agent_by_tag(tag)
            message = self._simulationViz.get_agent_information(agent)
        
        elif "vertices" in all_tags:
            tag = self._extract_unique_tag_from_obj_id(obj_id, "vertex")
            agent = self._graphViz.get_vertex_by_tag(tag)
            message = self._simulationViz.get_vertex_information(agent)
        self._popup_message(tag, message)

    def _deactivate_element_clicking(self):
        self._canvas.tag_unbind("agents", '<Button-1>')
        self._canvas.tag_unbind("vertices", '<Button-1>')
        self._canvas.tag_unbind("agents", "<Enter>")
        self._canvas.tag_unbind("vertices", "<Enter>")
        self._canvas.tag_unbind("agents", "<Leave>")
        self._canvas.tag_unbind("vertices", "<Leave>")        

    def _extract_unique_tag_from_obj_id(self, obj_id, group_tag):
        # obj_id should be the identifier of a canvas element having tag
        # *group_tag*

        # all the tags of canvas object separated by spaces
        all_tags = self._canvas.itemcget(obj_id, "tags")
        for tag in all_tags.split(" "):
            pattern = f"^{group_tag}[0-9]+$"
            if re.match(rf"{pattern}", tag) is not None:
                return tag

    def _hide_or_display_agents(self):
        if not self._hide_agents.get():
            self.draw_agents()
        else:
            self.clear_agents()

    def _hover_element(self, event):
        obj_id = self._canvas.find_closest(event.x, event.y)
        if     "agent_texts" in self._canvas.gettags(obj_id):
            obj_id = self._canvas.find_below(obj_id)

        if "agent_graphics" in self._canvas.gettags(obj_id):
            tag = self._extract_unique_tag_from_obj_id(obj_id, "agent")
            agent = self._simulationViz.get_agent_by_tag(tag)
            _, _, color = self._simulationViz.get_agent_color(agent)
            width = 2*self._simulationViz.get_agents_border_thickness()
            self._canvas.itemconfig(obj_id, {"outline": color, "width": width})

        elif "vertices" in self._canvas.gettags(obj_id):
            tag = self._extract_unique_tag_from_obj_id(obj_id, "vertex")
            width = self._graphViz.get_vertices_border_thickness()
            self._canvas.itemconfig(obj_id, {"outline": "cyan", "width": width})

    def _unhover_element(self, event):
        obj_id = self._canvas.find_closest(event.x, event.y, halo=10)
        if     "agent_texts" in self._canvas.gettags(obj_id):
            obj_id = self._canvas.find_below(obj_id)

        if "agent_graphics" in self._canvas.gettags(obj_id):
            tag = self._extract_unique_tag_from_obj_id(obj_id,"agent")
            agent = self._simulationViz.get_agent_by_tag(tag)
            _, color, _ = self._simulationViz.get_agent_color(agent)
            width = self._simulationViz.get_agents_border_thickness()
            self._canvas.itemconfig(obj_id, {"outline": color, "width": width})

        elif "vertices" in self._canvas.gettags(obj_id):
            tag = self._extract_unique_tag_from_obj_id(obj_id, "vertex")
            width = self._graphViz.get_vertices_border_thickness()
            color = self._graphViz.get_vertices_border_color()
            self._canvas.itemconfig(obj_id, {"outline": color, "width": width})


def start(simulation):
    """
        Starts the Graphical User Interface (GUI).

        :param simulation: the simulation to execute and display. It contains,
            in particular, the :class:`mas.graph.Graph.Graph` to draw in the
            main _canvas of the GUI.
        :type simulation: :class:`mas.agent.Simulation.Simulation`
    """
    root = tk.Tk()
    app = GUI(root, simulation)
    root.title("Mobile Agents Simulator")
    app.mainloop()
