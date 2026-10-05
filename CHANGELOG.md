ToDo:
          - Need to encrypt the talking over a network modularly
          - Need to check if person is online when listing contacts

Changelog:
	9/30/26 - Implemented simple user registration and pushed to github repository online
	10/2/26 - Created the Skeleton for the commands
	        - Implemented storing salt and kdf key derivation from password
					- Implemented secure contact adding and storing
					- Changed from json to bin storage and total encryption
	10/4/26 - Implemented talking from one application to another
					- Transmits and sends informational data about person at IP
					- Implemented ability to add friends and list contacts
