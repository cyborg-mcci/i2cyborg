import plotly.graph_objects as go
import numpy as np
import math

x = np.linspace(start=0, stop=120, num=2000)
y = np.fabs(np.sqrt(np.sin(x)))


fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name=r'$sqrt{2}$ testplot'))
fig.title(r'$sqrt{2}$ testplot')
fig.show()