from django.http import HttpResponseRedirect, HttpResponse
from pffl.models import CredentialsModel

# GOOGLE AUTHENTICATION
import os
import httplib2
from apiclient import discovery
from oauth2client import client
from django.conf import settings
from oauth2client.contrib import xsrfutil
from oauth2client.contrib.django_util import storage

REDIRECT_URI = settings.GOOGLE_OAUTH2_CALLBACK_URL
# REDIRECT_URI = 'https://pffl.herokuapp.com/oauth2callback'
FLOW = client.flow_from_clientsecrets(
    settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
    scope='https://www.googleapis.com/auth/spreadsheets',
    redirect_uri=REDIRECT_URI)

def authorize_google(step, request):
    if step==1:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                        request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    if step==2:
        if not xsrfutil.validate_token(settings.SECRET_KEY, str(request.GET.__getitem__('state')),
                                     request.user):
            return  False
        if request.GET.__contains__('error'):
            return False
        credential = FLOW.step2_exchange(request.GET)
        storage.DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential').put(credential)
        return True
    return False

def is_authorized(request):
    credential = storage.DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential').get()
    if credential is None or credential.invalid == True:
        return False
    return True

def get_credentials(request):
    credential = storage.DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential').get()
    return credential.authorize(httplib2.Http())

def get_spreadsheet_id(url):
    return (url.split('/d/'))[1].split('/')[0]

def get_sheet(http, url, rangeName):
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
        'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    spreadsheetId = get_spreadsheet_id(url)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return False
    else:
        return values



##### WRITE #####

def create_google_color(r,g,b):
    red = 255-r
    green = 255-g
    blue = 255-b

    if red == 0:
        red = 1.0
    if green == 0:
        green = 1.0
    if blue == 0:
        blue = 1.0

    color = {
        "red": red,
        "green": green,
        "blue": blue
    }
    return color

def create_header_cell(value, center="LEFT"):
    cell = {
        "userEnteredValue": {"stringValue": str(value).upper()},
        "userEnteredFormat": {
            "backgroundColor": create_google_color(217,217,217),
            "horizontalAlignment" : center,
            "textFormat": {
                "foregroundColor": {
                    "red": 0,
                    "green": 0,
                    "blue": 0
                },
                "bold": True
            }
        },
    }
    return cell

def create_body_cell(value, backgroundColor, foregroundColor, center="LEFT"):
    cell = {
        "userEnteredValue": {"stringValue": str(value).upper()},
        "userEnteredFormat": {
            "backgroundColor": backgroundColor,
            "horizontalAlignment" : center,
            "textFormat": {
                "foregroundColor": foregroundColor
            }
        },
    }
    return cell

def get_header_row(total):
    row = [
        create_header_cell('team'),
        create_header_cell('conferance'),
        create_header_cell('division'),
        create_header_cell('rank')
    ]
    for match in range(1, total+1):
        row.append(create_header_cell('match '+str(match)))
    return { "values": row }

def get_body_row(row_data):
    non_con = create_google_color(143,201,66)
    non_div = create_google_color(72,195,207)
    in_div = create_google_color(201,125,245)
    white = create_google_color(255,255,255)
    black = create_google_color(0,0,0)

    fg = black
    bg = white

    row = []
    for cell in row_data:
        if cell['format'] == 'in_div':
            bg = in_div
            fg = white
        elif cell['format'] == 'non_div':
            bg = non_div
            fg = white
        elif cell['format'] == 'non_con':
            bg = non_con
            fg = white
        else:
            bg = white
            fg = black
        row.append(create_body_cell(cell['value'], bg, fg))
    return { "values": row }

def get_body(data):
    rows = []
    for row in data:
        rows.append(get_body_row(row))
    return rows

def create_sheet(http, data, schedule):
    service = discovery.build('sheets', 'v4', http=http)
    title = "[" + schedule.season + ", " + str(schedule.year) + "] " + schedule.name
    body = { 'properties': { 'title': title } }
    spreadsheetId = service.spreadsheets().create(body=body).execute().get('spreadsheetId')

    requests = []

    # header
    requests.append({
      "updateCells": {
        "start": {
          "sheetId": 0,
          "rowIndex": 0,
          "columnIndex": 0
        },
        "rows": [ get_header_row(schedule.total) ],
        "fields": "userEnteredValue,userEnteredFormat(backgroundColor,textFormat,horizontalAlignment),"
      }
    })

    # body
    requests.append({
      "updateCells": {
        "start": {
          "sheetId": 0,
          "rowIndex": 1,
          "columnIndex": 0
        },
        "rows": get_body(data),
        "fields": "userEnteredValue,userEnteredFormat(backgroundColor,textFormat,horizontalAlignment),"
      }
    })

    body = { 'requests': requests }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()