import random
import json

import telebot
from telebot import types

bot = telebot.TeleBot('5601099296:AAGfTFBOSZb7oFKTE-gEib7Fdc6UNBXS3gU')

users = {}
class User(object):
	cities = []
	def __init__(self, currentBotCity, score, fails):
		self.currentBotCity = currentBotCity
		self.score = score
		self.fails = fails
		self.cities.append(currentBotCity)

def menu(message):
		keyboard = types.InlineKeyboardMarkup()

		key_start = types.InlineKeyboardButton(text='Старт', callback_data='newgame')
		keyboard.add(key_start)

		key_help = types.InlineKeyboardButton(text='Правила игры', callback_data='gamerules')
		keyboard.add(key_help)

		bot.send_message(message.chat.id, text='Привет, я бот для игры в города!\nНажми кнопку "Старт", чтобы начать игру!\nИли нажми кнопку "Правила игры", чтобы узнать правила.', reply_markup=keyboard)

def rules(message):
	keyboard = types.InlineKeyboardMarkup()

	key_start = types.InlineKeyboardButton(text='Старт', callback_data='newgame')
	keyboard.add(key_start)

	key_help = types.InlineKeyboardButton(text='В меню', callback_data='back')
	keyboard.add(key_help)
	rulesMsg = "Правила игры:"+"\n1. Бот загадывает любой город России,"+"\n2. Напишите в ответ город, начинающийся с последней буквы этого города,"+"\n3. Если не знаете название города на эту букву, нажмите кнопку пропустить и бот загадает новое слово,"+"\n4. Если вы ошибаетесь 3 раза при загадывании города - игра заканчивается,"+"\n5. Города не должны повторяться,"+"\n6. Если город заканчивается на букву: ь, ъ или ы, нужно загадывать город на предпоследнюю букву."

	bot.send_message(message.chat.id, text=rulesMsg, reply_markup=keyboard)

def backmenu(call):
		keyboard = types.InlineKeyboardMarkup()

		key_start = types.InlineKeyboardButton(text='Старт', callback_data='newgame')
		keyboard.add(key_start)

		key_help = types.InlineKeyboardButton(text='Правила игры', callback_data='gamerules')
		keyboard.add(key_help)

		bot.send_message(call.message.chat.id, text='Привет, я бот для игры в города!\nНажми кнопку "Старт", чтобы начать игру!\nИли нажми кнопку "Правила игры", чтобы узнать правила.', reply_markup=keyboard)

@bot.message_handler(commands=["start"])
def send_command(message):
		menu(message)

@bot.message_handler(commands=["rules"])
def send_command(message):
		rules(message)


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
	global users
	if call.data == "newgame":
		keyboard = types.InlineKeyboardMarkup()
		key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
		keyboard.add(key_skip)

		key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
		keyboard.add(key_end)

		cities = []
		pathFile = 'russian-cities.json'
		with open(pathFile, 'r', encoding='utf-8') as f:
			cities = json.load(f)
		randomCity = cities[random.randint(0, len(cities))]['name']
		user = User(randomCity, 0, 0)
		users[call.from_user.id] = user
		bot.send_message(call.message.chat.id, text=randomCity, reply_markup=keyboard)
		print('User {} started the game'.format(call.from_user.id))

	if call.data == "gamerules":
		keyboard = types.InlineKeyboardMarkup()

		key_start = types.InlineKeyboardButton(text='Старт', callback_data='newgame')
		keyboard.add(key_start)

		key_help = types.InlineKeyboardButton(text='В меню', callback_data='back')
		keyboard.add(key_help)
		rulesMsg = "Правила игры:"+"\n1. Бот загадывает любой город России,"+"\n2. Напишите в ответ город, начинающийся с последней буквы этого города,"+"\n3. Если не знаете название города на эту букву, нажмите кнопку пропустить и бот загадает новое слово,"+"\n4. Если вы ошибаетесь 3 раза при загадывании города - игра заканчивается,"+"\n5. Города не должны повторяться,"

		bot.send_message(call.message.chat.id, text=rulesMsg, reply_markup=keyboard)

	if call.data == "back":
		backmenu(call)
	if call.data == "skip":
		keyboard = types.InlineKeyboardMarkup()
		key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
		keyboard.add(key_skip)

		key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
		keyboard.add(key_end)
		try:
			user = users[call.from_user.id]
			cities = []
			pathFile = 'russian-cities.json'
			with open(pathFile, 'r', encoding='utf-8') as f:
				cities = json.load(f)

			isFound = False
			for city in cities:
				if city['name'].startswith(user.currentBotCity[-1].capitalize()) and city['name'] not in user.cities:
					user.currentBotCity = city['name']
					user.cities.append(city['name'])
					isFound = True
					break
			if isFound == False:
				while(True):
					randomCity = cities[random.randint(0, len(cities))]['name']
					if randomCity not in user.cities:
						break
				user.currentBotCity = randomCity
				user.cities.append(randomCity)

				users[call.from_user.id] = user
				bot.send_message(call.message.chat.id, text=user.currentBotCity, reply_markup=keyboard)
			else:
				users[call.from_user.id] = user
				bot.send_message(call.message.chat.id, text=user.currentBotCity, reply_markup=keyboard)
			print('User {} missed the word'.format(call.from_user.id))
		except:
			backmenu(call)
	if call.data == "endgame":
		try:
			user = users[call.from_user.id]
			mes = 'Игра окончена!\nИтоговый счет: {} городов'.format(user.score)
			users.pop(call.from_user.id)
			
			keyboard = types.InlineKeyboardMarkup()

			key_start = types.InlineKeyboardButton(text='Начать сначала', callback_data='newgame')
			keyboard.add(key_start)

			key_end = types.InlineKeyboardButton(text='В меню', callback_data='back')
			keyboard.add(key_end)
			bot.send_message(call.message.chat.id, text=mes, reply_markup=keyboard)
			print('User {} completed the game'.format(call.from_user.id))
		except:
			backmenu(call)

