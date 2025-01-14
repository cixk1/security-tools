import random

# Generates words with the following
# - first capital/small lettter
# - In sequence add until 4 random numbers appended to the word

print("Please input a word in all small letters without spaces\n")
word = input("Please enter a word: ")
amount = 100
dictionary = []

def big_first_letter(input):
	first_letter = input[0:1]
	result = first_letter.upper() + input[1:]
	return result

def get_numbers():
	range_num = []
	result = []
	for i in range(0, 10):
		range_num.append(i)
	for i in range(0, 4):
		value = random.choice(range_num)
		result.append(str(value))
	return ''.join(result)

def write_to_file(input):
	with open("wordlist.txt", "w") as file:
		for i in range(0, len(dictionary)):
			file.write(input[i] + "\n")

for i in range(0, amount):
	dictionary.append(word + get_numbers())

for i in range(0, len(dictionary)):
	res = big_first_letter(dictionary[i])
	dictionary.append(res)

answer = input("Do you want write to a file (y/n):")
if (answer == "y"):
	write_to_file(dictionary)
	print("\nWrite successful")

else:
	print("Please find the output below:\n")
	print(dictionary)
