#rules.py
Rules = [{"pattern":r"\brm\s+-rf\s+/$","category":"destructive","severity":"high","reason":"Recusively deletes everything from the root directory. Irreversible."},
         {"pattern":r"curl.*\|\s*bash","category":"destructive","severity":"high","reason":"Downloads and executes code from the internet. High risk."},
         {"pattern":r"chmod\s+777\s*","category":"destructive","severity":"critical","reason":"Grants full permissions to all users."},
         {"pattern":r"sudo\s+su","category":"destructive","severity":"medium","reason":"Executes commands with root privileges."},
         {"pattern":r"\b(nc|netcat|ncat)\b(?=.*\b-[a-zA-Z]*[lpV][a-zA-Z]*\b)(?=.*\b\d{2,5}\b)","category":"destructive","severity":"high","reason":"Listens for incoming connections on a specified port."},
         {"pattern":r"bash -i .* /dev/tcp/.*","category":"destructive","severity":"high","reason":"Establishes a reverse shell connection."},
         {"pattern":r"sh -i .* /dev/tcp/.*","category":"destructive","severity":"high","reason":"Establishes a reverse shell connection."},
         {"pattern":r"base64\s*-d\s*\|\s*bash","category":"destructive","severity":"high","reason":"Decodes and executes base64 encoded code."}]
