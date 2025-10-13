import requests

def readPositions():

    url = "https://fidelity-investments.p.rapidapi.com/v3/auto-complete"

    querystring = {"q": "apple"}

    headers = {
        "X-RapidAPI-Key": "SIGN-UP-FOR-KEY",
        "X-RapidAPI-Host": "fidelity-investments.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return(True)