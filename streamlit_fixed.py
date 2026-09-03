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
    geolocator = Nominatim(user_agent="geoapiexercises")
    try:
        location = geolocator.geocode(location_name, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        else:
            st.error(f"Could not find '{location_name}' — try a more specific name.")
            return None
    except Exception as e:
        st.error(f"Geocoding failed for '{location_name}': {e}")
        return None

def get_location_from_user():
    locations = []
    num_locations = st.number_input("enter the n number of locations: ", min_value=2, step=1)
    for i in range(num_locations):
        location_name = st.text_input(f"enter the name of location {i+1}", key=f"location_{i}")
        if location_name:
            coordinates = get_coordinates_from_locations(location_name)
            if coordinates:
                st.success(f"{location_name}: {coordinates}")
                locations.append(coordinates)
    return locations



def calculate_distance(p1, p2):
    """Plain Euclidean distance — correct for the Random Points grid (x, y) mode."""
    return math.sqrt((p2[0] - p1[0])**2+(p2[1] - p1[1])**2)

def haversine_distance(p1, p2):
    """Great-circle distance in km between two (lat, lon) points — for Real-World mode."""
    R = 6371  # Earth's radius in km
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def brute_force_tsp(points, distance_fn=calculate_distance):
    shortest_distance = float('inf')
    shortest_path = None

    for path in itertools.permutations(points):
        distance = 0
        for i in range(len(path) - 1):
            distance = distance + distance_fn(path[i], path[i + 1])
        distance = distance + distance_fn(path[-1], path[0])  # return to the start
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_path = path
    return shortest_path, shortest_distance

def nearest_neighbor_tsp(points, distance_fn=calculate_distance):
    unvisited_nodes = points[:]  # Copy list to avoid modifying original
    start = unvisited_nodes.pop(0)  # Start from the first node
    path = [start]
    total_distance = 0

    while unvisited_nodes:  # Keep running until all nodes are visited
        min_distance = float('inf')
        nearest_node = None

        for node in unvisited_nodes:
            distance = distance_fn(path[-1], node)
            if distance < min_distance:
                min_distance = distance
                nearest_node = node  # Update nearest node

        if nearest_node is not None:
            total_distance += min_distance
            path.append(nearest_node)
            unvisited_nodes.remove(nearest_node)

    # add return leg back to start so distance matches brute force
    total_distance += distance_fn(path[-1], path[0])
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
    # ── keep points fixed until user asks for new ones ──
    key = f"{num_nodes}_{max_x}_{max_y}"
    if "points" not in st.session_state or st.session_state.get("points_key") != key:
        st.session_state.points_key = key
        xs = generate_random_x_points(num_nodes, max_x)
        ys = generate_random_y_points(num_nodes, max_y)
        st.session_state.points = list(zip(xs, ys))

    if st.button("🔀 Generate new random points"):
        xs = generate_random_x_points(num_nodes, max_x)
        ys = generate_random_y_points(num_nodes, max_y)
        st.session_state.points = list(zip(xs, ys))

    points = st.session_state.points
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])

elif choice == "Real-World Locations":
    points = get_location_from_user()

else:
    print("invalid choice")
    exit()




import time

IS_REAL = (choice == "Real-World Locations")

def solve(algo):
    dist_fn = haversine_distance if IS_REAL else calculate_distance
    if algo == "bf":
        path, dist = brute_force_tsp(points, dist_fn)
        start = points[0]
        if start in list(path):
            idx = list(path).index(start)
            path = list(path)[idx:] + list(path)[:idx]
    else:
        path, dist = nearest_neighbor_tsp(points, dist_fn)
    return list(path), dist

