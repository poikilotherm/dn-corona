import requests
import lxml.html as lh
import json
from datetime import datetime, timedelta
import calendar
from dateutil.rrule import DAILY, rrule, MO, TU, WE, TH, FR

def daterange(start_date, end_date):
  return rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR))

def parseHTMLTable(doc, date):
    # Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')
    # 24 comes from the rows with the data + some contact numbers
    if (len(tr_elements) == 24):
        # Actual data we want is in rows 1 to 17 (0 = header, rest = contacts)
        datarows = tr_elements[1:17]
        for row in datarows:
            # Get location and cases
            location = row[0].text_content() # loc in first column
            cases = row[2].text_content() # alltime positive cases in third column

            # Get location key from text content
            if (location in map_names_to_towns):
                town = map_names_to_towns[location]
            else:
                print("Could not find a valid town for location \""+location+"\".")
                return False

            # Insert into dict of total cases
            data[town]["data"].append({"date": date.strftime("%Y-%m-%d"), "total_cases": cases})




baseurls = [
  'https://www.kreis-dueren.de/presse/2021/corona_{year}-{month}-{day}.php',
  'https://www.kreis-dueren.de/presse/2021/Corona_{year}-{month}-{day}.php',
  'https://www.kreis-dueren.de/presse/2021/Corona_{day}{month}.php'
]
start_date = datetime(2021, 4, 20)
end_date = datetime.now() - timedelta(1) # = yesterday
weekdays = daterange(start_date, end_date)

map_names_to_towns = {
  "Aldenhoven": "aldenhoven",
  "Düren": "dueren",
  "Dueren": "dueren",
  "Stadt Düren": "dueren",
  "Stadt Dueren": "dueren",
  "Düren (Stadt)": "dueren",
  "Heimbach": "heimbach",
  "Hürtgenwald": "huertgenwald",
  "Huertgenwald": "huertgenwald",
  "Inden": "inden",
  "Jülich": "juelich",
  "Juelich": "juelich",
  "Kreuzau": "kreuzau",
  "Langerwehe": "langerwehe",
  "Linnich": "linnich",
  "Merzenich": "merzenich",
  "Nideggen": "nideggen",
  "Niederzier": "niederzier",
  "Noervenich": "noervenich",
  "Nörvenich": "noervenich",
  "Titz": "titz",
  "Vettweiß": "vettweiss",
  "Kreis Düren": "kreis",
  "Düren (Kreis)": "kreis"
}

# Population data based on reference date 2020-06-30
# https://www.it.nrw/statistik/eckdaten/bevoelkerung-nach-gemeinden-93051
data = {
    "aldenhoven": {"population": 13790, "data": []},
    "dueren": {"population": 91123, "data": []},
    "heimbach": {"population": 4291, "data": []},
    "huertgenwald": {"population": 8687, "data": []},
    "inden": {"population": 7419, "data": []},
    "juelich": {"population": 32460, "data": []},
    "kreuzau": {"population": 17471, "data": []},
    "langerwehe": {"population": 14051, "data": []},
    "linnich": {"population": 12725, "data": []},
    "merzenich": {"population": 9917, "data": []},
    "nideggen": {"population": 10132, "data": []},
    "niederzier": {"population": 14208, "data": []},
    "noervenich": {"population": 10602, "data": []},
    "titz": {"population": 8513, "data": []},
    "vettweiss": {"population": 9470, "data": []},
    "kreis": {"population": 264859, "data": []}
}

# Get and parse all data from Kreis Düren website
for date in weekdays:
    # Try all the different patterns for URLs in use...
    for baseurl in baseurls:
        url = baseurl.format(year = date.strftime("%Y"), month = date.strftime("%m"), day = date.strftime("%d"))

        # Try to fetch the page
        page = requests.get(url)
        if (page.status_code == 200):
            break

    # Could not find a page for the date although we tried our best.
    if (page.status_code == 404):
        print("Could not find a page for date "+date.strftime("%Y-%m-%d"))

    print(page.url)

    # Store the contents of the website under doc
    doc = lh.fromstring(page.content)

    ### 1. attempt: get a HTML table with the data inside
    parseHTMLTable(doc, date)

# Create JSON
with open("data.json", "w") as outfile:
   json.dump(data, outfile, indent=4, default=str)
