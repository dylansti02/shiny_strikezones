
from shiny import App, ui, render, reactive, req, Inputs, Outputs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from io import BytesIO
import base64
from helpers import get_league_average, pitch_family_map
from heatmaps import statcast_heatmap 


app_ui = ui.page_fluid(
    ui.h2("Statcast Heatmap Viewer"),

    ui.input_text("player", "Player Name", placeholder="e.g., Shohei Ohtani"),
    ui.input_date("start_date", "Start Date", value="2023-04-01"),
    ui.input_date("end_date", "End Date"),
    ui.input_select("pitch_type", "Pitch Type", 
                    choices=["", "Fastball", "Breaking", "Offspeed"],
                    selected=""),
    ui.input_select("p_throws", "Pitcher Throws", 
                    choices=["", "L", "R"],
                    selected=""),
    ui.input_action_button("generate", "Generate Heatmaps"),

    ui.output_ui("plot_ui")
)

def server(input, output, session):

    @reactive.event(input.generate)
    def generate_heatmap():
        player = input.player()
        start_dt = str(input.start_date())
        end_dt = str(input.end_date()) if input.end_date() else None
        pitch_type = input.pitch_type() or None
        p_throws = input.p_throws() or None

        if not player:
            raise ValueError("Player name is required.")

        # Generate the plot using your function
        fig = statcast_heatmap(
            player=player,
            start_dt=start_dt,
            end_dt=end_dt,
            pitch_type=pitch_type,
            p_throws=p_throws
        )

        return fig

    @output
    @render.ui
    def plot_ui():
        try:
            fig = generate_heatmap()
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            buf.close()
            return ui.tags.img(src=f"data:image/png;base64,{encoded}", style="max-width:100%;")
        except Exception as e:
            return ui.tags.div({"style": "color: red;"}, f"Error: {str(e)}")


app = App(app_ui, server)
