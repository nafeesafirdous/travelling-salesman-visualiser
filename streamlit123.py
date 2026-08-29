from geopy.geocoders import Nominatim
import random
import matplotlib.pyplot as plt
import numpy as np
import math
import itertools
import streamlit as st
import pandas as pd
import pydeck as pdk


def generate_random_x_points(num_nodes, max_x):  #, max_y):
     return[random.randint(0, max_x) for _ in range(num_nodes)] #random.randint(0, max_y))
   
    
def generate_random_y_points(num_nodes, max_y):  #, max_y):
     return[random.randint(0, max_y) for _ in range(num_nodes)]

def get_coordinates_from_locations(location_name):                        
    geolocator= Nominatim(user_agent= "geoapiexercises")
    location = geolocator.geocode(location_name)
    return (location.latitude, location.longitude)

def get_location_from_user():
    locations = []
    num_locations = st.number_input("enter the n number of locations: ",  min_value=1, step=1)
    for i in range (num_locations):
        location_name = st.text_input(f"enter the name of location {i+1}", key=f"location_{i}")
        coordinates = get_coordinates_from_locations(location_name)
        if coordinates:
            st.success(f"{location_name}:{coordinates}")
            locations.append(coordinates)
        else:
            st.error("error")
    return locations



def calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2+(p2[1] - p1[1])**2)

def brute_force_tsp(points):
    shortest_distance = float('inf')
    shortest_path = None

    for path in itertools.permutations(points):
        distance = 0
        for i in range(len(path) - 1):
            distance = distance + calculate_distance(path[i], path[i + 1])
        distance = distance + calculate_distance(path[-1], path[0])  # return to the start
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_path = path
    return shortest_path, shortest_distance

def nearest_neighbor_tsp(points):
    unvisited_nodes = points[:]  # Copy list to avoid modifying original
    start = unvisited_nodes.pop(0)  # Start from the first node
    path = [start]
    total_distance = 0

    while unvisited_nodes:  # Keep running until all nodes are visited
        min_distance = float('inf')
        nearest_node = None

        for node in unvisited_nodes:
            distance = calculate_distance(path[-1], node)
            if distance < min_distance:
                min_distance = distance
                nearest_node = node  # Update nearest node

        # ✅ Check if nearest_node is None before removing
        if nearest_node is not None: #and nearest_node in unvisited_nodes:
            total_distance += min_distance
            path.append(nearest_node)
            unvisited_nodes.remove(nearest_node) 
    return path, total_distance
   
      

def plot_path(path, total_distance, points):
    x_coords = [p[0] for p in path]
    y_coords = [p[1] for p in path]

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#0f1117')
    ax.tick_params(colors='#aaaaaa')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')

    for j in range(len(x_coords) - 1):
        ax.plot([x_coords[j], x_coords[j+1]], [y_coords[j], y_coords[j+1]],
                color='#7A9E87', linewidth=1.8, alpha=0.85, zorder=1)
    ax.plot([x_coords[-1], x_coords[0]], [y_coords[-1], y_coords[0]],
            color='#7A9E87', linewidth=1.8, alpha=0.5, linestyle='--', zorder=1)

    ax.scatter(x_coords[1:-1], y_coords[1:-1],
               color='#ffffff', s=80, zorder=3, edgecolors='#7A9E87', linewidths=1.5)
    ax.scatter(x_coords[0], y_coords[0], color='#C4622D', s=180,
               zorder=4, edgecolors='white', linewidths=1.5, label='Start')
    ax.scatter(x_coords[-1], y_coords[-1], color='#5b9bd5', s=180,
               zorder=4, edgecolors='white', linewidths=1.5, label='End')

    for i in range(len(x_coords)):
        ax.text(x_coords[i] + 0.5, y_coords[i] + 0.5, str(i + 1),
                color='#eeeeee', fontsize=9, fontweight='bold', zorder=5)

    ax.set_title(f"Total Distance: {total_distance:.2f}", color='white', fontsize=12, pad=12)
    ax.legend(facecolor='#1a1a2e', edgecolor='#333333', labelcolor='white', fontsize=9)
    st.pyplot(fig)
    plt.close(fig)

#MAIN PROGRAM STARTS HERE


st.title("The Travelling Salesman Problem Visualizer")
choice = st.radio("Choose what to visualize:", ["Random Points", "Real-World Locations"])


if choice == "Random Points":
    

    num_nodes = int(st.number_input("Enter the number of nodes: ", min_value=1, step=1))
    max_x = int(st.number_input("Enter a maximum x value: ", min_value=1, step=1))
    max_y = int(st.number_input("Enter a maximum y value: ", min_value=1, step=1))
    coordinates_of_random_x_points = generate_random_x_points(num_nodes, max_x) 
    coordinates_of_random_y_points = generate_random_y_points(num_nodes, max_y) 
    points = list(zip(coordinates_of_random_x_points, coordinates_of_random_y_points))
    x = np.array(coordinates_of_random_x_points)
    y= np.array(coordinates_of_random_y_points)
    plt.scatter(x, y, color='yellow')
    plt.show()
    actual_distance = sum(calculate_distance(points[i], points[i + 1]) for i in range(len(points) - 1))
    actual_distance += calculate_distance(points[-1], points[0])  # Return to start
    print("Actual distance:",actual_distance)
    print("generated points:", points)

elif choice == "Real-World Locations":
    points = get_location_from_user()

else:
    print("invalid choice")
    exit()



algorithm_choice = st.radio("Select a TSP Algorithm:", ["Brute Force", "Nearest Neighbor"])
if algorithm_choice == "Brute Force":
    path, total_distance = brute_force_tsp(points)
    print(f"BRUTE FORCE-- Total Distance: {total_distance} Shortest Path : {path}")
elif algorithm_choice == "Nearest Neighbor":
    path, total_distance = nearest_neighbor_tsp(points)
    print(f"NEAREST NEIGHBOR-- Total Distance: {total_distance} Shortest Path : {path}")

else:
    print("Invalid choice")
    exit()

def path_on_map(path):
    df=pd.DataFrame(path, columns=["latitude","longitude"])
    st.map(df)
    

plot_path(path, total_distance, points)

path_on_map(path)


def plot_with_pydeck(path):
    path_coords = [[point[0], point[1]] for point in path]  # Convert to list of [latitude, longitude]
    chart_data = pd.DataFrame(path, columns=["latitude","longitude"])
    mapbox_token = "YOUR_MAPBOX_TOKEN_HERE"


    deck = pdk.Deck(
        map_style=f"mapbox://styles/mapbox/standard-satellite?access_token={mapbox_token}",
         initial_view_state=pdk.ViewState(
            latitude=path[0][0],  # Initial latitude
            longitude=path[0][1],  # Initial longitude
            zoom=10,
            pitch=50,
        ),

        layers=[pdk.Layer("PathLayer",
                           data = chart_data,
                           get_path = "coordinates",
                           get_color = [255, 0, 0],
                           get_width=10,
                           pickable = True
                           )]

    )
    st.pydeck_chart(deck)
        
plot_with_pydeck(path) 
#st.map(data=plot_path, latitude=None, longitude=None, color=None, size=None, zoom=None, use_container_width=True, width=None, height=None)