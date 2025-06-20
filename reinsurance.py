from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_daq as daq 
from pal import config, XoLTower, distributions
from pal.frequency_severity import FrequencySeverityModel
import numpy as np
import plotly.graph_objs as go
from dash import dash_table

app = Dash(__name__, suppress_callback_exceptions=True)

THEMES = {
    "dark": {
        "background": "#181A1B",
        "card": "#23272E",
        "text": "#F5F6FA",
        "primary": "#859EFF",
        "border": "#444"
    },
    "light": {
        "background": "#F5F6FA",
        "card": "#FFFFFF",
        "text": "#23272E",
        "primary": "#3B4CCA",
        "border": "#CCC"
    }
}

# Store to keep track of which card is full screen
fullscreen_store = dcc.Store(id='home-fullscreen-card', data=None)

def fullscreen_button(card_id):
    return html.Button(
        "⛶",
        id=f"{card_id}-fullscreen-btn",
        n_clicks=0,
        title="Full Screen",
        style={
            'position': 'absolute',
            'top': '14px',
            'right': '18px',
            'zIndex': 2,
            'backgroundColor': '#859EFF',
            'color': '#23272E',
            'border': 'none',
            'borderRadius': '6px',
            'padding': '4px 10px',
            'fontWeight': 'bold',
            'cursor': 'pointer',
            'fontSize': '1.2em',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'
        }
    )

def home_page(theme="dark", fullscreen_card=None):
    colors = THEMES[theme]
    text_color = "#23272E" if theme == "light" else colors["text"]
    primary_color = colors["primary"] if theme == "dark" else "#3B4CCA"
    card_bg = colors["card"]
    bg_color = colors["background"]

    card_ids = ["purpose", "language", "source", "faq"]

    def card_with_button(card_id, children, style):
        return html.Div(
            [
                fullscreen_button(card_id),
                html.Div(children, style={'position': 'relative', 'zIndex': 1})
            ],
            id=f"{card_id}-card",
            style={**style, 'position': style.get('position', 'absolute'), 'transition': 'all 0.3s'}
        )

    return html.Div(
        [
            fullscreen_store,
            html.H1(
                "Home",
                style={
                    'fontWeight': 'bold',
                    'fontSize': '3em',
                    'textAlign': 'center',
                    'marginBottom': '30px',
                    'color': primary_color
                }
            ),
            html.Div(
                [
                    # Top left card: Graphs purpose
                    card_with_button(
                        "purpose",
                        [
                            html.H2("Understanding the purpose of the graphs", style={'color': text_color}),
                            html.P(
                                "The graphs on the main app page help users visualize the expected recoveries (losses of insurance companies covered by reinsurance companies) "
                                "and the effects of different reinsurance parameters as well as the overall distribution of recoveries. "
                                "The many simulations allow not only more precise results "
                                "but also allow reinsurance companies to find the worst case scenario. This lets them prepare accordingly and "
                                "make sure the company doesn't go bankrupt.",
                                style={'color': text_color}
                            ),
                        ],
                        {
                            'width': '46%',
                            'height': '46%',
                            'backgroundColor': card_bg,
                            'borderRadius': '10px',
                            'padding': '30px',
                            'margin': '2%',
                            'boxSizing': 'border-box',
                            'position': 'absolute',
                            'top': '0',
                            'left': '0'
                        }
                    ),
                    # Top right card: Graphs and language
                    card_with_button(
                        "language",
                        [
                            html.H2("What the graphs and language mean", style={'color': text_color}),
                            html.P(
                                "As covered in the understanding the purpose of the graphs section, the graphs are showing the losses "
                                "a reinsurance company may experience. But what do the different terms you can input mean?",
                                style={'color': text_color, 'marginTop': '10px', 'fontSize': '0.83em'}
                            ),
                            html.Ul([
                                html.Li([html.B("Reinsurance: ", style={'color': text_color}), "A contract where an insurance company transfers part of its risk to another insurer (the reinsurer)."]),
                                html.Li([html.B("Limit: ", style={'color': text_color}), "The maximum amount the reinsurer will pay for a single claim or event."]),
                                html.Li([html.B("Policy Limit: ", style={'color': text_color}), "The maximum amount the insurer will pay for all claims under a single insurance policy during the policy period."]),
                                html.Li([html.B("Aggregate Limit: ", style={'color': text_color}), "The maximum amount the reinsurer will pay for all claims in a policy period."]),
                                html.Li([html.B("Excess: ", style={'color': text_color}), "The amount of loss the insurer must pay before the reinsurance coverage starts."]),
                                html.Li([html.B("Aggregate Deductible: ", style={'color': text_color}), "The total amount the insurer must pay before the reinsurer starts paying for claims in a policy period."]),
                                html.Li([html.B("Premium: ", style={'color': text_color}), "The price paid by the insurer to the reinsurer for coverage."]),
                                html.Li([html.B("Mean Frequency: ", style={'color': text_color}), "The average number of claims expected in a year."]),
                                html.Li([html.B("Simulations: ", style={'color': text_color}), "The number of times the model is run to estimate possible outcomes."]),
                                html.Li([html.B("GPD Parameters: ", style={'color': text_color}), "Parameters for the Generalized Pareto Distribution used to model claim sizes. These include: Shape, Scale, and Location. Shape controls the tail of the distribution, Scale controls the spread of the distribution, and Location shifts the distribution along the x-axis."]),
                            ], style={'color': text_color, 'marginTop': '10px', 'fontSize': '0.81em'})
                        ],
                        {
                            'width': '46%',
                            'height': '46%',
                            'backgroundColor': card_bg,
                            'borderRadius': '10px',
                            'padding': '30px',
                            'margin': '2%',
                            'boxSizing': 'border-box',
                            'position': 'absolute',
                            'top': '0',
                            'right': '0'
                        }
                    ),
                    # Bottom left card: Where the graphs have come from
                    card_with_button(
                        "source",
                        [
                            html.H2("Where the graphs have come from", style={'color': text_color, 'fontSize': '1.5em'}),
                            html.P(
                                "The graphs are generated mostly from your inputs for the reinsurance calculator. However, there are some factors that you can't control:",
                                style={'color': text_color, 'marginTop': '10px', 'fontSize': '0.93em'}
                            ),
                            html.Ul([
                                html.Li("The code uses a Generalized Pareto Distribution (GPD) for severity distribution. This controls claim sizes. You can find more information about the GPD on the more info page."),
                                html.Li("The code uses a Poisson distribution for frequency distributions. This controls the number of claims per simulation, affecting how often claims occur. To find out more check the more info page."),
                                html.Li("Random sampling is used so that each simulation draws random values for claim frequency and severity."),
                                html.Li("The reinstatement cost is also within the code of the program. It is the extra amount an insurer must pay to restore reinsurance coverage after it has been used up by a large claim, so that protection is available for future claims."),
                            ], style={'color': text_color, 'marginTop': '10px', 'fontSize': '0.93em'})
                        ],
                        {
                            'width': '46%',
                            'height': '44%',
                            'backgroundColor': card_bg,
                            'borderRadius': '10px',
                            'padding': '30px',
                            'margin': '2%',
                            'boxSizing': 'border-box',
                            'position': 'absolute',
                            'bottom': '0',
                            'left': '0'
                        }
                    ),
                    # Bottom right card: FAQ
                    card_with_button(
                        "faq",
                        [
                            html.H2("FAQ", style={'color': text_color}),
                            dcc.Markdown(
                                """
- **What are the main types of reinsurance contracts?**  
  There are two basic categories: Facultative reinsurance and Treaty reinsurance. To find out more go to the more info page.
- **How does reinsurance impact the stability of the insurance market?**  
  Reinsurance enhances risk capacity and diversification. This ensures that primary insurers maintain financial health and market stability through well-designed contracts.
- **What are common challenges in modeling reinsurance risk?**  
  Lack of reliable models or lack of loss history.
- **How do catastrophic events affect reinsurance recoveries?**  
  They have a significant impact on reinsurance recoveries as they trigger large-scale claims. Also, after major losses, reinsurance premiums often rise due to increased risk perception. To find out more about the biggest insurance claims, check the more info page.
- **How do global events (like climate change or pandemics) influence reinsurance pricing?**  
  They significantly impact reinsurance pricing by increasing risk exposure and uncertainty. Climate change leads to rising frequency and severity of natural disasters which makes prices of premiums increase.
                                """,
                                style={
                                    'color': text_color,
                                    'whiteSpace': 'pre-line',
                                    'fontSize': '0.85em'
                                }
                            ),
                        ],
                        {
                            'width': '46%',
                            'height': '44%',
                            'backgroundColor': card_bg,
                            'borderRadius': '10px',
                            'padding': '30px',
                            'margin': '2%',
                            'boxSizing': 'border-box',
                            'position': 'absolute',
                            'bottom': '0',
                            'right': '0'
                        }
                    ),
                ],
                style={
                    'position': 'relative',
                    'width': '100%',
                    'height': '110vh',
                    'minHeight': '800px'
                }
            ),
        ],
        style={
            'backgroundColor': bg_color,
            'minHeight': '130vh',
            'height': '130vh',
            'margin': 0,
            'padding': 0,
            'boxSizing': 'border-box'
        }
    )

