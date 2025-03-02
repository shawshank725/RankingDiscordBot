# Ranking Discord Bot
This is a discord bot that can help you create role-based ranked system in your discord server. It is made using python and all the user data is stored in serverless database.

This project has 3 python files.
* main.py file containing the bot's main code.
* sql_queries.py file containing sql queries used to create table, insert and update data
* read_env.py file to read data from .env file.

How to use it for your server - 
* Go to discord developer portal and create a new bot application and grant it the admin permissions.
* Copy the bot token.
* .env file, by default contains a key word called "TOKEN" whereyou place your bot's token.
* Whatever key word is used in .env file, use that in the main.py file.
* The main.py file's on_message function contains if else statements adding roles based on their level.
* here in the file, people with level less than 10 are beginners. Your server can have different roles and level range

Features of this bot - 
* This bot can observe all the members level and rank
* It has other commands like /hello, /evaluate, /test etc.
* This bot has /rank command to get your or someone else's rank and /top3 command to get top 3 discord chatters.
