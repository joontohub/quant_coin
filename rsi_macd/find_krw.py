import requests




def find_krw_market():
    word_count = 0
    word = []
    word_2 = []
    krw_list  = []
    word_2_str =""
    url = "https://api.upbit.com/v1/market/all"

    querystring = {"isDetails":"false"}

    response = requests.request("GET", url, params=querystring)

    coin_list = response.text
    coin_list = coin_list[1:]
    coin_list = coin_list[:-1]


    for a in coin_list:
        
        if a != "}":
            word.append(a)
        else:
            word.append(a)
            word_str = ''.join(word)
            if word_count == 0:
                word_str = word_str[1:]
            else:
                word_str = word_str[2:]
            word_str = word_str[:-1]
            if 'KRW-' in word_str:
                count = 0
                for a in word_str:
                    if a == '"':
                        word_2.append(a)
                        count += 1
                        if count == 4:
                            word_2_str= ''.join(word_2)
                            break
                    else:
                        word_2.append(a)
                if "{" in word_2_str:
                    word_2_str.replace("{","")
                # print(word_2_str , "   this is 2 ")
                
                krw_list.append(word_2_str)
                
            word = []
            word_2 = []
            word_str = ""
            word_2_str = ""
        word_count += 1
        

    return krw_list

