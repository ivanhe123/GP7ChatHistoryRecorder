import dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly
from selenium import webdriver
import threading
from bs4 import BeautifulSoup
import plotly.graph_objs as go
statistics = {}
words={}
words_counts={}
avg={}
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
        names = soup.find_all('tr', {'class': 'ng-star-inserted'})

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
                    words[name_x] = 0
                    avg[name_x] = 0
                    words_counts[name_x]=0
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
                print(len(message_text.split(" ")), statistics[username.replace(":", "")])
                words[username.replace(":", "")] += len(message_text.split(" "))
                avg[username.replace(":","")] = words[username.replace(":", "")]/statistics[username.replace(":", "")]

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
    X = list(statistics.values())
    Y = list(statistics.values())

    data = plotly.graph_objs.Bar(
        x=list(statistics.keys()),
        y=list(statistics.values()),
        name="Messages Sent"
    )
    data1 = plotly.graph_objs.Bar(
        x=list(statistics.keys()),
        y=list(avg.values()),
        name="Average Message Length"
    )
    return {'data': [data,data1],
            'layout': go.Layout(xaxis=dict(range=[0, len(X)]), yaxis=dict(range=[0, max(Y+list(avg.values()), default=0)]), )}

if __name__ == '__main__':
    t=threading.Thread(target=runi)
    t.start()

    app.run_server()
    t.join()
