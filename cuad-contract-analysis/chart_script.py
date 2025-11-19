
import plotly.graph_objects as go

# Create figure
fig = go.Figure()

# Define node positions (x, y)
positions = {
    'START': (0.5, 13),
    'Load': (0.5, 12),
    'Loop': (0.5, 11),
    'Extract': (0.5, 10),
    'Normalize': (0.5, 9),
    'Term': (0.5, 8),
    'Conf': (0.5, 7),
    'Liab': (0.5, 6),
    'Summary': (0.5, 5),
    'Save': (0.5, 4),
    'Export': (0.5, 3),
    'Index': (0.5, 2),
    'END': (0.5, 1)
}

# Add rectangles for process nodes
processes = [
    ('Load', 'Load 50 Contracts'),
    ('Extract', 'Extract PDF Text'),
    ('Normalize', 'Normalize Text'),
    ('Term', 'Extract Term Clause'),
    ('Conf', 'Extract Conf Clause'),
    ('Liab', 'Extract Liab Clause'),
    ('Summary', 'Generate Summary'),
    ('Save', 'Save Results'),
    ('Export', 'Export CSV/JSON'),
    ('Index', 'Build Search Index')
]

for node, label in processes:
    x, y = positions[node]
    # Rectangle
    fig.add_shape(type="rect", x0=x-0.25, y0=y-0.3, x1=x+0.25, y1=y+0.3,
                  line=dict(color="#21808d", width=2), fillcolor="#e8f4f5")
    fig.add_annotation(x=x, y=y, text=label, showarrow=False, 
                      font=dict(size=11, color="#13343b"))

# Add rounded rectangles for start/end
for node in ['START', 'END']:
    x, y = positions[node]
    fig.add_shape(type="rect", x0=x-0.2, y0=y-0.25, x1=x+0.2, y1=y+0.25,
                  line=dict(color="#21808d", width=2), fillcolor="#e8f4f5",
                  layer='below')
    fig.add_annotation(x=x, y=y, text=node, showarrow=False,
                      font=dict(size=12, color="#13343b", family="Arial Black"))

# Add diamond for decision
x, y = positions['Loop']
diamond_x = [x, x+0.25, x, x-0.25, x]
diamond_y = [y+0.3, y, y-0.3, y, y+0.3]
fig.add_trace(go.Scatter(x=diamond_x, y=diamond_y, fill="toself",
                        fillcolor="#e8f4f5", line=dict(color="#21808d", width=2),
                        mode='lines', showlegend=False, hoverinfo='skip'))
fig.add_annotation(x=x, y=y, text="For Each<br>Contract?", showarrow=False,
                  font=dict(size=10, color="#13343b"))

# Add arrows
arrows = [
    ('START', 'Load'),
    ('Load', 'Loop'),
    ('Extract', 'Normalize'),
    ('Normalize', 'Term'),
    ('Term', 'Conf'),
    ('Conf', 'Liab'),
    ('Liab', 'Summary'),
    ('Summary', 'Save'),
    ('Export', 'Index'),
    ('Index', 'END')
]

for start, end in arrows:
    x0, y0 = positions[start]
    x1, y1 = positions[end]
    fig.add_annotation(x=x1, y=y1+0.3, ax=x0, ay=y0-0.3,
                      xref='x', yref='y', axref='x', ayref='y',
                      showarrow=True, arrowhead=2, arrowsize=1,
                      arrowwidth=2, arrowcolor="#333333")

# Loop to Extract (Yes)
fig.add_annotation(x=0.5, y=10.3, ax=0.5, ay=10.7,
                  xref='x', yref='y', axref='x', ayref='y',
                  showarrow=True, arrowhead=2, arrowsize=1,
                  arrowwidth=2, arrowcolor="#333333")
fig.add_annotation(x=0.35, y=10.5, text="Yes", showarrow=False,
                  font=dict(size=9, color="#21808d"))

# Save back to Loop (curved)
fig.add_shape(type="path",
              path=f"M 0.5,3.7 L 0.8,3.7 L 0.8,11 L 0.75,11",
              line=dict(color="#333333", width=2))
fig.add_annotation(x=0.75, y=11, ax=0.75, ay=11,
                  xref='x', yref='y', axref='x', ayref='y',
                  showarrow=True, arrowhead=2, arrowsize=1,
                  arrowwidth=2, arrowcolor="#333333")

# Loop to Export (No)
fig.add_annotation(x=0.5, y=3.3, ax=0.5, ay=10.7,
                  xref='x', yref='y', axref='x', ayref='y',
                  showarrow=True, arrowhead=2, arrowsize=1,
                  arrowwidth=2, arrowcolor="#333333")
fig.add_annotation(x=0.35, y=7, text="No", showarrow=False,
                  font=dict(size=9, color="#21808d"))

# Update layout
fig.update_xaxes(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False)
fig.update_yaxes(range=[0, 14], showgrid=False, showticklabels=False, zeroline=False)
fig.update_layout(
    title="CUAD Contract Pipeline",
    plot_bgcolor='#f3f3ee',
    paper_bgcolor='#f3f3ee'
)

# Save the figure
fig.write_image('cuad_pipeline.png')
fig.write_image('cuad_pipeline.svg', format='svg')
