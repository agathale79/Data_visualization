from mmap import PROT_EXEC
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np


from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from datetime import date
import plotly.express as px 
import plotly.io as pio


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Daily Job Dashboard"
server = app.server


# Plotly mapbox public token
# mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

# Dictionary of important lifecycle 
list_of_lifecycle = {
    "Production": "P",
    "Quality Control": "Q",
    "Development": "D",
    "-- All Lifecycle --": "ALL"
}

# Dictionary of important job type
list_of_jobtype = {
    "XFM": "XFM",
    "XFM Table Level": "XFM-TAB",
    "VC Batch": "VCB",
    "VC": "VC",
    "Inform": "INFORM",
    "Inform Subjob": "INFORM_SUB",
    "-- All Job Types --": "ALL"
}

# Initialize data frame
df1 = pd.read_csv(
    "finalpocjobdata_0525_1.csv",
    dtype=object,
)

df1['year']  = df1['year'].astype('int')
df1['month'] = df1['month'].astype('int')
df1['day'] = df1['day'].astype('int')
df1['hour'] = df1['hour'].astype('int')
df1['mins'] = df1['mins'].astype('int')
df1['time_taken_sec'] = df1['time_taken_sec'].astype('float')
df1['master_total_time'] = df1['master_total_time'].astype('float')
df1['master_sch_total'] = df1['master_sch_total'].astype('float')
df1['number_of_tables'] = df1['number_of_tables'].astype('int')
df1['row_refreshed'] = df1['row_refreshed'].astype('int')
df1['row_inserted'] = df1['row_inserted'].astype('int')
df1['row_updated'] = df1['row_updated'].astype('int')
df1['row_deleted'] = df1['row_deleted'].astype('int')
df1['number_of_subjob'] = df1['number_of_subjob'].astype('int')
df1['ava_si'] = df1['ava_si'].astype('int')
df1['job_id'] = df1['job_id'].astype('int')
df1['master_job_id'] = df1['master_job_id'].astype('int')
df1['master_sch_job_id'] = df1['master_sch_job_id'].astype('int')



df = df1.copy()
df["Date/Time"] = pd.to_datetime(df["exec_start_time"], format="%m/%d/%y %H:%M")
df.index = df["Date/Time"]
df.drop("Date/Time", 1, inplace=True)
totalList = []

def getDataforlc(dataset, lifecycle):
    if lifecycle is None:
        lc='ALL'
    else:
        lc= list_of_lifecycle[lifecycle]

    if lc=='ALL':
        df_1=dataset.copy()
    else:
        df_1 = dataset[dataset["lifecycle"] ==lc].copy() 
    
    return df_1

def getDataforjobtype(dataset, jobtype):
    if jobtype is None:
        jt='ALL'
    else:
        jt= list_of_jobtype[jobtype]


    if jt=='ALL':
        df_1=dataset.copy()
    else:
        df_1 = dataset[dataset["job_type"] ==jt].copy() 
    
    return df_1

def setData(lifecycle,df1):
    totalList = []
    df_1= getDataforlc(df1,lifecycle)
    df_1["Date/Time"] = pd.to_datetime(df_1["exec_start_time"], format="%m/%d/%y %H:%M")
    df_1.index = df_1["Date/Time"]
    df_1.drop("Date/Time", 1, inplace=True)
    for month in df_1.groupby(df_1.index.month):
        dailyList = []
        for day in month[1].groupby(month[1].index.day):
            dailyList.append(day[1])
        totalList.append(dailyList)
    #totalList = np.array(totalList)

    return totalList

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="two columns div-user-controls",
                    children=[
                        html.H2("Job Dashboard"),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2021, 2, 2) ,
                                    max_date_allowed=dt(2021,7,31),
                                    initial_visible_month=dt(2021,2,2),
                                    date=dt(2021,2,2).date(),
                                    display_format="MM/DD/YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for lifecycle on map
                                        dcc.Dropdown(
                                            id="lifecycle-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_lifecycle
                                            ],
                                            value="-- All Lifecycle --",
                                            placeholder="-- All Lifecycle --",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for Job Type on map
                                        dcc.Dropdown(
                                            id="job-type",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_jobtype
                                            ],
                                            value="-- All Job Types --",
                                            placeholder="-- All Job Types ---",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": str(n),
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select certain hours",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.P(id="total-jobs"),
                        html.P(id="total-jobs-selection"),
                        html.P(id="date-value"),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="ten columns div-for-charts bg-grey",
                    children=[
                        html.Div([
                            html.Div(
                                className="four columns div-for-charts bg-grey",
                                children=[
                                    dcc.Graph(id="pie_graph",figure={'data': [{'y': [1, 2, 3]}]})                             
                                ],
                            ),
                            html.Div(
                                className="four columns div-for-charts bg-grey", 
                                children=[                             
                                    dcc.Graph(id="line_graph", figure={'data': [{'y': [1, 2, 3]}]})
                                ],
                            ),                            
                            html.Div(
                                className="four columns div-for-charts bg-grey",
                                children=[
                                    dcc.Graph(id="study_pie_graph",figure={'data': [{'y': [1, 2, 3]}]})                             
                                ],
                            ),

                        ],  className="row"),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any of the bars on the histogram to section data by time."
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        )
    ]
)

