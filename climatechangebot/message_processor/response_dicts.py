"""
    Various response dictionaries we use in the message processor

"""

# Dictionary of random GIFs we will send the user
gif_dict = {
    'TEMPERATURE': [
        'https://media.giphy.com/media/hPovBcQ3c1g9W/giphy.gif',
        'https://media.giphy.com/media/9u7xpfvuzD89W/giphy.gif',
        'https://media.giphy.com/media/xTiTnpsAMlk0pJMFd6/giphy.gif'
    ],
}

# Facebook stickers send as image payloads, so we need to map certain sticker ids to text responses
#   the default sticker response is a thumbs up
# sticker_dict = {
#     369239263222822: 'thumbs_up',
#     369239343222814: 'thumbs_up'
# }

sticker_response = {
    'thumbs_up': u'\U0001F44D'
}
