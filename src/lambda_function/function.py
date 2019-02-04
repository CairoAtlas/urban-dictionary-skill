import requests
import json
import logging.config

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

RANDOM_URL = 'http://api.urbandictionary.com/v0/random'
WOD_URL = 'http://urban-word-of-the-day.herokuapp.com/today'


# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(output):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': True
    }


def build_response(speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': {},
        'response': speechlet_response
    }


def random_definition():
    urban_dictionary_response = requests.get(RANDOM_URL)
    urban_json = json.loads(urban_dictionary_response.text)
    urban_word = get_most_liked_word(urban_json)
    if urban_word is None:
        return build_response(build_speechlet_response('No Random words found'))

    speech_output = str(urban_word['word']) + '... ' + str(urban_word['definition']) + \
                    '... Here is the word used in an example. ' + str(urban_word['example'])

    speech_output = speech_output.replace('[', '')
    speech_output = speech_output.replace(']', '')

    return build_response(build_speechlet_response(speech_output))


def get_word_of_day():
    urban_dictionary_response = requests.get(WOD_URL)
    urban_json = json.loads(urban_dictionary_response.text)
    speech_output = str(urban_json['word']) + '... ' + str(urban_json['meaning']) + \
                    '... Here is the word used in an example. ' + urban_json['example']

    return build_response(build_speechlet_response(speech_output))


def get_most_liked_word(urban_dictionary_response):
    word = Nonesetup.py
    previous_item = None
    for item in urban_dictionary_response['list']:
        if previous_item is None:
            previous_item = item
        elif int(item['thumbs_up']) > int(previous_item['thumbs_up']):
            word = item
            previous_item = item

    return word


def on_intent(intent_request, session):
    LOG.info("on_intent requestId=" + intent_request['requestId'] +
             ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "RandomIntent":
        return random_definition()
    if intent_name == 'WordOfDayIntent':
        return get_word_of_day()
    else:
        raise ValueError("Invalid intent")


# --------------- Main handler ------------------
def handler(event, context):
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.52d41acb-c4a5-4c58-b097-5e59839aa173"):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