# Tooltip icon helper
def tooltip_icon(id, text):
    return html.Span(
        " ⓘ",
        id=id,
        title=text,
        style={
            'cursor': 'pointer',
            'color': '#859EFF',
            'fontWeight': 'bold',
            'marginLeft': '4px',
            'fontSize': '1em',
            'verticalAlign': 'middle'
        }
    )

# Main app page: user input & graphs
def main_app_page(theme="dark"):
    colors = THEMES[theme]
    loading_color = "#000000" if theme == "light" else "#F5F6FA"
    graph_outline = "#23272E" if theme == "light" else "#FFFFFF"
    responsive_css = dcc.Markdown(
        """
        <style>
        @media (max-width: 900px) {
            .main-flex-row {
                flex-direction: column !important;
            }
            .main-left-col, .main-right-col {
                width: 100% !important;
                min-width: 0 !important;
                margin-bottom: 20px !important;
            }
            .input-columns {
                flex-direction: column !important;
            }
            .input-col {
                width: 100% !important;
                min-width: 0 !important;
                margin-bottom: 20px !important;
            }
        }
        </style>
        """,
        dangerously_allow_html=True
    )
    return html.Div([
        responsive_css,
        html.Div(
            html.H1(
                "Reinsurance Calculator",
                style={
                    'fontWeight': 'bold',
                    'fontSize': '3em',
                    'textAlign': 'center',
                    'color': "#859EFF",
                    'margin': 0,
                    'padding': 0,
                }
            ),
            style={
                'width': '100%',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'marginTop': '30px',
                'marginBottom': '30px',
            }
        ),
        html.Div([
            html.Div([
                html.Div([
                    # Contract parameters column
                    html.Div([
                        html.H3("Contract parameters", style={'color': colors["text"], 'marginBottom': '18px', 'textAlign': 'center'}),
                        html.Div([
                            html.Label([
                                'Limit',
                                tooltip_icon('tooltip-limit', 'The maximum amount the reinsurer will pay for a single claim or event.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-limit',
                                type='number',
                                placeholder='Limit',
                                value=10_000_000,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 10,000,000",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            )
                        ]),
                        html.Div([
                            html.Label([
                                'Aggregate Limit',
                                tooltip_icon('tooltip-aggregate-limit', 'The maximum amount the reinsurer will pay for all claims in a policy period.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-aggregate-limit',
                                type='number',
                                placeholder='Aggregate Limit',
                                value=20_000_000,
                                min=0,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 20,000,000",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            ),
                            html.Div(
                                "(Aggregate limit must be greater than or equal to limit because it is the maximum amount the reinsurer will pay for all claims in a policy period (home page). The limit is the same for one claim).",
                                id='aggregate-limit-warning',
                                style={'color': '#ffb347', 'fontSize': '0.95em', 'marginBottom': '10px', 'display': 'none'}
                            )
                        ]),
                        html.Div([
                            html.Label([
                                'Excess',
                                tooltip_icon('tooltip-excess', 'The amount of loss the insurer must pay before the reinsurance coverage starts.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-excess',
                                type='number',
                                placeholder='Excess',
                                value=1_000_000,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 1,000,000",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            ),
                            html.Div(
                                "(No coverage is given if the excess is higher than the limit as the coverage is from the excess to the limit).",
                                id='limit-excess-warning',
                                style={'color': '#ffb347', 'fontSize': '0.95em', 'marginBottom': '10px', 'display': 'none'}
                            ),
                        ]),
                        html.Div([
                            html.Label([
                                'Aggregate Deductible',
                                tooltip_icon('tooltip-aggregate-deductible', 'The total amount the insurer must pay before the reinsurer starts paying for claims in a policy period.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-aggregate-deductible',
                                type='number',
                                placeholder='Aggregate Deductible',
                                value=2_000_000,
                                min=0,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 2,000,000",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            ),
                            html.Div(
                                "(Aggregate deductible must be greater than the excess as it is for a year rather than just one claim).",
                                id='aggregate-deductible-warning',
                                style={'color': '#ffb347', 'fontSize': '0.95em', 'marginBottom': '10px', 'display': 'none'}
                            )
                        ]),
                        html.Div([
                            html.Label([
                                'Premium',
                                tooltip_icon('tooltip-premium', 'The price paid by the insurer to the reinsurer for coverage.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-premium',
                                type='number',
                                placeholder='Premium',
                                value=5_000,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 5,000",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            )
                        ]),
                    ], className='input-col', style={
                        'width': '48%',
                        'display': 'inline-block',
                        'verticalAlign': 'top',
                        'paddingRight': '10px',
                        'minWidth': '180px'
                    }),
                    # Loss simulation column
                    html.Div([
                        html.H3("Loss simulation", style={'color': colors["text"], 'marginBottom': '18px', 'textAlign': 'center'}),
                        html.Div([
                            html.Label([
                                'Policy Limit',
                                tooltip_icon('tooltip-policy-limit', 'The maximum amount the insurer will pay for all claims under a single insurance policy during the policy period.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-policy-limit',
                                type='number',
                                placeholder='Policy Limit',
                                value=5_000_000,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 5,000,000",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            ),
                            html.Div(
                                "(If the policy limit is lower than the excess then expected recoveries = 0 because no policies can be written).",
                                id='policy-limit-warning',
                                style={'color': '#ffb347', 'fontSize': '0.95em', 'marginBottom': '10px', 'display': 'none'}
                            )
                        ]),
                        html.Div([
                            html.Label([
                                'Mean Frequency',
                                tooltip_icon('tooltip-mean-frequency', 'The average number of claims expected in a year.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-mean-frequency',
                                type='number',
                                placeholder='Mean Frequency',
                                value=2,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 2 (claims per year)",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            )
                        ]),
                        html.Div([
                            html.Label([
                                'Simulations',
                                tooltip_icon('tooltip-simulations', 'The number of times the model is run to estimate possible outcomes.')
                            ], style={'color': colors["text"]}),
                            dcc.Input(
                                id='input-n-sims',
                                type='number',
                                placeholder='Simulations',
                                value=100_000,
                                min=1000,
                                step=1000,
                                style={
                                    'width': '100%',
                                    'backgroundColor': colors["card"],
                                    'color': colors["text"],
                                    'border': f'1px solid {colors["border"]}',
                                    'marginBottom': '5px',
                                    'fontSize': '1.1em'
                                }
                            ),
                            html.Div(
                                "Example: 100,000 (recommended)",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px'}
                            )
                        ]),
                        html.Div([
                            html.Label([
                                'GPD Parameters',
                                tooltip_icon('tooltip-gpd', 'Parameters for the Generalized Pareto Distribution: Shape, Scale, and Location.')
                            ], style={'color': colors["text"], 'marginBottom': '5px'}),
                            html.Div([
                                dcc.Input(
                                    id='input-gpd-shape',
                                    type='number',
                                    placeholder='Shape',
                                    value=0.33,
                                    style={
                                        'width': '30%',
                                        'display': 'inline-block',
                                        'backgroundColor': colors["card"],
                                        'color': colors["text"],
                                        'border': f'1px solid {colors["border"]}',
                                        'marginRight': '2%',
                                        'fontSize': '1.1em'
                                    }
                                ),
                                dcc.Input(
                                    id='input-gpd-scale',
                                    type='number',
                                    placeholder='Scale',
                                    value=100000,
                                    style={
                                        'width': '30%',
                                        'display': 'inline-block',
                                        'backgroundColor': colors["card"],
                                        'color': colors["text"],
                                        'border': f'1px solid {colors["border"]}',
                                        'marginRight': '2%',
                                        'fontSize': '1.1em'
                                    }
                                ),
                                dcc.Input(
                                    id='input-gpd-loc',
                                    type='number',
                                    placeholder='Location',
                                    value=1000000,
                                    style={
                                        'width': '30%',
                                        'display': 'inline-block',
                                        'backgroundColor': colors["card"],
                                        'color': colors["text"],
                                        'border': f'1px solid {colors["border"]}',
                                        'fontSize': '1.1em'
                                    }
                                ),
                            ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '2%'}),
                            html.Div(
                                "Examples: Shape 0.33, Scale 100,000, Location 1,000,000",
                                style={'color': '#aaa', 'fontSize': '0.95em', 'marginBottom': '10px', 'marginTop': '5px'}
                            ),
                        ]),
                    ], className='input-col', style={
                        'width': '48%',
                        'display': 'inline-block',
                        'verticalAlign': 'top',
                        'paddingLeft': '10px',
                        'minWidth': '180px'
                    }),
                ], className='input-columns', style={
                    'display': 'flex',
                    'flexDirection': 'row',
                    'justifyContent': 'space-between',
                    'gap': '10px'
                }),
                html.Div([
                    html.Label([
                        dcc.Checklist(
                            id='show-raw-data',
                            options=[{'label': ' Show raw simulated recoveries', 'value': 'show'}],
                            value=[],
                            style={'marginBottom': '10px', 'color': colors["text"]}
                        )
                    ])
                ], style={'marginTop': '18px'}),
                html.Button(
                    'Submit',
                    id='submit-val',
                    n_clicks=0,
                    style={
                        'marginTop': '18px',
                        'width': '100%',
                        'backgroundColor': '#444',
                        'color': '#F5F6FA',
                        'border': 'none'
                    },
                    disabled=False
                ),
                dcc.Loading(
                    id="loading",
                    type="default",
                    color=loading_color,
                    children=[
                        html.Div(
                            id='output-summary',
                            style={'marginTop': '20px', 'color': colors["text"]}
                        ),
                        html.Div(id='raw-data-table-container')
                    ]
                ),
            ], className='main-left-col', style={
                'width': '32%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '30px',
                'minWidth': '320px',
                'backgroundColor': colors["card"],
                'borderRadius': '10px',
                'position': 'relative',
                'left': 0,
            }),
            html.Div([
                html.Div(
                    dcc.Graph(
                        id='recoveries-cdf',
                        style={'height': '350px', 'backgroundColor': '#23272E'}
                    ),
                    id='recoveries-cdf-container',
                    style={'display': 'none'}
                ),
                html.Div(
                    dcc.Graph(
                        id='recoveries-hist',
                        style={'height': '350px', 'backgroundColor': '#23272E'}
                    ),
                    id='recoveries-hist-container',
                    style={'display': 'none'}
                ),
                html.Div([
                    html.Div(
                        dcc.Graph(
                            id='effects-line',
                            style={'height': '400px', 'width': '100%', 'backgroundColor': '#23272E'}
                        ),
                        id='effects-line-container',
                        style={'display': 'none', 'width': '100%', 'marginTop': '40px'}
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id='recoveries-pie',
                                style={'height': '400px', 'width': '100%', 'backgroundColor': '#23272E'}
                            ),
                            html.Div(style={'height': '0px'}),
                            html.Div(
                                id='pie-legend-custom',
                                style={
                                    'textAlign': 'center',
                                    'marginTop': '10px',
                                    'color': '#F5F6FA',
                                    'whiteSpace': 'pre-line'
                                }
                            )
                        ],
                        id='recoveries-pie-container',
                        style={'display': 'none', 'width': '100%', 'marginTop': '40px'}
                    )
                ], style={'width': '100%'})
            ], className='main-right-col', style={
                'width': '66%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '30px',
                'minWidth': '400px',
                'backgroundColor': '#181A1B',
                'borderRadius': '10px'
            })
        ], className='main-flex-row', style={
            'width': '100%',
            'display': 'flex',
            'flexDirection': 'row',
            'justifyContent': 'space-between',
            'backgroundColor': colors["background"],
            'minHeight': '100vh'
        })
    ])

# More Info page: external resources
def more_info_page(theme="dark"):
    colors = THEMES[theme]
    card_bg = colors["card"]
    text_color = "#23272E" if theme == "light" else colors["text"]
    bg_color = "#FFFFFF" if theme == "light" else "#181A1B"

    def card_text(text):
        if len(text) > 35:
            return {
                'padding': '10px',
                'fontWeight': 'bold',
                'fontSize': '0.95em',
                'lineHeight': '1.1em',
                'textAlign': 'center',
                'backgroundColor': card_bg,
                'color': text_color,
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'whiteSpace': 'normal'
            }
        else:
            return {
                'padding': '10px',
                'fontWeight': 'bold',
                'fontSize': '1.1em',
                'lineHeight': '1.2em',
                'textAlign': 'center',
                'backgroundColor': card_bg,
                'color': text_color,
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'whiteSpace': 'normal'
            }

    card_style = {
        'backgroundColor': card_bg,
        'borderRadius': '10px',
        'padding': '0px',
        'margin': '10px',
        'boxSizing': 'border-box',
        'color': text_color,
        'minHeight': '180px',
        'maxHeight': '180px',
        'minWidth': '220px',
        'maxWidth': '220px',
        'flex': '1',
        'overflow': 'hidden',
        'cursor': 'pointer',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'flex-start'
    }
    row_style = {
        'display': 'flex',
        'flexDirection': 'row',
        'alignItems': 'flex-start',
        'justifyContent': 'center',
        'marginBottom': '20px'
    }
    def card_text(text):
        if len(text) > 35:
            return {
                'padding': '10px',
                'fontWeight': 'bold',
                'fontSize': '0.95em',
                'lineHeight': '1.1em',
                'textAlign': 'center',
                'backgroundColor': card_bg,
                'color': text_color,
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'whiteSpace': 'normal'
            }
        else:
            return {
                'padding': '10px',
                'fontWeight': 'bold',
                'fontSize': '1.1em',
                'lineHeight': '1.2em',
                'textAlign': 'center',
                'backgroundColor': card_bg,
                'color': text_color,
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'whiteSpace': 'normal'
            }
    # Cards for external resources
    first_card = html.A(
        [
            html.Img(
                src="https://info.online.hbs.edu/hubfs/CORe_Blog/AdobeStock_77573252-159655-edited.jpeg",
                alt="London Skyline",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "How insurance markets work",
                style=card_text("How insurance markets work")
            )
        ],
        href="https://online.hbs.edu/blog/post/risky-business-how-insurance-markets-actually-work",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    second_card = html.A(
        [
            html.Img(
                src="https://i.ytimg.com/vi/cxQzlwto64Y/maxresdefault.jpg",
                alt="The History of Insurance",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "The history of insurance",
                style=card_text("The history of insurance")
            )
        ],
        href="https://worldhistoryjournal.com/2025/03/09/the-history-of-insurance-industry/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    third_card = html.A(
        [
            html.Img(
                src="https://eor7ztmv4pb.exactdn.com/wp-content/uploads/2021/03/word-image-14964-2.png?strip=all&lossy=1&ssl=1",
                alt="Reinsurance Basics",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Reinsurance basics",
                style=card_text("Reinsurance basics")
            )
        ],
        href="https://web.theinstitutes.org/course/reinsurance-basics",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    gpd_card = html.A(
        [
            html.Img(
                src="https://upload.wikimedia.org/wikipedia/commons/5/55/Gpdcdf.svg",
                alt="Generalized Pareto Distribution",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'contain',
                    'display': 'block',
                    'backgroundColor': '#fff',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Generalized Pareto Distribution",
                style=card_text("Generalized Pareto Distribution")
            )
        ],
        href="https://en.wikipedia.org/wiki/Generalized_Pareto_distribution",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    poisson_card = html.A(
        [
            html.Img(
                src="https://upload.wikimedia.org/wikipedia/commons/1/16/Poisson_pmf.svg",
                alt="Poisson Distribution",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'contain',
                    'display': 'block',
                    'backgroundColor': '#fff',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Poisson Distribution",
                style=card_text("Poisson Distribution")
            )
        ],
        href="https://en.wikipedia.org/wiki/Poisson_distribution",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    types_reinsurance_card = html.A(
        [
            html.Img(
                src="https://th.bing.com/th/id/R.8b7e9ec41fd5b182eaae7d607ebcb03a?rik=KC5Me1RBwl%2fwdw&riu=http%3a%2f%2fkeydifferences.com%2fwp-content%2fuploads%2f2017%2f03%2freinsurance1.jpg&ehk=OhBqDjupGVta%2bzT5MdYhRVgckpzc8VpH9omulCsQ1bI%3d&risl=&pid=ImgRaw&r=0&sres=1&sresct=1&srh=799&srw=922",
                alt="Types of reinsurance",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Types of reinsurance",
                style=card_text("Types of reinsurance")
            )
        ],
        href="https://theinsuranceuniverse.com/types-of-reinsurance-agreements/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    fourth_card = html.A(
        [
            html.Img(
                src="https://citybuildingowners.com/wp-content/uploads/2019/09/bigstock-Insurance-Concept-And-Hurrican-263279497.jpg",
                alt="Biggest Insurance Claim Payouts",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Biggest insurance claim payouts",
                style=card_text("Biggest insurance claim payouts")
            )
        ],
        href="https://www.falconinsurance.co.uk/10-biggest-insurance-claim-payouts-of-all-time/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    fifth_card = html.A(
        [
            html.Img(
                src="https://fbf.eui.eu/wp-content/uploads/2022/04/Economics-insurance-market.jpg",
                alt="The Economics of Insurance",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "The economics of insurance",
                style=card_text("The economics of insurance")
            )
        ],
        href="https://www.sciencedirect.com/book/9780444873446/economics-of-insurance",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    fun_facts_first_card = html.A(
        [
            html.Img(
                src="https://citybuildingowners.com/wp-content/uploads/2019/09/bigstock-Insurance-Concept-And-Hurrican-263279497.jpg",
                alt="Biggest Insurance Claim Payouts",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Biggest insurance claims",
                style=card_text("Biggest insurance claims")
            )
        ],
        href="https://www.falconinsurance.co.uk/10-biggest-insurance-claim-payouts-of-all-time/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    surprising_facts_card = html.A(
        [
            html.Img(
                src="https://media-exp1.licdn.com/dms/image/C4E12AQEfgYvlKqyaLw/article-cover_image-shrink_600_2000/0/1537249838603?e=2147483647&v=beta&t=KjVeLhaZILHXHWIE6x_sWd2ZIrNoKHBAbd5ZmaXQnKM",
                alt="Surprising facts",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Surprising facts",
                style=card_text("Surprising facts")
            )
        ],
        href="https://factsvibes.com/fun-facts-about-insurance/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    crazy_facts_card = html.A(
        [
            html.Img(
                src="https://factsvibes.com/wp-content/uploads/2024/01/10-fascinating-fun-facts-about-insurance-you-need-to-know-1024x427.jpg",
                alt="Crazy facts",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Crazy facts",
                style=card_text("Crazy facts")
            )
        ],
        href="https://facts.uk/facts-about-insurance/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    how_insurance_began_card = html.A(
        [
            html.Img(
                src="https://excaliburinsurance.ca/blog/wp-content/uploads/2023/02/How-Did-Insurance-Originally-Begin-Updated.jpg",
                alt="How insurance began",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "How insurance began",
                style=card_text("How insurance began")
            )
        ],
        href="https://www.bowtie.com.hk/blog/en/insurance101/insurance-history/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    types_of_insurance_card = html.A(
        [
            html.Img(
                src="https://c8.alamy.com/comp/2E3GENX/illustration-of-the-various-types-of-insurance-2E3GENX.jpg",
                alt="Types of insurance",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Types of insurance",
                style=card_text("Types of insurance")
            )
        ],
        href="https://www.hsbc.co.uk/insurance/types-of-insurance/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    insurance_glossary_card = html.A(
        [
            html.Img(
                src="https://promtinsurance.com/wp-content/uploads/2023/08/insurance-terms.jpg",
                alt="Insurance glossary",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Insurance glossary",
                style=card_text("Insurance glossary")
            )
        ],
        href="https://www.einsurance.com/glossary/",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    insurance_myths_card = html.A(
        [
            html.Img(
                src="https://novusacs.com/wp-content/uploads/2022/10/iStock-1343642331.jpg",
                alt="Insurance myths debunked",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Insurance myths debunked",
                style=card_text("Insurance myths debunked")
            )
        ],
        href="https://www.hixsonmalinowski.com/blog/10-common-insurance-myths-debunked-what-you-need-to-know#:~:text=In%20our%20latest%20blog%2C%20we%20debunk%2010%20common,fiction.%20Don%E2%80%99t%20fall%20for%20these%20myths%E2%80%94read%20more%20now%21",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )
    reinsurance_market_trends_card = html.A(
        [
            html.Img(
                src="https://www.jiwa.com.au/wp-content/uploads/2023/03/market-trends.png",
                alt="Reinsurance market trends",
                style={
                    'width': '100%',
                    'height': '90px',
                    'objectFit': 'cover',
                    'display': 'block',
                    'borderTopLeftRadius': '10px',
                    'borderTopRightRadius': '10px'
                }
            ),
            html.Div(
                "Reinsurance market trends",
                style=card_text("Reinsurance market trends")
            )
        ],
        href="https://www.gminsights.com/industry-analysis/reinsurance-market",
        target="_blank",
        style={**card_style, 'textDecoration': 'none'}
    )

    return html.Div([
        html.H1(
            "More Info on Insurance",
            style={
                'fontWeight': 'bold',
                'fontSize': '2.2em',
                'textAlign': 'center',
                'marginBottom': '24px',
                'color': colors["primary"] if theme == "dark" else "#3B4CCA"
            }
        ),
        html.Div([
            html.Div([
                html.Div("Insurance", style={
                    'minWidth': '120px',
                    'fontWeight': 'bold',
                    'fontSize': '1.2em',
                    'color': text_color,
                    'marginTop': '40px',
                    'marginRight': '12px',
                    'textAlign': 'right'
                }),
                first_card, second_card, fifth_card, types_of_insurance_card, insurance_glossary_card
            ], style=row_style),
            html.Div([
                html.Div("Reinsurance", style={
                    'minWidth': '120px',
                    'fontWeight': 'bold',
                    'fontSize': '1.2em',
                    'color': text_color,
                    'marginTop': '40px',
                    'marginRight': '12px',
                    'textAlign': 'right'
                }),
                third_card, types_reinsurance_card, gpd_card, poisson_card, reinsurance_market_trends_card
            ], style=row_style),
            html.Div([
                html.Div("Fun facts", style={
                    'minWidth': '120px',
                    'fontWeight': 'bold',
                    'fontSize': '1.2em',
                    'color': text_color,
                    'marginTop': '40px',
                    'marginRight': '12px',
                    'textAlign': 'right'
                }),
                fun_facts_first_card, surprising_facts_card, crazy_facts_card, how_insurance_began_card, insurance_myths_card
            ], style=row_style),
        ], style={'width': '95%', 'margin': '0 auto', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
    ], style={
        'backgroundColor': bg_color,
        'minHeight': '100vh',
        'height': '100vh',
        'margin': 0,
        'padding': 0,
        'boxSizing': 'border-box'
    })

# Navigation bar
navbar = html.Div([
    dcc.Tabs(
        id='page-tabs',
        value='home',
        children=[
            dcc.Tab(label='Home', value='home'),
            dcc.Tab(label='Main App', value='main'),
            dcc.Tab(label='More Info', value='moreinfo'),
        ],
        colors={
            "border": "#23272E",
            "primary": "#859EFF",
            "background": "#181A1B"
        }
    ),
    html.Div(
        [
            daq.ToggleSwitch(
                id='theme-toggle',
                label=['Dark', 'Light'],
                value=False,
                style={'marginLeft': '20px'}
            ),
            html.Div(
                "(Dark mode recommended)",
                id="dark-mode-msg",
                style={
                    'marginTop': '8px',
                    'fontSize': '0.95em',
                    'color': '#aaa',
                    'textAlign': 'center'
                }
            )
        ],
        style={'float': 'right', 'margin': '10px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
    )
], style={
    'backgroundColor': '#181A1B',
    'color': '#F5F6FA',
    'marginBottom': '0px',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'space-between'
})

# App main layout with theme support
app.layout = html.Div([
    navbar,
    dcc.Store(id='theme-store', data='dark'),
    html.Div(id='page-content')
], id='main-app-bg', style={
    'backgroundColor': THEMES["dark"]["background"],
    'minHeight': '100vh',
    'height': '100vh',
    'margin': 0,
    'padding': 0,
    'boxSizing': 'border-box'
})

# Update the main background color when theme changes
@app.callback(
    Output('main-app-bg', 'style'),
    Input('theme-store', 'data')
)
def update_main_bg(theme):
    return {
        'backgroundColor': THEMES[theme]["background"],
        'minHeight': '100vh',
        'height': '100vh',
        'margin': 0,
        'padding': 0,
        'boxSizing': 'border-box'
    }

# Theme toggle callback
@app.callback(
    Output('theme-store', 'data'),
    Input('theme-toggle', 'value')
)
def update_theme(is_light):
    return 'light' if is_light else 'dark'

# Callback to update the dark mode message color for visibility
@app.callback(
    Output('dark-mode-msg', 'style'),
    Input('theme-store', 'data')
)
def update_dark_mode_msg(theme):
    return {
        'marginTop': '8px',
        'fontSize': '0.95em',
        'color': "#FFFFFF" if theme == 'light' else '#aaa',
        'textAlign': 'center',
        'display': 'block'
    }

# Page navigation callback with theme
@app.callback(
    Output('page-content', 'children'),
    Input('page-tabs', 'value'),
    Input('theme-store', 'data')
)
def render_page(tab, theme):
    if tab == 'home':
        return home_page(theme)
    elif tab == 'main':
        return main_app_page(theme)
    elif tab == 'moreinfo':
        return more_info_page(theme)
    return home_page(theme)

# Show/hide policy limit warning based on input changes
@app.callback(
    Output('policy-limit-warning', 'style'),
    Input('input-policy-limit', 'value'),
    Input('input-excess', 'value'),
)
def show_policy_limit_warning(policy_limit, excess):
    try:
        if policy_limit is not None and excess is not None and float(policy_limit) < float(excess):
            return {'color': '#ffb347', 'fontSize': '0.95em', 'marginBottom': '10px', 'display': 'block'}
    except Exception:
        pass
    return {'display': 'none'}

# Show/hide aggregate deductible warning as user is typing
@app.callback(
    Output('aggregate-deductible-warning', 'style'),
    Input('input-excess', 'value'),
    Input('input-aggregate-deductible', 'value'),
)
def show_aggregate_deductible_warning(excess, aggregate_deductible):
    try:
        if aggregate_deductible is not None and excess is not None and float(aggregate_deductible) <= float(excess):
            return {'color': '#ffb347', 'fontSize': '0.95em', 'marginBottom': '10px', 'display': 'block'}
    except Exception:
        pass
    return {'display': 'none'}

# Show/hide limit-excess warning as user is typing
@app.callback(
    Output('limit-excess-warning', 'style'),
    Input('input-limit', 'value'),
    Input('input-excess', 'value'),
)
def show_limit_excess_warning(limit, excess):
    try:
        if limit is not None and excess is not None and float(limit) < float(excess):
            return {
                'color': '#ffb347',
                'fontSize': '0.95em',
                'marginBottom': '10px',
                'display': 'block'
            }
    except Exception:
        pass
    return {'display': 'none'}

# Main calculation and graph update callback
@app.callback(
    Output('output-summary', 'children'),
    Output('recoveries-cdf', 'figure'),
    Output('recoveries-hist', 'figure'),
    Output('effects-line', 'figure'),
    Output('recoveries-pie', 'figure'),
    Output('recoveries-cdf-container', 'style'),
    Output('recoveries-hist-container', 'style'),
    Output('recoveries-pie-container', 'style'),
    Output('effects-line-container', 'style'),
    Output('raw-data-table-container', 'children'),
    Input('submit-val', 'n_clicks'),
    State('input-limit', 'value'),
    State('input-aggregate-limit', 'value'),
    State('input-policy-limit', 'value'),
    State('input-excess', 'value'),
    State('input-aggregate-deductible', 'value'),
    State('input-premium', 'value'),
    State('input-mean-frequency', 'value'),
    State('input-n-sims', 'value'),
    State('theme-store', 'data'),
    State('show-raw-data', 'value'),
    prevent_initial_call=True
)
def update_output(
    n_clicks, limit, aggregate_limit, policy_limit, excess, aggregate_deductible, premium, mean_frequency, n_sims, theme,
    show_raw_data
):
    # Validate user input
    if (
        limit is None or aggregate_limit is None or policy_limit is None or excess is None or
        aggregate_deductible is None or premium is None or mean_frequency is None or n_sims is None
    ):
        return (
            "Please enter limit, aggregate limit, policy limit, excess, aggregate deductible, premium, mean frequency, and number of simulations.",
            go.Figure(), go.Figure(), go.Figure(),
            {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        )
    try:
        limit = float(limit)
        aggregate_limit = float(aggregate_limit)
        policy_limit = float(policy_limit)
        excess = float(excess)
        aggregate_deductible = float(aggregate_deductible)
        premium = float(premium)
        mean_frequency = float(mean_frequency)
        n_sims = int(n_sims)
    except Exception:
        return (
            "Inputs must be numbers.",
            go.Figure(), go.Figure(), go.Figure(),
            {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        )
    if aggregate_limit < limit:
        return (
            "Aggregate limit must be greater than or equal to limit.",
            go.Figure(), go.Figure(), go.Figure(),
            {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        )
    if aggregate_deductible <= excess:
        return (
            "Aggregate deductible must be greater than the excess as it is for a year rather than just one claim.",
            go.Figure(), go.Figure(), go.Figure(),
            {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        )

    config.n_sims = n_sims

    sev_dist = distributions.GPD(shape=0.33, scale=100000, loc=1000000)
    freq_dist = distributions.Poisson(mean=mean_frequency)
    losses_pre_cap = FrequencySeverityModel(freq_dist, sev_dist).generate()
    losses_post_cap = np.minimum(losses_pre_cap, policy_limit)
    gross_losses = losses_post_cap

    agg_limit = [aggregate_limit] if aggregate_limit else [None]
    agg_deductible = [aggregate_deductible] if aggregate_deductible else [None]

    prog = XoLTower(
        limit=[limit],
        excess=[excess],
        aggregate_limit=agg_limit,
        aggregate_deductible=agg_deductible,  
        premium=[premium],
        reinstatement_cost=[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]],
    )
    prog_results = prog.apply(gross_losses)
    recoveries_raw = prog_results.recoveries.aggregate()
    recoveries = np.array(
        [float(r.value) if hasattr(r, 'value') else float(r) for r in recoveries_raw],
        dtype=float
    ).flatten()
    if recoveries.size == 0:
        return (
            "No recoveries generated.",
            go.Figure(), go.Figure(), go.Figure(),
            {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        )
    # Calculate statistics
    expected_recoveries = float(np.mean(recoveries))
    median_recoveries = float(np.median(recoveries))
    counts, bin_edges = np.histogram(recoveries, bins=100)
    mode_index = int(np.argmax(counts))
    mode_recoveries = float((bin_edges[mode_index] + bin_edges[mode_index + 1]) / 2)
    prob_gt_zero = float(np.mean(recoveries > 0))

    # Set outline color based on theme
    graph_outline = "#23272E" if theme == "light" else "#FFFFFF"

    # CDF plot
    sorted_rec = np.sort(recoveries)
    cum_prob = np.arange(1, len(sorted_rec) + 1) / len(sorted_rec)
    fig_cdf = go.Figure()
    fig_cdf.add_trace(go.Scatter(
        x=sorted_rec,
        y=cum_prob,
        name='Cumulative Probability',
        mode='lines',
        marker=dict(color='blue', size=4),
        line=dict(color='blue')
    ))
    min_x = float(np.min(sorted_rec))
    max_x = float(np.max(sorted_rec))
    x_margin = (max_x - min_x) * 0.05 if max_x > min_x else 1
    fig_cdf.update_layout(
        title='Recoveries',
        xaxis_title='value',
        yaxis_title='Cumulative Probability',
        yaxis=dict(range=[0, 1], linecolor=graph_outline, gridcolor=graph_outline),
        xaxis=dict(range=[min_x - x_margin, max_x + x_margin], linecolor=graph_outline, gridcolor=graph_outline),
        plot_bgcolor='white' if theme == "light" else "#23272E",
        paper_bgcolor='white' if theme == "light" else "#23272E",
        font=dict(color=graph_outline),
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(font=dict(color=graph_outline))
    )

    # Histogram plot
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=recoveries,
        nbinsx=50,
        marker_color='orange',
        name='Recoveries Histogram',
        opacity=0.8
    ))
    fig_hist.update_layout(
        title='Histogram of Recoveries',
        xaxis_title='Recoveries',
        yaxis_title='Count',
        plot_bgcolor='white' if theme == "light" else "#23272E",
        paper_bgcolor='white' if theme == "light" else "#23272E",
        font=dict(color=graph_outline),
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(font=dict(color=graph_outline)),
        xaxis=dict(linecolor=graph_outline, gridcolor=graph_outline),
        yaxis=dict(linecolor=graph_outline, gridcolor=graph_outline)
    )

    # Pie chart calculation: bin recoveries into ranges
    total = recoveries.size
    count_zero = np.sum(recoveries == 0)
    count_0_10k = np.sum((recoveries > 1000) & (recoveries <= 10000))
    count_10k_50k = np.sum((recoveries > 10000) & (recoveries <= 50000))
    count_50k_100k = np.sum((recoveries > 50000) & (recoveries <= 100000))
    count_100k_1m = np.sum((recoveries > 100000) & (recoveries <= 1000000))
    count_1m_10m = np.sum((recoveries > 1000000) & (recoveries <= 10000000))
    count_10m_25m = np.sum((recoveries > 10_000_000) & (recoveries <= 25_000_000))
    count_25m_50m = np.sum((recoveries > 25_000_000) & (recoveries <= 50_000_000))
    count_50m_75m = np.sum((recoveries > 50_000_000) & (recoveries <= 75_000_000))
    count_75m_100m = np.sum((recoveries > 75_000_000) & (recoveries <= 100_000_000))
    count_100m_250m = np.sum((recoveries > 100_000_000) & (recoveries <= 250_000_000))
    count_250m_500m = np.sum((recoveries > 250_000_000) & (recoveries <= 500_000_000))
    count_500m_750m = np.sum((recoveries > 500_000_000) & (recoveries <= 750_000_000))
    count_750m_1b = np.sum((recoveries > 750_000_000) & (recoveries <= 1_000_000_000))
    count_1b_2_5b = np.sum((recoveries > 1_000_000_000) & (recoveries <= 2_500_000_000))
    count_2b_5b = np.sum((recoveries > 2_000_000_000) & (recoveries <= 5_000_000_000))
    count_5b_10b = np.sum((recoveries > 5_000_000_000) & (recoveries <= 10_000_000_000))
    count_10b_25b = np.sum((recoveries > 10_000_000_000) & (recoveries <= 25_000_000_000))
    count_25b_50b = np.sum((recoveries > 25_000_000_000) & (recoveries <= 50_000_000_000))
    count_50b_75b = np.sum((recoveries > 50_000_000_000) & (recoveries <= 75_000_000_000))
    count_75b_100b = np.sum((recoveries > 75_000_000_000) & (recoveries <= 100_000_000_000))
    count_100b_250b = np.sum((recoveries > 100_000_000_000) & (recoveries <= 250_000_000_000))
    count_250b_500b = np.sum((recoveries > 250_000_000_000) & (recoveries <= 500_000_000_000))
    count_500b_750b = np.sum((recoveries > 500_000_000_000) & (recoveries <= 750_000_000_000))
    count_750b_1t = np.sum((recoveries > 750_000_000_000) & (recoveries <= 1_000_000_000_000))
    count_gt_1t = np.sum(recoveries > 1_000_000_000_000)

    pie_labels = [
        "Recoveries = 0",
        "Recoveries = 0-10K",
        "Recoveries = 10K-50K",
        "Recoveries = 50K-100K",
        "Recoveries = 100K-1M",
        "Recoveries = 1M-10M"
    ]
    pie_values = [count_zero, count_0_10k, count_10k_50k, count_50k_100k, count_100k_1m, count_1m_10m]

    # Add higher bins if needed
    max_rec = recoveries.max()
    if max_rec > 10_000_000:
        pie_labels.append("Recoveries = 10M-25M")
        pie_values.append(count_10m_25m)
    if max_rec > 25_000_000:
        pie_labels.append("Recoveries = 25M-50M")
        pie_values.append(count_25m_50m)
    if max_rec > 50_000_000:
        pie_labels.append("Recoveries = 50M-75M")
        pie_values.append(count_50m_75m)
    if max_rec > 75_000_000:
        pie_labels.append("Recoveries = 75M-100M")
        pie_values.append(count_75m_100m)
    if max_rec > 100_000_000:
        pie_labels.append("Recoveries = 100M-250M")
        pie_values.append(count_100m_250m)
    if max_rec > 250_000_000:
        pie_labels.append("Recoveries = 250M-500M")
        pie_values.append(count_250m_500m)
    if max_rec > 500_000_000:
        pie_labels.append("Recoveries = 500M-750M")
        pie_values.append(count_500m_750m)
    if max_rec > 750_000_000:
        pie_labels.append("Recoveries = 750M-1B")
    if max_rec > 1_000_000_000:
        pie_labels.append("Recoveries = 1B-2.5B")
        pie_values.append(count_1b_2_5b)
    if max_rec > 2_000_000_000:
        pie_labels.append("Recoveries = 2.5B-5B")
        pie_values.append(count_2b_5b)
    if max_rec > 5_000_000_000:
        pie_labels.append("Recoveries = 5B-10B")
        pie_values.append(count_5b_10b)
    if max_rec > 10_000_000_000:
        pie_labels.append("Recoveries = 10B-25B")
        pie_values.append(count_10b_25b)
    if max_rec > 25_000_000_000:
        pie_labels.append("Recoveries = 25B-50B")
        pie_values.append(count_25b_50b)
    if max_rec > 50_000_000_000:
        pie_labels.append("Recoveries = 50B-75B")
        pie_values.append(count_50b_75b)
    if max_rec > 75_000_000_000:
        pie_labels.append("Recoveries = 75B-100B")
        pie_values.append(count_75b_100b)
    if max_rec > 100_000_000_000:
        pie_labels.append("Recoveries = 100B-250B")
        pie_values.append(count_100b_250b)
    if max_rec > 250_000_000_000:
        pie_labels.append("Recoveries = 250B-500B")
        pie_values.append(count_250b_500b)
    if max_rec > 500_000_000_000:
        pie_labels.append("Recoveries = 500B-750B")
        pie_values.append(count_500b_750b)
    if max_rec > 750_000_000_000:
        pie_labels.append("Recoveries = 750B-1T")
        pie_values.append(count_750b_1t)
    if max_rec > 1_000_000_000_000:
        pie_labels.append("Recoveries > 1T")
        pie_values.append(count_gt_1t)

    # Only show bins with values
    filtered_labels = []
    filtered_values = []
    for label, value in zip(pie_labels, pie_values):
        if value > 0:
            filtered_labels.append(label)
            filtered_values.append(value)

    fig_pie = go.Figure(
        data=[go.Pie(labels=filtered_labels, values=filtered_values, hole=0.3)]
    )
    fig_pie.update_layout(
        title="Recovery Distribution",
        plot_bgcolor='white' if theme == "light" else "#23272E",
        paper_bgcolor='white' if theme == "light" else "#23272E",
        font=dict(color=graph_outline),
        legend=dict(
            orientation="v",
            y=-0.8,
            x=0.5,
            xanchor="center",
            font=dict(color=graph_outline)
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Effects line graph: show how mean recoveries change with limit/excess
    limits = np.linspace(0, 10_000_000, 11)
    excesses = np.linspace(0, max(limit-1, 10_000_000), 11)
    mean_rec_by_limit = []
    mean_rec_by_excess = []

    for l in limits:
        prog = XoLTower(
            limit=[l],
            excess=[excess],
            aggregate_limit=[None],
            premium=[premium],
            reinstatement_cost=[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]],
        )
        prog_results = prog.apply(gross_losses)
        recs = np.array(
            [float(r.value) if hasattr(r, 'value') else float(r) for r in prog_results.recoveries.aggregate()],
            dtype=float
        ).flatten()
        mean_rec_by_limit.append(np.mean(recs))

    for e in excesses:
        prog = XoLTower(
            limit=[limit],
            excess=[e],
            aggregate_limit=[None],
            premium=[premium],
            reinstatement_cost=[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]],
        )
        prog_results = prog.apply(gross_losses)
        recs = np.array(
            [float(r.value) if hasattr(r, 'value') else float(r) for r in prog_results.recoveries.aggregate()],
            dtype=float
        ).flatten()
        mean_rec_by_excess.append(np.mean(recs))

    fig_effects = go.Figure()
    fig_effects.add_trace(go.Scatter(
        x=limits, y=mean_rec_by_limit, mode='lines+markers', name='Varying Limit'
    ))
    fig_effects.add_trace(go.Scatter(
        x=excesses, y=mean_rec_by_excess, mode='lines+markers', name='Varying Excess'
    ))
    fig_effects.update_layout(
        title="Effect of Limit and excess on Expected Recoveries",
        xaxis_title="Parameter Value",
        yaxis_title="Expected Recoveries",
        legend=dict(orientation="h", y=-0.2, font=dict(color=graph_outline)),
        plot_bgcolor='white' if theme == "light" else "#23272E",
        paper_bgcolor='white' if theme == "light" else "#23272E",
        font=dict(color=graph_outline),
        xaxis=dict(linecolor=graph_outline, gridcolor=graph_outline),
        yaxis=dict(linecolor=graph_outline, gridcolor=graph_outline),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Statistics summary for display
    stats_html = html.Div([
        html.H4(
            "Statistics",
            style={
                'color': "#FFFFFF",
                'marginBottom': '30px',
                'fontSize': '2em',
                'fontWeight': 'bold'
            }
        ),
        html.P(f"Expected recoveries (mean): {expected_recoveries:,.2f}"),
        html.P(f"Mode of recoveries: {mode_recoveries:,.2f}"),
        html.P(f"Probability recoveries > 0: {prob_gt_zero:.2%}"),
        html.P(f"1st percentile: {np.percentile(recoveries, 1):,.2f}"),
        html.P(f"25th percentile: {np.percentile(recoveries, 25):,.2f}"),
        html.P(f"Median recoveries: {median_recoveries:,.2f}"),
        html.P(f"75th percentile: {np.percentile(recoveries, 75):,.2f}"),
        html.P(f"99th percentile: {np.percentile(recoveries, 99):,.2f}"),
        html.P(f"Worst case scenario (max): {np.max(recoveries):,.2f}") 
    ])

    show_style = {'display': 'block'}
    hide_style = {'display': 'none'}

    # Raw data table (show only if requested)
    raw_data_table = None
    if 'show' in show_raw_data:
        # Show first 100 recoveries for performance
        raw_data_table = dash_table.DataTable(
            columns=[{"name": "Recovery", "id": "Recovery"}],
            data=[{"Recovery": f"{v:,.2f}"} for v in recoveries[:100]],
            style_table={'height': '300px', 'overflowY': 'auto', 'backgroundColor': 'white' if theme == "light" else "#23272E"},
            style_cell={'color': '#23272E' if theme == "light" else "#F5F6FA", 'backgroundColor': 'white' if theme == "light" else "#23272E"},
            style_header={'backgroundColor': '#859EFF', 'color': '#23272E' if theme == "light" else "#F5F6FA"},
            page_size=100
        )

    return (
        stats_html, fig_cdf, fig_hist, fig_effects, fig_pie,
        show_style, show_style, show_style, show_style,
        raw_data_table
    )

# Hide simulation recommendation after submit
@app.callback(
    Output('sim-recommend-msg', 'style'),
    Input('submit-val', 'n_clicks'),
    prevent_initial_call=True
)
def hide_sim_recommend_msg(n_clicks):
    return {'display': 'none'}

# show/hide aggregate limit warning based on input changes
@app.callback(
    Output('aggregate-limit-warning', 'style'),
    Input('input-limit', 'value'),
    Input('input-aggregate-limit', 'value'),
)
def show_aggregate_limit_warning(limit, aggregate_limit):
    try:
        if aggregate_limit is not None and limit is not None and float(aggregate_limit) < float(limit):
            return {'color': '#ffb347', 'fontSize': '0.95em', 'marginBottom': '10px', 'display': 'block'}
    except Exception:
        pass
    return {'display': 'none'}

# Fullscreen functionality for home cards
@app.callback(
    [
        Output("purpose-card", "style"),
        Output("language-card", "style"),
        Output("source-card", "style"),
        Output("faq-card", "style"),
        Output("home-fullscreen-card", "data"),
    ],
    [
        Input("purpose-fullscreen-btn", "n_clicks"),
        Input("language-fullscreen-btn", "n_clicks"),
        Input("source-fullscreen-btn", "n_clicks"),
        Input("faq-fullscreen-btn", "n_clicks"),
        Input("theme-store", "data"),
    ],
    State("home-fullscreen-card", "data"),
)
def fullscreen_home_card(
    purpose_click, language_click, source_click, faq_click, theme, fullscreen_card
):
    ctx_triggered = ctx.triggered_id
    card_ids = ["purpose", "language", "source", "faq"]
    card_bg = THEMES[theme]["card"]
    # Default card font size
    base_font_size = '1em'
    fullscreen_font_size = '2em'
    card_styles = [
        {'width': '46%', 'height': '46%', 'backgroundColor': card_bg, 'borderRadius': '10px', 'padding': '30px', 'margin': '2%', 'boxSizing': 'border-box', 'position': 'absolute', 'top': '0', 'left': '0', 'transition': 'all 0.3s', 'fontSize': base_font_size},
        {'width': '46%', 'height': '46%', 'backgroundColor': card_bg, 'borderRadius': '10px', 'padding': '30px', 'margin': '2%', 'boxSizing': 'border-box', 'position': 'absolute', 'top': '0', 'right': '0', 'transition': 'all 0.3s', 'fontSize': base_font_size},
        {'width': '46%', 'height': '44%', 'backgroundColor': card_bg, 'borderRadius': '10px', 'padding': '30px', 'margin': '2%', 'boxSizing': 'border-box', 'position': 'absolute', 'bottom': '0', 'left': '0', 'transition': 'all 0.3s', 'fontSize': base_font_size},
        {'width': '46%', 'height': '44%', 'backgroundColor': card_bg, 'borderRadius': '10px', 'padding': '30px', 'margin': '2%', 'boxSizing': 'border-box', 'position': 'absolute', 'bottom': '0', 'right': '0', 'transition': 'all 0.3s', 'fontSize': base_font_size},
    ]
    fullscreen_style = {
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'width': '100vw',
        'height': '100vh',
        'zIndex': 1000,
        'backgroundColor': card_bg,
        'borderRadius': '0px',
        'padding': '40px',
        'margin': '0',
        'boxSizing': 'border-box',
        'overflowY': 'auto',
        'transition': 'all 0.3s',
        'fontSize': fullscreen_font_size
    }
    if ctx_triggered in [
        "purpose-fullscreen-btn",
        "language-fullscreen-btn",
        "source-fullscreen-btn",
        "faq-fullscreen-btn",
    ]:
        idx = [
            "purpose-fullscreen-btn",
            "language-fullscreen-btn",
            "source-fullscreen-btn",
            "faq-fullscreen-btn",
        ].index(ctx_triggered)
        if fullscreen_card == card_ids[idx]:
            return [card_styles[0], card_styles[1], card_styles[2], card_styles[3], None]
        else:
            styles = []
            for i in range(4):
                if i == idx:
                    styles.append(fullscreen_style)
                else:
                    styles.append({**card_styles[i], 'zIndex': 0, 'opacity': 0.1, 'pointerEvents': 'none'})
            return [*styles, card_ids[idx]]
    if fullscreen_card in card_ids:
        idx = card_ids.index(fullscreen_card)
        styles = []
        for i in range(4):
            if i == idx:
                styles.append(fullscreen_style)
            else:
                styles.append({**card_styles[i], 'zIndex': 0, 'opacity': 0.1, 'pointerEvents': 'none'})
        return [*styles, fullscreen_card]
    return [card_styles[0], card_styles[1], card_styles[2], card_styles[3], None]

if __name__ == '__main__':
    app.run(debug=False,host="0.0.0.0")