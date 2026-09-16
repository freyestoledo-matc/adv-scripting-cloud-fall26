import boto3
sts = boto3.client('sts')

hFile = open("credential-check.txt", "w")
result = sts.get_caller_identity()

hFile.write("Account: " + result['Account'] + "\n")
hFile.write("User ID: " + result['UserId'] + "\n")

print(result)
hFile.close()
