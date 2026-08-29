# Travelling Salesman Problem Visualiser

An interactive web app that visualises solutions to the Travelling Salesman 
Problem (TSP), built with Python and Streamlit for my A-Level Computer Science NEA.

## What it does
- Choose between randomly generated points or real-world locations
- Real-world mode geocodes place names to actual coordinates using geopy
- Solve the route using either Brute Force or Nearest Neighbour algorithm
- Animated route visualisation on a dark-themed graph
- Interactive map view using PyDeck

## Algorithms
- **Brute Force** — tries every possible route and returns the shortest. Accurate 
  but slow for large inputs.
- **Nearest Neighbour** — greedy algorithm that always visits the closest unvisited 
  node next. Much faster but not always optimal.

## How to run

Install dependencies:
pip install geopy streamlit matplotlib numpy pandas pydeck


Run the app:
python -m streamlit run streamlit123.py


## Note
You will need a free Mapbox token from [mapbox.com](https://mapbox.com).  
Replace `YOUR_MAPBOX_TOKEN_HERE` in the code with your own token to enable the 3D map view.

## Built with
Python · Streamlit · geopy · Matplotlib · NumPy · PyDeck · pandas
