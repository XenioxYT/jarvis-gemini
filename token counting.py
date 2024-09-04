# Testing tools
from tools import Tools

print (Tools.get_news(headlines_only=True))

print(Tools.get_place_information("The five swans"))

print(Tools.get_weather("Newcastle upon tyne"))

print(Tools.get_directions("Newcastle upon tyne", "London"))

print(Tools.take_notes(notes = "I am testing the notes tool"))

print(Tools.google_search("I am testing the google search tool"))

print(Tools.send_message_to_phone("1234", "I am testing the send message to phone tool"))
