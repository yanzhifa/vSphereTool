#!python
#
# This is a simple json parser
# Kind of reinvented the wheel
#
# Rahul Ghose
# 08-April-2016 2:34 PM IST
#

DEBUG = False

def is_whitespace(c):
	return (c == " " or c == "\t" or c == "\n")

def get_tokens(s, delim = ","):
	string_started = False
	dict_count = 0
	arr_count = 0

	token_arr = []
	current_token_string = ""

	for character in s:
		if character == '\'' or character == '"':
			if string_started:
				string_started=False
			else:
				string_started=True
		if character == '{':
			dict_count += 1
		if character == '}':
			dict_count -= 1
		if character == '[':
			arr_count += 1
		if character == ']':
			arr_count -= 1
		if delim == character and arr_count == 0 and dict_count == 0 and not string_started:
			token_arr.append(current_token_string)
			current_token_string = ""
			continue
		current_token_string += character
	
	if len(current_token_string) > 0:
		token_arr.append(current_token_string)
	
	return token_arr

# Assume whitespaces have been truncated on the top level
# Returns the number of expected objects in the json string
def count_objects(s, delim = ","):
	if len(s) == 0:
		return 0
	string_started = False
	counted_objects = 0
	for character in s:
		if character == '\'' or character == '"':
			if string_started:
				string_started=False
			else:
				string_started=True
		if character == delim and not string_started:
			counted_objects += 1
	return (counted_objects+1)

# Removes whitespaces from non-string items
# which are not nested.
def truncate_whitespaces(s):
	string_started = False
	return_string = ""
	for character in s:
		if character == '\'' or character == '"':
			if string_started:
				string_started=False
			else:
				string_started=True
		if is_whitespace(character) and not string_started:
			continue
		return_string += character
	return return_string

#
# Check for valid json key
#
# a. They can be strings
# b. they can be numeric aka decimal or non-decimal numbers
#
def is_valid_key(s):
	l = len(s)
	if s[0] == "'" and s[l-1] == "'":
		return True
	if s[0] == "\"" and s[l-1] == "\"":
		return True
	if s.replace('.','',1).isdigit():
		return True
	return False

def array_from_string(s):
	if DEBUG:
		print "Called array_from_string: " + s
	s = truncate_whitespaces(s)
	length = len(s)
	if s[0] == '[' and s[length-1] != ']':
		raise Exception("[Parse error] Unexpected end of array string: " + s)
	return_object = []
	inner_string = s[1:length-1]
	objects = count_objects(inner_string)
	if DEBUG:
		print "Tokens for " + inner_string
	for token in get_tokens(inner_string):
		if DEBUG:
			print "Token:" + token
		return_object.append(get_object_from_string(token))
	return return_object

# Gets a dict object aka {} from the json
def dict_from_string(s):
	if DEBUG:
		print "Called dict_from_string: " + s
	s = truncate_whitespaces(s)
	length = len(s)
	if s[0] == '{' and s[length-1] != '}':
		raise Exception("[Parse error] Unexpected end of dict string: " + s)
	return_object = {}
	inner_string = s[1:length-1]
	if DEBUG:
		print "Tokens for " + inner_string
	for token in get_tokens(inner_string):
		if DEBUG:
			print "Token: "+ token
		try:
			key, value = get_tokens( token, ":")
		except Exception, e:
			print e
			raise Exception("[Parse error] Exception in parsing: " + token )
		if not is_valid_key(key):
			raise Exception("[Parse error] key is not a string: " + key)
		return_object[ key ] = get_object_from_string(value)
	return return_object

def get_object_from_string(s):
	if DEBUG:
		print "Called get_object_from_string: " + s
	s = truncate_whitespaces(s)
	if s[0] == '[':
		return array_from_string(s)
	if s[0] == '{':
		return dict_from_string(s)
	if is_valid_key(s):
		return eval(s)
	raise Exception("[Parse error] Invalid string: ", s)

def main():
	string = raw_input()
	print get_object_from_string(s)

def test():
	s1 = "[   {    } , {  }  ]"
	s2 = "[   {  \"test \": 1  } , {  }  ]"
	s3 = "[   { 'hmm': ['this is a long string', '  again', 'goo']   } , {  }  ]"
	s4 = '[{"state": {"cities": ["Mumbai", "Pune", "Nagpur", "Bhusaval", "Jalgaon"], "name": "Maharashtra"}}, {"state": {"cities": ["Bangalore", "Hubli"], "name": "Karnataka"}}, {"state": {"states": ["Raipur", "Durg"], "name": "Chhattisgarh"}}]'
	
	print get_object_from_string(s1)
	print get_object_from_string(s2)
	print get_object_from_string(s3)
	print get_object_from_string(s4)

#main()
test()