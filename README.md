#The final project for Intro to Computer Security

This is a secure drop application that encrypts from end to end following proper cryptography protocols to keeps information secure
Programmed in python 3.14


###Group Members:
	Alexander Roy


###Program Milestones:
  1: User Registration
  2: User Login
  3: Adding Contacts
  4: Listing Contacts
  5: Secure File Transfer

#Program Requirements:
  ##User Registration (20 points)
    While building this module, keep the following in mind:

    A database is not required. Plain files, YAML, or JSON are enough.
    Write the module without any security first. Once you know it works, add protection against ordinary password cracking.
    Write it so you can reuse it. The password protection comes back in the User Login milestone.
    Use existing libraries. Python's crypt module handles salted password hashes.
    Generate and store whatever you will need later for mutual authentication. You may assume a certificate authority (CA) is present and trusted on every client, which makes digital certificates easier to use.


  ##Milestone 2: User Login (10 points)
    This milestone should go quickly. The points to consider are:

    Reuse your code, since much of this resembles the User Registration milestone.
    Think about what the login credentials give you that later milestones can use. Hold that in memory without weakening password security, and clear it when the program exits.


  ##Milestone 3: Adding Contacts (10 points)
    This module is simple and should not take long. Two things to think about:
    
    A database is unnecessary. Plain files, YAML, or JSON are enough, and you can assume each user has only a few contacts.
    Use what Milestone 2 produced to keep the contact list confidential and intact, so that nobody can read or tamper with it.
    Milestone 4: Listing Contacts (20 points)
    This is the hard one, and it needs careful design. It is also the first point where your program talks over a network, which widens what an attacker can reach. When working on this module, keep the following in mind:

    Display a contact only when three conditions hold: the user has added the contact, the contact has added the user back, and the contact is online on the same network.
    Build it without security first, then add security. Use TCP or UDP for communication, and Python's socket module for the transport layer.
    Write reusable cryptographic code. Python's pycryptodome and cryptography modules cover most of what you need, and you will want the same functions again in the Secure File Transfer milestone.
    Encrypt who is talking to whom, so that packet sniffing reveals nothing. A leaked contact list leads to spam and targeted attacks.
    Guard against impersonation by building a protocol for mutual authentication between the two sides.
    Consider exchanging a protected secret between the two sides, so that later steps do not have to authenticate again. Keep that secret confidential.


  ##Milestone 5: Secure File Transfer (20 points)
    How hard this milestone is depends on how well the earlier ones went. The points to consider are:
    
    Send large files efficiently, and keep them confidential and intact. Check that the file received matches the file sent before you report a successful transfer.
    Stop replay attacks with sequence numbers, seeded randomly on each client.
