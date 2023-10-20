import lex
while True:
    text = input('SPy > ')
    result, error = lex.run('<stdin>', text)

    if error: 
        print(error.as_string())
    else: 
        print(result)