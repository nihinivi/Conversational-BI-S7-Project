import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import geopandas as gpd
from PIL import Image
import io
 

def create_bar_chart(categories: list, values: list, title="Bar Chart", xlabel="Categories", ylabel="Values") -> Image.Image:
    """ 
        categories (list): A list of strings for the x-axis categories.
        values (list): A list of numerical values for the y-axis.
        title (str): The title of the chart.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis. 
    """
    plt.figure(figsize=(10, 6))
    sns.barplot(x=categories, y=values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()  
    return img

def create_line_chart(x_values: list, y_values: list, title="Line Chart", xlabel="Time", ylabel="Value") -> Image.Image:
    """ 
        x_values (list): A list of values for the x-axis (e.g., dates, numbers).
        y_values (list): A list of numerical values for the y-axis.
        title (str): The title of the chart.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis. 
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img

def create_pie_chart(labels: list, sizes: list, title="Pie Chart") -> Image.Image:
    """ 
        labels (list): A list of strings for each wedge's label.
        sizes (list): A list of numerical values representing the size of each wedge.
        title (str): The title of the chart. 
    """
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    plt.axis('equal')   
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img

def create_scatter_plot(x_values: list, y_values: list, title="Scatter Plot", xlabel="X-Variable", ylabel="Y-Variable") -> Image.Image:
    """ 
        x_values (list): A list of numerical values for the x-axis.
        y_values (list): A list of numerical values for the y-axis.
        title (str): The title of the chart.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis. 
    """
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=x_values, y=y_values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img
    
def create_histogram(data: list, title="Histogram", xlabel="Value", bins=10) -> Image.Image:
    """ 
        data (list): A list of numerical data.
        title (str): The title of the chart.
        xlabel (str): The label for the x-axis.
        bins (int): The number of bins for the histogram.
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=bins, kde=True)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img
    
def create_radar_chart(categories: list, values: list, label: str, title="Radar Chart") -> Image.Image:
    """ 
        categories (list): List of category strings.
        values (list): List of numerical values for each category.
        label (str): The label for the data series.
        title (str): The title of the chart. 
    """
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=label
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.1]
            )),
        showlegend=True,
        title=title
    )
    
    # Save to bytes and then open with PIL
    img_bytes = fig.to_image(format="png")
    return Image.open(io.BytesIO(img_bytes))

def create_map_chart(column_to_plot: str, title="Geospatial Map") -> Image.Image:
    """ 
        column_to_plot (str): The name of the column to visualize on the map (e.g., 'pop_est', 'gdp_md_est').
        title (str): The title for the map. 
    """ 
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.plot(column=column_to_plot, ax=ax, legend=True,
               legend_kwds={'label': f"{column_to_plot} by Country", 'orientation': "horizontal"})
    ax.set_title(title, fontdict={'fontsize': '16', 'fontweight': '3'})
    ax.set_axis_off()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img
    
def create_heatmap(data: pd.DataFrame, title="Heatmap") -> Image.Image:
    """
        data (pd.DataFrame): A 2D DataFrame where rows and columns are labels and values are numerical.
        title (str): The title of the chart. 
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, annot=True, cmap="coolwarm", fmt=".1f")
    plt.title(title)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img

def create_bubble_chart(x_values: list, y_values: list, bubble_sizes: list, title="Bubble Chart", xlabel="X-Variable", ylabel="Y-Variable") -> Image.Image:
    """
        x_values (list): List of numerical values for the x-axis.
        y_values (list): List of numerical values for the y-axis.
        bubble_sizes (list): List of numerical values determining the size of each bubble.
        title (str): The title of the chart.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis. 
    """
    plt.figure(figsize=(12, 7))
    sns.scatterplot(x=x_values, y=y_values, size=bubble_sizes, sizes=(50, 2000), alpha=0.7, legend='auto')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img

def create_donut_chart(labels: list, sizes: list, title="Donut Chart") -> Image.Image:
    """
        labels (list): A list of strings for each section's label.
        sizes (list): A list of numerical values representing the size of each section.
        title (str): The title of the chart.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3))
    ax.set_title(title)
    ax.axis('equal')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img