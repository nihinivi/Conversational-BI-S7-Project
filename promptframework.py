
from base64 import b64encode 
import os 
import io
import pandas as pd
import numpy as np
import json
from PIL import Image
import boto3
import base64
from visualization_framework import (
    create_bar_chart,
    create_line_chart,
    create_pie_chart,
    create_scatter_plot,
    create_histogram,
    create_heatmap,
    create_bubble_chart,
    create_donut_chart,
    create_radar_chart,
    create_map_chart
)

lambda_client = boto3.client('lambda', region_name=os.getenv("REGION"),
                            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                            aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"))

def send_prompt(prompt_text: str) -> str:
    """Send prompt to GPT Lambda and return raw output."""
    payload = {"body": json.dumps({"prompt": prompt_text})}  
    response = lambda_client.invoke(
        FunctionName='gpt4olambda',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    result = json.loads(response['Payload'].read()) 
    return json.loads(result.get('body', '{}')).get('output', '')


def generate_visualization_schema(schema: dict, user_query: str) -> dict:
    """
    Sends schema + user query to GPT and receives a JSON schema
    describing which chart to create and which columns to use.
    """
    system_prompt = """
    You are a data visualization assistant.
    You will be given a table schema and a user query.
    Return a JSON object (no markdown) describing the best chart to generate.

    JSON format must be like one of the following:
    {
      "chart_type": "<chart type>",
      "x": "<column_name>",
      "y": "<column_name>",
      "title": "<chart title>",
      "xlabel": "<x label>",
      "ylabel": "<y label>"
    }

    OR 

    {
  "chart_type": "pie",
  "labels": "<column_name>",
  "values": "<column_value>",
  "title": "<chart title>"
  }

  OR
  {
  "chart_type": "histogram",
  "x": "<column_name>",
  "title": "<chart title>",
  "xlabel": "<x label>",
}

    Only return valid JSON.
    """

    user_prompt = f"""
    The user asked: "{user_query}"
    The table schema is:
    {json.dumps(schema, indent=2)}
    """

    prompt = system_prompt + "\n" + user_prompt
    response = send_prompt(prompt)
 
    try:
        viz_schema = json.loads(response)
        return viz_schema
    except json.JSONDecodeError:
        print("⚠️ Failed to parse GPT output as JSON:", response)
        return {}
    

def generate_visualization_from_schema(df: pd.DataFrame, viz_schema: dict) -> Image.Image:
    """
    Takes the visualization schema (from GPT) and creates the appropriate chart.
    """
    chart_type = viz_schema.get("chart_type")

    if chart_type == "bar":
        return create_bar_chart(
            categories=df[viz_schema["x"]].tolist(),
            values=df[viz_schema["y"]].tolist(),
            title=viz_schema.get("title", ""),
            xlabel=viz_schema.get("xlabel", viz_schema["x"]),
            ylabel=viz_schema.get("ylabel", viz_schema["y"])
        )

    elif chart_type == "pie":
        return create_pie_chart(
            labels=df[viz_schema["labels"]].tolist(),
            sizes=df[viz_schema["values"]].tolist(),
            title=viz_schema.get("title", "")
        )

    elif chart_type == "line":
        return create_line_chart(
            x_values=df[viz_schema["x"]].tolist(),
            y_values=df[viz_schema["y"]].tolist(),
            title=viz_schema.get("title", ""),
            xlabel=viz_schema.get("xlabel", viz_schema["x"]),
            ylabel=viz_schema.get("ylabel", viz_schema["y"])
        )

    elif chart_type == "scatter":
        return create_scatter_plot(
            x_values=df[viz_schema["x"]].tolist(),
            y_values=df[viz_schema["y"]].tolist(),
            title=viz_schema.get("title", ""),
            xlabel=viz_schema.get("xlabel", viz_schema["x"]),
            ylabel=viz_schema.get("ylabel", viz_schema["y"])
        )

    elif chart_type == "histogram":
        return create_histogram(
            data=df[viz_schema["x"]].tolist(),
            title=viz_schema.get("title", ""),
            xlabel=viz_schema.get("xlabel", viz_schema["x"])
        )

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")




def generate_visualization(df: pd.DataFrame, schema: dict, user_query: str) -> str:
    """
    End-to-end pipeline:
    1. Send schema + query to GPT (via Lambda)
    2. Get visualization JSON schema
    3. Generate and return base64-encoded chart image
    """
    viz_schema = generate_visualization_schema(schema, user_query)
    print("Visualization Schema:\n", viz_schema)
    img = generate_visualization_from_schema(df, viz_schema)
     
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return img_base64
