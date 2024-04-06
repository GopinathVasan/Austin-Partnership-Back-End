# import requests

# url = "https://www.fast2sms.com/dev/bulkV2"

# payload = {
#     "authorization": "Lz9ApKcGqcFQRtHk9luQFMSOA8munwdd1ux9JjFEv9VHXJquokooJFt33s86",
#     "variables_values": "5599",
#     "route": "otp",
#     "numbers": "9442848407"
# }

# # Lz9ApKcGqcFQRtHk9luQFMSOA8munwdd1ux9JjFEv9VHXJquokooJFt33s86

# headers = {
#     'cache-control': "no-cache"
# }

# response = requests.post(url, data=payload, headers=headers)

# print(response.text)


import requests

url = "https://www.fast2sms.com/dev/bulkV2"

querystring = {"authorization":"Lz9ApKcGqcFQRtHk9luQFMSOA8munwdd1ux9JjFEv9VHXJquokooJFt33s86","variables_values":"5599","route":"otp","numbers":"9442848407"}

headers = {
    'cache-control': "no-cache"
}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