def animate_graph(path, dist, label, ph):
    full = path + [path[0]]
    xs = [p[0] for p in full]
    ys = [p[1] for p in full]
    all_xs, all_ys = xs[:-1], ys[:-1]
    STEPS = 3
    done_segs = []
    for seg in range(len(full)-1):
        x1,y1 = xs[seg],ys[seg]
        x2,y2 = xs[seg+1],ys[seg+1]
        for step in range(STEPS+1):
            t = step/STEPS
            dx = x1+t*(x2-x1)
            dy = y1+t*(y2-y1)
            fig,ax = plt.subplots(figsize=(8,6))
            fig.patch.set_facecolor('#0f1117')
            ax.set_facecolor('#0f1117')
            ax.tick_params(colors='#aaaaaa')
            for sp in ax.spines.values(): sp.set_edgecolor('#333333')
            for (ex1,ey1,ex2,ey2) in done_segs:
                ax.plot([ex1,ex2],[ey1,ey2],color='#7A9E87',linewidth=1.8,alpha=0.85)
            ax.plot([x1,dx],[y1,dy],color='#00D4FF',linewidth=2.2,alpha=0.95)
            ax.scatter(all_xs[1:],all_ys[1:],color='#ffffff',s=70,zorder=3,edgecolors='#7A9E87',linewidths=1.2)
            ax.scatter(all_xs[0],all_ys[0],color='#C4622D',s=160,zorder=4,edgecolors='white',linewidths=1.5,label='Start')
            for i in range(len(all_xs)):
                ax.text(all_xs[i],all_ys[i],f' {i+1}',color='#eeeeee',fontsize=9,fontweight='bold',zorder=5)
            ax.scatter([dx],[dy],color='#FFB340',s=220,zorder=6,edgecolors='white',linewidths=1.5,label='Traveller')
            ax.set_title(f'{label}  |  seg {seg+1}/{len(full)-1}',color='white',fontsize=11,pad=10)
            ax.legend(facecolor='#1a1a2e',edgecolor='#333333',labelcolor='white',fontsize=8)
            ph.pyplot(fig)
            plt.close(fig)
            time.sleep(0.005)
        done_segs.append((x1,y1,x2,y2))
    # final static frame
    fig,ax = plt.subplots(figsize=(8,6))
    fig.patch.set_facecolor('#0f1117'); ax.set_facecolor('#0f1117')
    ax.tick_params(colors='#aaaaaa')
    for sp in ax.spines.values(): sp.set_edgecolor('#333333')
    for k in range(len(xs)-1):
        ax.plot([xs[k],xs[k+1]],[ys[k],ys[k+1]],color='#7A9E87',linewidth=1.8,alpha=0.85)
    ax.scatter(all_xs[1:],all_ys[1:],color='#ffffff',s=70,zorder=3,edgecolors='#7A9E87',linewidths=1.2)
    ax.scatter(all_xs[0],all_ys[0],color='#C4622D',s=160,zorder=4,edgecolors='white',linewidths=1.5,label='Start')
    for i in range(len(all_xs)):
        ax.text(all_xs[i],all_ys[i],f' {i+1}',color='#eeeeee',fontsize=9,fontweight='bold',zorder=5)
    ax.set_title(f'{label}  |  Total distance: {dist:.2f}',color='white',fontsize=12,pad=12)
    ax.legend(facecolor='#1a1a2e',edgecolor='#333333',labelcolor='white',fontsize=8)
    ph.pyplot(fig); plt.close(fig)

def show_map(path, dist, label, ph):
    full = path + [path[0]]
    lats = [p[0] for p in full]
    lons = [p[1] for p in full]
    node_df = pd.DataFrame({"lon":[p[1] for p in path],"lat":[p[0] for p in path]})
    cx = sum(p[0] for p in path)/len(path)
    cy = sum(p[1] for p in path)/len(path)

    # auto zoom based on spread of points
    lat_spread = max(lats) - min(lats)
    lon_spread = max(lons) - min(lons)
    spread = max(lat_spread, lon_spread)
    if spread < 0.05:   zoom = 12
    elif spread < 0.5:  zoom = 9
    elif spread < 2:    zoom = 7
    elif spread < 10:   zoom = 5
    elif spread < 40:   zoom = 3
    else:               zoom = 2

    STEPS = 6
    revealed = []
    for seg in range(len(full)-1):
        lat1,lon1 = lats[seg],lons[seg]
        lat2,lon2 = lats[seg+1],lons[seg+1]
        for step in range(STEPS+1):
            t = step/STEPS
            dlat = lat1+t*(lat2-lat1)
            dlon = lon1+t*(lon2-lon1)
            current_seg = [[lon1,lat1],[dlon,dlat]]
            all_segs = revealed + [{"path": current_seg,"color":[0,212,255]}]
            seg_df = pd.DataFrame(all_segs)
            dot_df = pd.DataFrame({"lon":[dlon],"lat":[dlat]})
            deck = pdk.Deck(
                map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                initial_view_state=pdk.ViewState(latitude=cx,longitude=cy,zoom=zoom,pitch=30),
                height=500,
                layers=[
                    pdk.Layer("PathLayer",data=seg_df,get_path="path",
                              get_color="color",width_min_pixels=3,pickable=True),
                    pdk.Layer("ScatterplotLayer",data=node_df,
                              get_position=["lon","lat"],get_color=[196,98,45],
                              get_radius=spread*1500,radius_min_pixels=5,pickable=True),
                    pdk.Layer("ScatterplotLayer",data=dot_df,
                              get_position=["lon","lat"],get_color=[255,179,64],
                              get_radius=spread*2000,radius_min_pixels=7,pickable=True),
                ],
            )
            ph.pydeck_chart(deck)
            time.sleep(0.08)
        revealed.append({"path":[[lon1,lat1],[lon2,lat2]],"color":[122,158,135]})
    # final static map
    final_df = pd.DataFrame([{"path":[[p[1],p[0]] for p in path+[path[0]]],"color":[0,212,255]}])
    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=cx,longitude=cy,zoom=zoom,pitch=30),
        height=500,
        layers=[
            pdk.Layer("PathLayer",data=final_df,get_path="path",
                      get_color="color",width_min_pixels=3,pickable=True),
            pdk.Layer("ScatterplotLayer",data=node_df,
                      get_position=["lon","lat"],get_color=[196,98,45],
                      get_radius=spread*1500,radius_min_pixels=5,pickable=True),
        ],
    )
    ph.pydeck_chart(deck)
    st.caption(f"{label}  |  Total distance: {dist:.2f} km")