@bot.message_handler(content_types=["text"])
def user_answer(message):
	global users

	cities = []
	citiesJson = []
	pathFile = 'russian-cities.json'
	with open(pathFile, 'r', encoding='utf-8') as f: #открыли файл
		citiesJson = json.load(f)

	for city in citiesJson:
		cities.append(city['name'])

	try:
		keyboard = types.InlineKeyboardMarkup()

		user = users[message.from_user.id]
		if message.text in cities:
			chars = ["ь", "ъ", "ы"]
			if user.currentBotCity[-1] not in chars:
				if message.text.startswith((user.currentBotCity[-1].capitalize(), user.currentBotCity[-1])):
					if(message.text in user.cities):
						user.fails = int(user.fails) + 1
						if(int(user.fails) == 3):	
							mes = 'Игра окончена!\nИтоговый счет: {} городов'.format(user.score)
							users.pop(message.from_user.id)

							key_start = types.InlineKeyboardButton(text='Начать сначала', callback_data='newgame')
							keyboard.add(key_start)

							key_end = types.InlineKeyboardButton(text='В меню', callback_data='back')
							keyboard.add(key_end)
						else:
							key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
							keyboard.add(key_skip)

							key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
							keyboard.add(key_end)

							users[message.from_user.id] = user
							mes = 'Такой город уже был\nКоличество ошибок: {}/3\nТекущее слово: "{}"'.format(user.fails, user.currentBotCity)
						bot.send_message(message.chat.id, text=mes, reply_markup=keyboard)
					else:
						key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
						keyboard.add(key_skip)

						key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
						keyboard.add(key_end)
						user.cities.append(message.text)
						isFound = False
						if message.text[-1] not in chars:
							for city in cities:
								if city.startswith(message.text[-1].capitalize()) and city not in user.cities:
									user.currentBotCity = city
									user.cities.append(city)
									isFound = True
									break
						else:
							for city in cities:
								if city.startswith(message.text[-2].capitalize()) and city not in user.cities:
									user.currentBotCity = city
									user.cities.append(city)
									isFound = True
									break
						if isFound == False:
							while(True):
								randomCity = cities[random.randint(0, len(cities))]
								if randomCity not in user.cities:
									break
							user.currentBotCity = randomCity
							user.cities.append(randomCity)

						user.score = int(user.score) + 1
						users[message.from_user.id] = user
						bot.send_message(message.chat.id, text=user.currentBotCity, reply_markup=keyboard)
				else:
					user.fails = int(user.fails) + 1
					if(int(user.score) == 3):	
						mes = 'Игра окончена!\nИтоговый счет: {} городов'.format(user.score)
						users.pop(message.from_user.id)

						key_start = types.InlineKeyboardButton(text='Начать сначала', callback_data='newgame')
						keyboard.add(key_start)

						key_end = types.InlineKeyboardButton(text='В меню', callback_data='back')
						keyboard.add(key_end)
					else:
						key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
						keyboard.add(key_skip)

						key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
						keyboard.add(key_end)
						users[message.from_user.id] = user
						mes = 'Город должен начинаться с последней буквы\nКоличество ошибок: {}/3\nТекущее слово: "{}"'.format(user.fails, user.currentBotCity)
					bot.send_message(message.chat.id, text=mes, reply_markup=keyboard)
			else:
				if message.text.startswith((user.currentBotCity[-2].capitalize(), user.currentBotCity[-2])):
					if(message.text in user.cities):
						user.fails = int(user.fails) + 1
						if(int(user.fails) == 3):	
							mes = 'Игра окончена!\nИтоговый счет: {} городов'.format(user.score)
							users.pop(message.from_user.id)

							key_start = types.InlineKeyboardButton(text='Начать сначала', callback_data='newgame')
							keyboard.add(key_start)

							key_end = types.InlineKeyboardButton(text='В меню', callback_data='back')
							keyboard.add(key_end)
						else:
							key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
							keyboard.add(key_skip)

							key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
							keyboard.add(key_end)

							users[message.from_user.id] = user
							mes = 'Такой город уже был\nКоличество ошибок: {}/3\nТекущее слово: "{}"'.format(user.fails, user.currentBotCity)
						bot.send_message(message.chat.id, text=mes, reply_markup=keyboard)
					else:
						key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
						keyboard.add(key_skip)

						key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
						keyboard.add(key_end)
						user.cities.append(message.text)
						isFound = False
						if message.text[-1] not in chars:
							for city in cities:
								if city.startswith(message.text[-1].capitalize()) and city not in user.cities:
									user.currentBotCity = city
									user.cities.append(city)
									isFound = True
									break
						else:
							for city in cities:
								if city.startswith(message.text[-2].capitalize()) and city not in user.cities:
									user.currentBotCity = city
									user.cities.append(city)
									isFound = True
									break							
						if isFound == False:
							while(True):
								randomCity = cities[random.randint(0, len(cities))]
								if randomCity not in user.cities:
									break
							user.currentBotCity = randomCity
							user.cities.append(randomCity)

						user.score = int(user.score) + 1
						users[message.from_user.id] = user
						bot.send_message(message.chat.id, text=user.currentBotCity, reply_markup=keyboard)
				else:
					user.fails = int(user.fails) + 1
					if(int(user.score) == 3):	
						mes = 'Игра окончена!\nИтоговый счет: {} городов'.format(user.score)
						users.pop(message.from_user.id)

						key_start = types.InlineKeyboardButton(text='Начать сначала', callback_data='newgame')
						keyboard.add(key_start)

						key_end = types.InlineKeyboardButton(text='В меню', callback_data='back')
						keyboard.add(key_end)
					else:
						key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
						keyboard.add(key_skip)

						key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
						keyboard.add(key_end)
						users[message.from_user.id] = user
						mes = 'Город должен начинаться с последней буквы\nКоличество ошибок: {}/3\nТекущее слово: "{}"'.format(user.fails, user.currentBotCity)
					bot.send_message(message.chat.id, text=mes, reply_markup=keyboard)
		else:
			user.fails = int(user.fails) + 1
			if(int(user.fails) == 3):	
				mes = 'Игра окончена!\nИтоговый счет: {} городов'.format(user.score)
				users.pop(message.from_user.id)

				key_start = types.InlineKeyboardButton(text='Начать сначала', callback_data='newgame')
				keyboard.add(key_start)

				key_end = types.InlineKeyboardButton(text='В меню', callback_data='back')
				keyboard.add(key_end)
			else:
				key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='skip')
				keyboard.add(key_skip)

				key_end = types.InlineKeyboardButton(text='Закончить игру', callback_data='endgame')
				keyboard.add(key_end)

				users[message.from_user.id] = user
				mes = 'Такого города не существует\nКоличество ошибок: {}/3\nТекущее слово: "{}"'.format(user.fails, user.currentBotCity)
			bot.send_message(message.chat.id, text=mes, reply_markup=keyboard)
	except:
		keyboard = types.InlineKeyboardMarkup()

		key_start = types.InlineKeyboardButton(text='Старт', callback_data='newgame')
		keyboard.add(key_start)

		key_help = types.InlineKeyboardButton(text='Правила игры', callback_data='gamerules')
		keyboard.add(key_help)

		bot.send_message(message.chat.id, text='Вы еще не начали игру. Нажмите "Старт"', reply_markup=keyboard)
	
	

bot.polling(none_stop=True, interval=0)