# Gets the amount of days in the specified month
# Index represents month (0 is April, 1 is May, ... etc.)
daysInMonth = [28, 31, 30, 31, 30, 31]

# Get index for the specified month in the dataframe
monthIndex = pd.Index(["Feb","Mar","Apr", "May", "June", "July"])

# Get the amount of jobs per hour based on the time selected
# This also higlights the color of the histogram bars based on
# if the hours are selected
def get_selection(month, day, selection,totalList):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of jobs at a particular time
        try:
            val= len(totalList[month][day][totalList[month][day].index.hour == i])
        except:
            val=0
        yVal.append(val)
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]


# Selected Data in the Histogram updates the Values in the Hours selection dropdown menu
@app.callback(
    Output("bar-selector", "value"),
    [
        Input("histogram", "selectedData"), 
        Input("histogram", "clickData")
    ],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update the total number of jobs Tag
@app.callback(Output("total-jobs", "children"),
     [  
         Input("date-picker", "date"),
         Input("lifecycle-dropdown", "value"),
    ])
def update_total_jobs(datePicked,selectedLifecycle):
    totalList=setData(selectedLifecycle,df1)
    date_object = date.fromisoformat(datePicked)
    date_str = date_object.strftime("%m/%d/%y")
    #
    #date_picked = dt.strptime(datePicked, "%m/%d/%y")
    date_picked = dt.strptime(date_str, "%m/%d/%y")
    return "Total Number of jobs: {:,d}".format(
        len(totalList[date_picked.month - 2][date_picked.day - 2])
    )


# Update the total number of jobs in selected times
@app.callback(
    [Output("total-jobs-selection", "children"), Output("date-value", "children")],
    [   
        Input("date-picker", "date"), 
        Input("bar-selector", "value"),
        Input("lifecycle-dropdown", "value"),
    ],
)
def update_total_jobs_selection(datePicked, selection,selectedLifecycle):
    firstOutput = ""
    totalList=setData(selectedLifecycle,df1)
    if selection is not None or len(selection) !=0:
        date_object = date.fromisoformat(datePicked)
        date_str = date_object.strftime("%m/%d/%y")
        #
        #date_picked = dt.strptime(datePicked, "%m/%d/%y")
        date_picked = dt.strptime(date_str, "%m/%d/%y")
        
        totalInSelection = 0
        for x in selection:
            totalInSelection += len(
                totalList[date_picked.month - 2][date_picked.day - 2][
                    totalList[date_picked.month - 2][date_picked.day - 2].index.hour
                    == int(x)
                ]
            )
        firstOutput = "Total jobs in selection: {:,d}".format(totalInSelection)

    if (
        datePicked is None
        or selection is None
        or len(selection) == 24
        or len(selection) == 0
    ):
        return firstOutput, (datePicked, " - showing hour(s): All")

    holder = sorted([int(x) for x in selection])

    if holder == list(range(min(holder), max(holder) + 1)):
        return (
            firstOutput,
            (
                datePicked,
                " - showing hour(s): ",
                holder[0],
                "-",
                holder[len(holder) - 1],
            ),
        )

    holder_to_string = ", ".join(str(x) for x in holder)
    return firstOutput, (datePicked, " - showing hour(s): ", holder_to_string)

# Update the pie graph
@app.callback(
        Output("pie_graph", "figure"),
    [   
        Input("date-picker", "date"), 
        Input("bar-selector", "value"),
        Input("lifecycle-dropdown", "value"),
        Input("job-type", "value"),
    ],
)

def update_pie_graph(datePicked, selection,selectedLifecycle, jobtype):
    
    xSelected=[]

    df_1=getDataforlc(df1, selectedLifecycle)
    df_1= getDataforjobtype(df_1, jobtype)

    date_object = date.fromisoformat(datePicked)
    date_str = date_object.strftime("%m/%d/%y")
    date_picked = dt.strptime(date_str, "%m/%d/%y")
    
    yearpicked = date_picked.year 
    monthPicked = date_picked.month 
    dayPicked = date_picked.day 

    
    df_1 = df_1[df_1["year"]==yearpicked]
    
    df_1 = df_1[df_1["month"]==monthPicked]
  
    df_1 = df_1[df_1["day"]==dayPicked]

    if selection is not None or len(selection) != 0:    
        # Put selected times into a list of numbers xSelected
        xSelected.extend([int(x) for x in selection])

    if  len(xSelected) :
        df_1= df_1[df_1['hour'].isin(xSelected)]

    piechart = px.pie(data_frame=df_1,
        names="job_type",
        hole=.3,
        )

    piechart.layout.plot_bgcolor="#323130"
    piechart.layout.paper_bgcolor="#323130"
    piechart.layout.font=dict(color="white")
    piechart.layout.title= '<b>Number of Job(s) per Job-Type </b>'
    piechart.update_traces(textposition='inside')
    return piechart


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [   
        Input("date-picker", "date"), 
        Input("bar-selector", "value"),
        Input("lifecycle-dropdown", "value"),
        Input("job-type", "value"),
    ],
)
def update_histogram(datePicked, selection,selectedLifecycle, jobtype):
    df_1= getDataforjobtype(df, jobtype)
    totalList=setData(selectedLifecycle,df_1)
    date_object = date.fromisoformat(datePicked)
    date_str = date_object.strftime("%m/%d/%y")
    #
    #date_picked = dt.strptime(datePicked, "%m/%d/%y")
    date_picked = dt.strptime(date_str, "%m/%d/%y")
    
    monthPicked = date_picked.month - 2
    dayPicked = date_picked.day - 2

    [xVal, yVal, colorVal] = get_selection(monthPicked, dayPicked, selection,totalList)

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )



