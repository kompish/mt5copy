from telethon.sync import TelegramClient

# Use your own values from my.telegram.org
API_ID = '7966550'
API_HASH = 'f987296e9fced34a3bcd4969998826e1'

# The name of your session file
session_name = 'my_session'

# Creating the client and connecting
client = TelegramClient(session_name, API_ID, API_HASH)
test = {}
ppp = []
async def main():
    # Getting all the dialogs (conversations)
    async for dialog in client.iter_dialogs():
        # print(f'{dialog.name}: {dialog.id}')
        test[f'{int(dialog.id)}']= f'{dialog.name}'
        ppp.append(dialog.id)


# Running the client
with client:
    client.loop.run_until_complete(main())

print(test)
print(ppp)

z = [int(str(x)[4:]) for x in ppp]

print(z)