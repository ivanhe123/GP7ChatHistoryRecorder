import dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly
from selenium import webdriver
import threading
from bs4 import BeautifulSoup
import plotly.graph_objs as go
statistics = {"NaN":0}
def runi():
    global statistics

    driver = webdriver.Edge()

    driver.get('https://www.pottersschool.org/gp7/#/login')

    length = 0
    length1 = 0
    tmp = 0
    tmp1=0
    html = driver.page_source

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all divs with class 'PUBLIC ng-star-inserted'
    divs = soup.find_all('div', {'class': 'l-chat-history'})
    names = soup.find_all('tr',{'class': 'ng-star-inserted'})
    while len(divs)==0 or len(names)==0:
        html = driver.page_source

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div', {'class': 'l-chat-history'})
    

    while True:
        # Get page source
        html = driver.page_source

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all divs with class 'PUBLIC ng-star-inserted'
        divs = soup.find_all('div', {'class': 'PUBLIC ng-star-inserted'})
        length = len(divs)
        names = soup.find_all('tr',{'class': 'ng-star-inserted'})
        for ns in names:
            finded = ns.find("span")
            if finded:
                name_x= finded.text.strip()
                if name_x not in statistics:
                    statistics[name_x] = 0
        if tmp != length:
            try:
                div = divs[length]
            except:
                div = divs[length - 1]
            # Find spans within div
            user_span = div.find('span', {'class': 'chat-msg-from ng-star-inserted'})
            text_span = div.find('span', {'class': 'chat-msg-text'})

            # Check if both spans are found
            if user_span and text_span:
                # Record username and message text
                username = user_span.text.strip()
                message_text = text_span.text.strip()

                statistics[username.replace(":", "")] += 1
        tmp = length
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals=0
        ),
    ]
)


@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(n):
    # Get page source
    X = list(statistics.keys())
    Y = list(statistics.values())

    data = plotly.graph_objs.Bar(
        x=list(statistics.keys()),
        y=list(statistics.values()),
        name="Messages Sent"
    )

    return {'data': [data],
            'layout': go.Layout(xaxis=dict(range=[0, len(X)]), yaxis=dict(range=[0, max(Y, default=0)]), )}


if __name__ == '__main__':

    choice1 = input("Do you want to load a student list file? [Y/n]")
    if choice1.lower() == 'n':
        print("Please enter your students' firstname one at a line. Please also enter your first name. Then, press Enter two times.")
        while True:
            n = input()
            if n == "":
                break
            statistics[n] = 0
        choice = input("Do you want to save this student list into a file? [Y/n]")
        if choice.lower() == 'y':
            name = input("Filename:")
            open(name, 'w').writelines(list(statistics.keys()))
    else:
        name = input("Filename:")
        students = open(name, 'r').readlines()
        for x in students:
            statistics[x.replace("\n","")] = 0
    t=threading.Thread(target=runi)
    t.start()

    app.run_server()
    t.join()