def draw_static_map(path, dist, label, ph):
    """Non-animated version of show_map — draws the final route once, no per-frame replay."""
    lats = [p[0] for p in path]
    lons = [p[1] for p in path]
    node_df = pd.DataFrame({"lon": [p[1] for p in path], "lat": [p[0] for p in path]})
    cx = sum(p[0] for p in path) / len(path)
    cy = sum(p[1] for p in path) / len(path)

    lat_spread = max(lats) - min(lats)
    lon_spread = max(lons) - min(lons)
    spread = max(lat_spread, lon_spread)
    if spread < 0.05:   zoom = 12
    elif spread < 0.5:  zoom = 9
    elif spread < 2:    zoom = 7
    elif spread < 10:   zoom = 5
    elif spread < 40:   zoom = 3
    else:               zoom = 2

    final_df = pd.DataFrame([{"path": [[p[1], p[0]] for p in path + [path[0]]], "color": [0, 212, 255]}])
    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=cx, longitude=cy, zoom=zoom, pitch=30),
        height=500,
        layers=[
            pdk.Layer("PathLayer", data=final_df, get_path="path",
                      get_color="color", width_min_pixels=3, pickable=True),
            pdk.Layer("ScatterplotLayer", data=node_df,
                      get_position=["lon", "lat"], get_color=[196, 98, 45],
                      get_radius=spread * 1500, radius_min_pixels=5, pickable=True),
        ],
    )
    ph.pydeck_chart(deck)
    st.caption(f"{label}  |  Total distance: {dist:.2f} km")

def draw_static(path, dist, label, ph):
    full = path+[path[0]]
    xs=[q[0] for q in full]; ys=[q[1] for q in full]
    fig,ax=plt.subplots(figsize=(8,6))
    fig.patch.set_facecolor('#0f1117'); ax.set_facecolor('#0f1117')
    ax.tick_params(colors='#aaaaaa')
    for sp in ax.spines.values(): sp.set_edgecolor('#333333')
    for k in range(len(xs)-1): ax.plot([xs[k],xs[k+1]],[ys[k],ys[k+1]],color='#7A9E87',linewidth=1.8)
    ax.scatter(xs[:-1][1:],ys[:-1][1:],color='#ffffff',s=70,zorder=3,edgecolors='#7A9E87',linewidths=1.2)
    ax.scatter(xs[0],ys[0],color='#C4622D',s=160,zorder=4,edgecolors='white',linewidths=1.5)
    ax.set_title(f'{label}  |  Total distance: {dist:.2f}',color='white',fontsize=12,pad=12)
    ph.pyplot(fig); plt.close(fig)

# session state for persistent results
for k in ["bf_path","nn_path","bf_ran","nn_ran"]:
    if k not in st.session_state: st.session_state[k] = None

# ── if the current locations/points don't match what was last solved,
#    clear old results so nothing renders (or re-animates) until Run is clicked ──
if st.session_state.get("last_points") != points:
    st.session_state.bf_path = None
    st.session_state.nn_path = None
    st.session_state.bf_ran = False
    st.session_state.nn_ran = False
    st.session_state.last_points = points

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("▶ Run Brute Force", use_container_width=True):
        p,d = solve("bf")
        st.session_state.bf_path = (p,d)
        st.session_state.bf_ran = True
with col2:
    if st.button("▶ Run Nearest Neighbour", use_container_width=True):
        p,d = solve("nn")
        st.session_state.nn_path = (p,d)
        st.session_state.nn_ran = True

def render(path, dist, label, ph, is_animate):
    if IS_REAL:
        if is_animate: show_map(path,dist,label,ph)
        else: draw_static_map(path,dist,label,ph)
    else:
        if is_animate: animate_graph(path,dist,label,ph)
        else: draw_static(path,dist,label,ph)

if IS_REAL:
    # real-world: stacked full width
    if st.session_state.bf_path:
        p,d = st.session_state.bf_path
        st.subheader("Brute Force")
        ph = st.empty()
        was_ran = bool(st.session_state.bf_ran)
        if was_ran: st.session_state.bf_ran = False
        render(p,d,"Brute Force",ph,was_ran)

    if st.session_state.nn_path:
        p,d = st.session_state.nn_path
        st.subheader("Nearest Neighbour")
        ph2 = st.empty()
        was_ran = bool(st.session_state.nn_ran)
        if was_ran: st.session_state.nn_ran = False
        render(p,d,"Nearest Neighbour",ph2,was_ran)

else:
    # random points: side by side
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        if st.session_state.bf_path:
            p,d = st.session_state.bf_path
            st.subheader("Brute Force")
            ph = st.empty()
            was_ran = bool(st.session_state.bf_ran)
            if was_ran: st.session_state.bf_ran = False
            render(p,d,"Brute Force",ph,was_ran)
    with res_col2:
        if st.session_state.nn_path:
            p,d = st.session_state.nn_path
            st.subheader("Nearest Neighbour")
            ph2 = st.empty()
            was_ran = bool(st.session_state.nn_ran)
            if was_ran: st.session_state.nn_ran = False
            render(p,d,"Nearest Neighbour",ph2,was_ran)