# Update the line graph Avg time per hour
@app.callback(
        Output("line_graph", "figure"),
    [   
        Input("date-picker", "date"), 
        Input("bar-selector", "value"),
        Input("lifecycle-dropdown", "value"),
        Input("job-type", "value"),
    ],
)

def update_line_graph(datePicked, selection,selectedLifecycle, jobtype):
    xSelected=[]
    df_1=getDataforlc(df1, selectedLifecycle)
    df_1= getDataforjobtype(df_1, jobtype)

    date_object = date.fromisoformat(datePicked)
    date_str = date_object.strftime("%m/%d/%y")
    date_picked = dt.strptime(date_str, "%m/%d/%y")
    
    yearpicked = date_picked.year 
    monthPicked = date_picked.month 
    dayPicked = date_picked.day 

    
    df_1 = df_1[df_1["year"]==yearpicked]
    
    df_1 = df_1[df_1["month"]==monthPicked]
  
    df_1 = df_1[df_1["day"]==dayPicked]

    df_1 = df_1[df_1["MasterJob"]=='N']

    if selection is not None or len(selection) != 0:    
        # Put selected times into a list of numbers xSelected
        xSelected.extend([int(x) for x in selection])

    if  len(xSelected) :
        df_1= df_1[df_1['hour'].isin(xSelected)]

    df_1= df_1.sort_values(by=['hour'])

    aggs = ["count","avg","median","mode","rms","stddev","min","max","first","last","sum",]

    agg = []
    agg_func = []
    for i in range(0, len(aggs)):
        agg = dict(
            args=['transforms[0].aggregations[0].func', aggs[i]],
            label=aggs[i],
            method='restyle'
        )
        agg_func.append(agg)
    

    data = [dict(
    type = 'scatter',
    x = df_1["hour"],
    y = df_1["time_taken_sec"],
    mode = 'bar',
    transforms = [dict(
        type = 'aggregate',
        groups = df_1["hour"],
        aggregations = [dict(
            target = 'y', func = 'avg', enabled = True)
        ]
    )]
    )]

    layout = dict(
    plot_bgcolor="#323130",
    paper_bgcolor="#323130",
    font=dict(color="white"),
    title = '<b>Time taken by jobs to complete per hour </b>      <br>use dropdown to change aggregation',
    xaxis = dict(title = 'Hour'),
    yaxis = dict(title = 'Time Taken in Seconds', range = [0,5000]),
    updatemenus = [dict(
            x = 0.85,
            y = 1.00,
            xref = 'paper',
            yref = 'paper',
            yanchor = 'top',
            active = 1,
            showactive = False,
            buttons = agg_func,
            font=dict(color="white")
    )]
    )

    fig_dict = dict(data=data, layout=layout)
    return fig_dict



# Update the pie graph
@app.callback(
        Output("study_pie_graph", "figure"),
    [   
        Input("date-picker", "date"), 
        Input("bar-selector", "value"),
        Input("lifecycle-dropdown", "value"),
        Input("job-type", "value"),
    ],
)

def update_study_pie_graph(datePicked, selection,selectedLifecycle, jobtype):
    
    xSelected=[]

    df_1=getDataforlc(df1, selectedLifecycle)
    df_1= getDataforjobtype(df_1, jobtype)

    date_object = date.fromisoformat(datePicked)
    date_str = date_object.strftime("%m/%d/%y")
    date_picked = dt.strptime(date_str, "%m/%d/%y")
    
    yearpicked = date_picked.year 
    monthPicked = date_picked.month 
    dayPicked = date_picked.day 

    
    df_1 = df_1[df_1["year"]==yearpicked]
    
    df_1 = df_1[df_1["month"]==monthPicked]
  
    df_1 = df_1[df_1["day"]==dayPicked]

    if selection is not None or len(selection) != 0:    
        # Put selected times into a list of numbers xSelected
        xSelected.extend([int(x) for x in selection])

    if  len(xSelected) :
        df_1= df_1[df_1['hour'].isin(xSelected)]

    piechart = px.pie(data_frame=df_1,
        names="study",
        hole=.3,
        )

    piechart.layout.plot_bgcolor="#323130"
    piechart.layout.paper_bgcolor="#323130"
    piechart.layout.font=dict(color="white")
    piechart.layout.title= '<b>Number of Job(s) per Study </b>'
    piechart.update_traces(textposition='inside')
    return piechart



if __name__ == "__main__":
    app.run_server(debug=True)