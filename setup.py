"""
Setup script that configures hash salts and downloads necessary packages
"""

import json
import subprocess
import time

print "Welcome to BasicBlog Setup!"

salt_1 = raw_input("First, type a random and arbitrary string of characters to act as a hashing"
                   " salt: ")

salt_2 = raw_input("Now, choose another random and arbitrary string to act as a second salt: ")

# load the two salts into a dict, serialize with json and store in a file
salts = dict(passwords=salt_1, cookies=salt_2)

salts = json.dumps(salts)
salt_file = open('salts.data', 'w')
salt_file.write(salts)
salt_file.close()

# now pip install the necessary packages:
print "Thanks! Now we'll just install the necessary packages and have your environment ready" \
      "in no time!"

subprocess.call("pip install -r requirements.txt", shell=True)
